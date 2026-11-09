"""
Model eğitim scripti (Transfer Learning).

Çalıştırma (backend klasöründeyken, sanal ortam aktifken):
    python -m training.train --arch mobilenet_v3_large
    python -m training.train --arch resnet18

    # Gerçek dünya ince ayarı: mevcut modelden başla, TACO/Commons ek verisini de kullan,
    # sonucu ayrı bir dosyaya kaydet (uygulamanın modeline dokunmaz)
    python -m training.train --extra --init weights/eco_ai_model.pth --name mobilenet_v3_large_v2 --epochs 10 --lr 3e-4

Çıktılar:
    weights/<name>.pth                -> en iyi model (doğrulama kaybına göre); name varsayılan = arch
    reports/<name>/history.json       -> her epoch'un loss/accuracy değerleri
    reports/<name>/training_curves.png -> eğitim grafikleri

OVERFITTING'E KARŞI ALINAN ÖNLEMLER:
    1. Data augmentation        (app/utils/transforms.py)
    2. Dropout                  (app/models/classifier.py)
    3. Weight decay (AdamW)     ağırlıkların aşırı büyümesini cezalandırır
    4. Farklı öğrenme hızları   önceden eğitilmiş gövde yavaş, yeni kafa hızlı öğrenir
    5. Early stopping           doğrulama kaybı iyileşmeyi bırakınca eğitim durur
    6. En iyi modeli kaydetme   son epoch değil, doğrulamada en iyi olan epoch saklanır
"""

import argparse
import json
import time
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # ekran açmadan dosyaya grafik çiz
import matplotlib.pyplot as plt
import torch
from torch import nn
from tqdm import tqdm

from app.models.classifier import CLASS_NAMES, SUPPORTED_ARCHS, build_model
from app.utils.device import get_device
from app.utils.transforms import IMAGENET_MEAN, IMAGENET_STD, IMG_SIZE
from training.dataset import compute_class_weights, make_loader

BACKEND_DIR = Path(__file__).resolve().parents[1]
WEIGHTS_DIR = BACKEND_DIR / "weights"
REPORTS_DIR = BACKEND_DIR / "reports"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="ECO AI model eğitimi")
    p.add_argument("--arch", choices=SUPPORTED_ARCHS, default="mobilenet_v3_large")
    p.add_argument("--epochs", type=int, default=15, help="en fazla epoch sayısı")
    p.add_argument("--batch-size", type=int, default=32)
    p.add_argument("--lr", type=float, default=1e-3, help="yeni sınıflandırma katmanının öğrenme hızı")
    p.add_argument("--patience", type=int, default=4, help="early stopping sabrı (epoch)")
    p.add_argument("--workers", type=int, default=4)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--extra", action="store_true",
                   help="dataset/extra altındaki gerçek ortam görsellerini (TACO, Commons) de kullan")
    p.add_argument("--init", type=Path, default=None,
                   help="ImageNet yerine bu .pth dosyasındaki modelden başla (ince ayar)")
    p.add_argument("--name", default=None, help="çıktı dosyalarının adı (varsayılan: mimari adı)")
    args = p.parse_args()
    args.name = args.name or args.arch
    return args


def head_parameters(model: nn.Module, arch: str) -> list[nn.Parameter]:
    """Yeni eklenen son katmanın parametreleri."""
    head = model.classifier[-1] if arch == "mobilenet_v3_large" else model.fc
    return list(head.parameters())


def run_epoch(model, loader, criterion, device, optimizer=None, desc=""):
    """
    Bir epoch boyunca veriyi modelden geçirir.
    optimizer verilirse EĞİTİM (ağırlıklar güncellenir), verilmezse DOĞRULAMA yapılır.
    Dönüş: (ortalama kayıp, doğruluk)
    """
    training = optimizer is not None
    model.train(training)  # train modunda dropout açık, eval modunda kapalı
    total_loss, correct, seen = 0.0, 0, 0

    with torch.set_grad_enabled(training):
        for images, labels in tqdm(loader, desc=desc, leave=False):
            images, labels = images.to(device), labels.to(device)
            outputs = model(images)            # 1) ileri geçiş: tahmin
            loss = criterion(outputs, labels)  # 2) hata ne kadar?
            if training:
                optimizer.zero_grad()
                loss.backward()                # 3) geri yayılım: hangi ağırlık ne kadar suçlu?
                optimizer.step()               # 4) ağırlıkları biraz düzelt
            total_loss += loss.item() * labels.size(0)
            correct += (outputs.argmax(dim=1) == labels).sum().item()
            seen += labels.size(0)

    return total_loss / seen, correct / seen


def plot_history(history: dict, out_path: Path, arch: str) -> None:
    """Loss ve accuracy eğrilerini çizer."""
    epochs = range(1, len(history["train_loss"]) + 1)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.5))

    ax1.plot(epochs, history["train_loss"], "o-", label="Eğitim")
    ax1.plot(epochs, history["val_loss"], "o-", label="Doğrulama")
    ax1.set_title("Kayıp (Loss)")
    ax1.set_xlabel("Epoch")
    ax1.legend()
    ax1.grid(alpha=0.3)

    ax2.plot(epochs, [a * 100 for a in history["train_acc"]], "o-", label="Eğitim")
    ax2.plot(epochs, [a * 100 for a in history["val_acc"]], "o-", label="Doğrulama")
    ax2.set_title("Doğruluk (Accuracy, %)")
    ax2.set_xlabel("Epoch")
    ax2.legend()
    ax2.grid(alpha=0.3)

    best = history["best_epoch"]
    for ax in (ax1, ax2):
        ax.axvline(best, color="gray", linestyle="--", alpha=0.6)
    fig.suptitle(f"{arch} – eğitim süreci (kesikli çizgi: kaydedilen en iyi epoch = {best})")
    fig.tight_layout()
    fig.savefig(out_path, dpi=120)
    plt.close(fig)


def main() -> None:
    args = parse_args()
    torch.manual_seed(args.seed)
    device = get_device()
    print(f"Donanım: {device} | Mimari: {args.arch}")

    train_loader = make_loader("train", args.batch_size, args.workers, use_extra=args.extra)
    val_loader = make_loader("val", args.batch_size, args.workers, use_extra=args.extra)
    print(f"Eğitim görseli: {len(train_loader.dataset)} | Doğrulama görseli: {len(val_loader.dataset)}")

    if args.init:
        # İnce ayar: zaten atıkları tanımayı öğrenmiş modelden devam et
        init_ckpt = torch.load(args.init, map_location="cpu", weights_only=True)
        if init_ckpt["arch"] != args.arch or init_ckpt["class_names"] != CLASS_NAMES:
            raise ValueError(f"{args.init} farklı bir mimari/sınıf listesine ait: {init_ckpt['arch']}")
        model = build_model(args.arch, pretrained=False)
        model.load_state_dict(init_ckpt["state_dict"])
        model.to(device)
        print(f"Başlangıç modeli: {args.init}")
    else:
        model = build_model(args.arch, pretrained=True).to(device)

    # Dengesiz sınıflar için ağırlıklı kayıp fonksiyonu
    class_weights = compute_class_weights(train_loader.dataset).to(device)
    print("Sınıf ağırlıkları:", {c: round(w, 2) for c, w in zip(CLASS_NAMES, class_weights.tolist())})
    criterion = nn.CrossEntropyLoss(weight=class_weights)

    # Farklı öğrenme hızları: gövde zaten iyi özellikler biliyor, onu bozmamak için 10 kat yavaş.
    head_params = head_parameters(model, args.arch)
    head_ids = {id(p) for p in head_params}
    body_params = [p for p in model.parameters() if id(p) not in head_ids]
    optimizer = torch.optim.AdamW(
        [{"params": body_params, "lr": args.lr / 10}, {"params": head_params, "lr": args.lr}],
        weight_decay=1e-4,
    )
    # Öğrenme hızını epoch'lar boyunca yumuşakça azalt (cosine annealing)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=args.epochs)

    WEIGHTS_DIR.mkdir(exist_ok=True)
    report_dir = REPORTS_DIR / args.name
    report_dir.mkdir(parents=True, exist_ok=True)
    weights_path = WEIGHTS_DIR / f"{args.name}.pth"

    history = {"train_loss": [], "train_acc": [], "val_loss": [], "val_acc": [], "epoch_seconds": []}
    best_val_loss = float("inf")
    epochs_without_improvement = 0
    start_all = time.time()

    for epoch in range(1, args.epochs + 1):
        t0 = time.time()
        train_loss, train_acc = run_epoch(model, train_loader, criterion, device, optimizer, f"Epoch {epoch} eğitim")
        val_loss, val_acc = run_epoch(model, val_loader, criterion, device, None, f"Epoch {epoch} doğrulama")
        scheduler.step()
        secs = time.time() - t0

        for key, val in zip(history, (train_loss, train_acc, val_loss, val_acc, secs)):
            history[key].append(val)

        improved = val_loss < best_val_loss
        marker = "  ⭐ en iyi, kaydedildi" if improved else ""
        print(f"Epoch {epoch:2d}/{args.epochs} | "
              f"train loss {train_loss:.4f} acc {train_acc*100:5.1f}% | "
              f"val loss {val_loss:.4f} acc {val_acc*100:5.1f}% | {secs:.0f}s{marker}")

        if improved:
            best_val_loss = val_loss
            epochs_without_improvement = 0
            history["best_epoch"] = epoch
            # Modeli ve onu yeniden kurmak için gereken her bilgiyi birlikte kaydet.
            torch.save({
                "arch": args.arch,
                "class_names": CLASS_NAMES,
                "state_dict": model.state_dict(),
                "img_size": IMG_SIZE,
                "mean": list(IMAGENET_MEAN),
                "std": list(IMAGENET_STD),
                "epoch": epoch,
                "val_loss": val_loss,
                "val_acc": val_acc,
                "use_extra": args.extra,
                "init_from": str(args.init) if args.init else "imagenet",
            }, weights_path)
        else:
            epochs_without_improvement += 1
            if epochs_without_improvement >= args.patience:
                print(f"⏹  Early stopping: {args.patience} epoch boyunca doğrulama kaybı iyileşmedi.")
                break

    history["total_minutes"] = (time.time() - start_all) / 60
    history["args"] = {k: (str(v) if isinstance(v, Path) else v) for k, v in vars(args).items()}
    (report_dir / "history.json").write_text(json.dumps(history, indent=2), encoding="utf-8")
    plot_history(history, report_dir / "training_curves.png", args.name)

    best = history["best_epoch"]
    print(f"\n✅ Eğitim bitti ({history['total_minutes']:.1f} dk). "
          f"En iyi epoch: {best} | val acc: {history['val_acc'][best-1]*100:.2f}%")
    print(f"   Model   : {weights_path}")
    print(f"   Grafik  : {report_dir / 'training_curves.png'}")


if __name__ == "__main__":
    main()
