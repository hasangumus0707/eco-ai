"""
Model değerlendirme scripti.

Çalıştırma (backend klasöründeyken):
    python -m training.evaluate --arch mobilenet_v3_large
    python -m training.evaluate --arch resnet18
    python -m training.evaluate --arch mobilenet_v3_large --deploy   # uygulamada kullanılacak modeli seç

Yaptıkları:
  1. Güven eşiğini DOĞRULAMA kümesinden hesaplar (test kümesine bakmadan).
  2. TEST kümesinde ölçer: Accuracy, Precision, Recall, F1, Confusion Matrix.
  3. Bilinmeyen nesne kontrolünü ölçer: "other" görsellerinin kaçı yanlışlıkla atık sanıldı?
  4. Hız ve dosya boyutunu ölçer (Windows'taki CPU'lar için de).
  5. --deploy ile modeli weights/eco_ai_model.pth olarak kopyalar ve
     eşiği weights/model_config.json'a yazar. Backend bu iki dosyayı okur.

Çıktılar: reports/<arch>/metrics.json, confusion_matrix.png, classification_report.txt
"""

import argparse
import json
import shutil
import time
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import torch
from sklearn.metrics import (accuracy_score, classification_report, confusion_matrix,
                             precision_recall_fscore_support)

from app.models.classifier import CLASS_NAMES, SUPPORTED_ARCHS, load_checkpoint
from app.utils.decision import OTHER_CLASS, decide
from app.utils.device import get_device
from training.dataset import make_loader

BACKEND_DIR = Path(__file__).resolve().parents[1]
WEIGHTS_DIR = BACKEND_DIR / "weights"
REPORTS_DIR = BACKEND_DIR / "reports"
DEPLOY_WEIGHTS = WEIGHTS_DIR / "eco_ai_model.pth"
DEPLOY_CONFIG = WEIGHTS_DIR / "model_config.json"

# Doğru sınıflandırılan atık görsellerinin %95'i eşiği geçsin -> eşik = 5. yüzdelik
THRESHOLD_KEEP_RATIO = 0.95
CLASS_NAMES_TR = {"glass": "Cam", "metal": "Metal", "other": "Diğer", "paper": "Kâğıt", "plastic": "Plastik"}


@torch.no_grad()
def predict_all(model, loader, device) -> tuple[np.ndarray, np.ndarray]:
    """Bütün kümeyi modelden geçirir. Dönüş: (olasılıklar [N,5], gerçek etiketler [N])"""
    all_probs, all_labels = [], []
    for images, labels in loader:
        logits = model(images.to(device))
        all_probs.append(torch.softmax(logits, dim=1).cpu().numpy())  # softmax: skorları olasılığa çevirir
        all_labels.append(labels.numpy())
    return np.concatenate(all_probs), np.concatenate(all_labels)


def calibrate_threshold(probs: np.ndarray, labels: np.ndarray) -> float:
    """
    Güven eşiğini doğrulama verisinden seçer.
    Gerçekten atık olan VE doğru tahmin edilen görsellerin güven skorlarına bakar;
    bunların %95'inin geçeceği en yüksek eşiği seçer.
    """
    other_idx = CLASS_NAMES.index(OTHER_CLASS)
    preds = probs.argmax(1)
    mask = (labels != other_idx) & (preds == labels)
    confidences = probs[mask].max(1)
    threshold = float(np.quantile(confidences, 1 - THRESHOLD_KEEP_RATIO))
    return round(min(max(threshold, 0.5), 0.95), 3)  # makul aralıkta tut


def open_set_metrics(probs: np.ndarray, labels: np.ndarray, threshold: float) -> dict:
    """Karar kuralını (decide) test verisine uygulayıp sonuçlarını ölçer."""
    other_idx = CLASS_NAMES.index(OTHER_CLASS)
    decisions = [decide(dict(zip(CLASS_NAMES, map(float, p))), threshold) for p in probs]
    true_names = [CLASS_NAMES[i] for i in labels]

    recyclable = [(d, t) for d, t in zip(decisions, true_names) if t != OTHER_CLASS]
    accepted = [(d, t) for d, t in recyclable if d.is_valid]
    others = [d for d, t in zip(decisions, true_names) if t == OTHER_CLASS]
    others_wrongly_accepted = [d for d in others if d.is_valid]

    return {
        "threshold": threshold,
        # Gerçek atıkların yüzde kaçına kesin sonuç verdik?
        "recyclable_coverage": len(accepted) / len(recyclable),
        # Kesin sonuç verdiklerimizin yüzde kaçı doğruydu?
        "recyclable_accuracy_when_accepted": sum(d.predicted_class == t for d, t in accepted) / max(len(accepted), 1),
        # Atık OLMAYAN görsellerin yüzde kaçını yanlışlıkla atık sandık? (düşük = iyi)
        "other_false_accept_rate": len(others_wrongly_accepted) / len(others),
        "n_recyclable": len(recyclable),
        "n_other": len(others),
        "n_other_test_images": int((labels == other_idx).sum()),
    }


def measure_speed(model, device, n: int = 30) -> float:
    """Tek bir görsel için ortalama tahmin süresi (ms)."""
    x = torch.randn(1, 3, 224, 224, device=device)
    with torch.no_grad():
        for _ in range(5):  # ısınma turları
            model(x)
        if device.type == "mps":
            torch.mps.synchronize()
        t0 = time.perf_counter()
        for _ in range(n):
            model(x)
        if device.type == "mps":
            torch.mps.synchronize()
    return (time.perf_counter() - t0) / n * 1000


def plot_confusion(cm: np.ndarray, out_path: Path, arch: str, acc: float) -> None:
    """Confusion matrix: satır = gerçek sınıf, sütun = modelin tahmini."""
    labels_tr = [CLASS_NAMES_TR[c] for c in CLASS_NAMES]
    cm_norm = cm / cm.sum(axis=1, keepdims=True)
    fig, ax = plt.subplots(figsize=(7, 6))
    im = ax.imshow(cm_norm, cmap="Greens", vmin=0, vmax=1)
    ax.set_xticks(range(len(CLASS_NAMES)), labels_tr)
    ax.set_yticks(range(len(CLASS_NAMES)), labels_tr)
    ax.set_xlabel("Modelin tahmini")
    ax.set_ylabel("Gerçek sınıf")
    for i in range(len(CLASS_NAMES)):
        for j in range(len(CLASS_NAMES)):
            color = "white" if cm_norm[i, j] > 0.6 else "black"
            ax.text(j, i, f"{cm[i, j]}\n{cm_norm[i, j]*100:.1f}%", ha="center", va="center", color=color, fontsize=9)
    fig.colorbar(im, ax=ax, fraction=0.046)
    ax.set_title(f"{arch} – Test Confusion Matrix (accuracy {acc*100:.2f}%)")
    fig.tight_layout()
    fig.savefig(out_path, dpi=120)
    plt.close(fig)


def main() -> None:
    p = argparse.ArgumentParser(description="ECO AI model değerlendirme")
    p.add_argument("--arch", choices=SUPPORTED_ARCHS, required=True)
    p.add_argument("--name", default=None, help="weights/<name>.pth (varsayılan: mimari adı)")
    p.add_argument("--extra", action="store_true",
                   help="eşiği Kaggle + gerçek ortam (TACO/Commons) doğrulama verisiyle hesapla")
    p.add_argument("--deploy", action="store_true", help="bu modeli uygulamada kullanılacak model yap")
    p.add_argument("--workers", type=int, default=4)
    args = p.parse_args()
    args.name = args.name or args.arch

    device = get_device()
    weights_path = WEIGHTS_DIR / f"{args.name}.pth"
    if not weights_path.exists():
        raise FileNotFoundError(f"{weights_path} yok. Önce eğit: python -m training.train --arch {args.arch}")
    model, ckpt = load_checkpoint(str(weights_path), device)
    print(f"Model: {args.name} [{args.arch}] (epoch {ckpt['epoch']}) | Donanım: {device}")

    # 1) Eşik: yalnızca doğrulama verisi
    val_loader = make_loader("val", 64, args.workers, use_extra=args.extra)
    val_probs, val_labels = predict_all(model, val_loader, device)
    threshold = calibrate_threshold(val_probs, val_labels)
    print(f"Doğrulama verisinden hesaplanan güven eşiği: {threshold}")

    # 2) Test
    test_probs, test_labels = predict_all(model, make_loader("test", 64, args.workers), device)
    preds = test_probs.argmax(1)
    acc = accuracy_score(test_labels, preds)
    prec, rec, f1, _ = precision_recall_fscore_support(test_labels, preds, average="macro", zero_division=0)
    per_class = precision_recall_fscore_support(test_labels, preds, labels=range(len(CLASS_NAMES)), zero_division=0)
    report = classification_report(test_labels, preds, target_names=CLASS_NAMES, digits=4, zero_division=0)
    cm = confusion_matrix(test_labels, preds)

    open_set = open_set_metrics(test_probs, test_labels, threshold)

    # Gerçek ortam doğrulama görselleri (TACO/Commons val) üzerinde ayrı ölçüm.
    # Bu görseller eğitimde hiç kullanılmadı; modelin "laboratuvar dışı" başarısını gösterir.
    real_val = None
    if args.extra:
        from torch.utils.data import DataLoader
        from training.dataset import CombinedDataset
        extra_ds = CombinedDataset(val_loader.dataset.datasets[1:])
        rv_probs, rv_labels = predict_all(model, DataLoader(extra_ds, batch_size=64, num_workers=args.workers), device)
        real_val = {
            "images": int(len(rv_labels)),
            "accuracy": float(accuracy_score(rv_labels, rv_probs.argmax(1))),
            "open_set": open_set_metrics(rv_probs, rv_labels, threshold),
        }

    # 3) Hız ve boyut
    ms_device = measure_speed(model, device)
    model_cpu, _ = load_checkpoint(str(weights_path), torch.device("cpu"))
    ms_cpu = measure_speed(model_cpu, torch.device("cpu"))
    size_mb = weights_path.stat().st_size / 1e6
    n_params = sum(p.numel() for p in model.parameters())

    metrics = {
        "arch": args.arch,
        "name": args.name,
        "threshold_calibrated_on": "kaggle+extra val" if args.extra else "kaggle val",
        "best_epoch": ckpt["epoch"],
        "test_images": int(len(test_labels)),
        "accuracy": acc,
        "macro_precision": prec,
        "macro_recall": rec,
        "macro_f1": f1,
        "per_class": {
            c: {"precision": float(per_class[0][i]), "recall": float(per_class[1][i]),
                "f1": float(per_class[2][i]), "support": int(per_class[3][i])}
            for i, c in enumerate(CLASS_NAMES)
        },
        "confusion_matrix": cm.tolist(),
        "open_set": open_set,
        "real_world_val": real_val,
        "inference_ms_per_image": {str(device): round(ms_device, 2), "cpu": round(ms_cpu, 2)},
        "model_size_mb": round(size_mb, 1),
        "parameters_million": round(n_params / 1e6, 2),
    }

    out_dir = REPORTS_DIR / args.name
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "metrics.json").write_text(json.dumps(metrics, indent=2, ensure_ascii=False), encoding="utf-8")
    (out_dir / "classification_report.txt").write_text(report, encoding="utf-8")
    plot_confusion(cm, out_dir / "confusion_matrix.png", args.arch, acc)

    print("\n" + report)
    print(f"Accuracy        : {acc*100:.2f}%")
    print(f"Macro Precision : {prec*100:.2f}%  | Macro Recall: {rec*100:.2f}%  | Macro F1: {f1*100:.2f}%")
    print("\nBilinmeyen nesne kontrolü (eşik = {:.3f}):".format(threshold))
    print(f"  Gerçek atıklara kesin sonuç verme oranı : {open_set['recyclable_coverage']*100:.1f}%")
    print(f"  Kesin sonuçların doğruluğu               : {open_set['recyclable_accuracy_when_accepted']*100:.1f}%")
    print(f"  'Diğer' görsellerini atık sanma oranı    : {open_set['other_false_accept_rate']*100:.1f}%  (düşük = iyi)")
    print(f"\nHız: {ms_device:.1f} ms/görsel ({device}), {ms_cpu:.1f} ms/görsel (CPU) | "
          f"Boyut: {size_mb:.1f} MB | Parametre: {n_params/1e6:.2f}M")
    if real_val:
        print(f"\nGerçek ortam doğrulama ({real_val['images']} görsel): accuracy {real_val['accuracy']*100:.1f}% | "
              f"kesin sonuç oranı {real_val['open_set']['recyclable_coverage']*100:.1f}% | "
              f"kesin sonuç doğruluğu {real_val['open_set']['recyclable_accuracy_when_accepted']*100:.1f}% | "
              f"'diğer'i atık sanma {real_val['open_set']['other_false_accept_rate']*100:.1f}%")
    print(f"Raporlar: {out_dir}")

    if args.deploy:
        shutil.copy2(weights_path, DEPLOY_WEIGHTS)
        DEPLOY_CONFIG.write_text(json.dumps({
            "model_file": DEPLOY_WEIGHTS.name,
            "arch": args.arch,
            "class_names": CLASS_NAMES,
            "confidence_threshold": threshold,
            "test_accuracy": round(acc, 4),
            "test_macro_f1": round(f1, 4),
        }, indent=2), encoding="utf-8")
        print(f"\n🚀 Uygulama modeli olarak ayarlandı: {DEPLOY_WEIGHTS.name} + {DEPLOY_CONFIG.name}")


if __name__ == "__main__":
    main()
