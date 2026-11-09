"""
Gerçek dünya testi: kendi çektiğimiz fotoğraflarla modeli değerlendirir.

Çalıştırma (backend klasöründeyken):
    python -m training.evaluate_real
    python -m training.evaluate_real --folder ../baska/klasor
    python -m training.evaluate_real --model-file mobilenet_v3_large_v2.pth --threshold 0.7  # aday model

Girdi : ornek-gorseller/{plastic,paper,metal,glass,other}/*.jpg
        (ornek-gorseller/_internet/ altındaki aynı yapıdaki görseller de dahil edilir)
Çıktı : reports/real_world/results.json ve results.md

Kaggle test kümesiyle (%95) karşılaştırınca, modelin "laboratuvar dışında"
ne kadar başarılı olduğunu dürüstçe gösterir.

Backend ile AYNI kodu kullanır (ModelService + decide), yani sonuçlar
web arayüzünde göreceğinizle birebir aynıdır.
"""

import argparse
import json
from collections import defaultdict
from pathlib import Path

from app.services.model_service import ModelService
from app.utils.image_validation import ImageValidationError, validate_and_load_image

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_FOLDER = PROJECT_ROOT / "ornek-gorseller"
REPORT_DIR = Path(__file__).resolve().parents[1] / "reports" / "real_world"
CLASSES = ["plastic", "paper", "metal", "glass", "other"]
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp"}
TR = {"plastic": "Plastik", "paper": "Kâğıt", "metal": "Metal", "glass": "Cam", "other": "Diğer"}


def collect(folder: Path) -> list[tuple[Path, str]]:
    """(dosya, gerçek_sınıf) listesi. _internet alt klasörü de taranır."""
    items = []
    for base in (folder, folder / "_internet"):
        for cls in CLASSES:
            d = base / cls
            if d.is_dir():
                items += [(p, cls) for p in sorted(d.iterdir()) if p.suffix.lower() in IMAGE_EXTS]
    return items


def outcome(true_cls: str, predicted: str, is_valid: bool) -> str:
    """
    Her görselin sonucunu 4 gruptan birine koyar:
      correct   : doğru ve kesin sonuç (atık için doğru kategori / "other" için reddetme)
      rejected  : atıktı ama sistem "emin değilim / atık değil" dedi (zararsız hata)
      wrong     : yanlış kategoriyi KESİN sonuç olarak gösterdi (zararlı hata)
    """
    if true_cls == "other":
        return "correct" if not is_valid else "wrong"
    if not is_valid:
        return "rejected"
    return "correct" if predicted == true_cls else "wrong"


def main() -> None:
    p = argparse.ArgumentParser(description="Gerçek dünya fotoğraflarıyla test")
    p.add_argument("--folder", type=Path, default=DEFAULT_FOLDER)
    p.add_argument("--model-file", default=None, help="weights/ altındaki aday model (varsayılan: uygulama modeli)")
    p.add_argument("--threshold", type=float, default=None, help="aday modelin güven eşiği")
    args = p.parse_args()
    report_dir = REPORT_DIR / Path(args.model_file).stem if args.model_file else REPORT_DIR

    items = collect(args.folder)
    if not items:
        print(f"Hiç görsel bulunamadı: {args.folder}/<sınıf>/")
        print("Klasör yapısı için ornek-gorseller/README.md dosyasına bakın.")
        return

    service = ModelService(args.model_file, args.threshold)
    print(f"Model: {service.arch} | eşik: {service.threshold} | {len(items)} görsel\n")

    rows = []
    for path, true_cls in items:
        try:
            image = validate_and_load_image(path.read_bytes())
        except ImageValidationError as exc:
            print(f"  ATLANDI {path.name}: {exc}")
            continue
        probs, decision = service.predict(image)
        res = outcome(true_cls, decision.predicted_class, decision.is_valid)
        rows.append({
            "file": str(path.relative_to(args.folder)),
            "true": true_cls,
            "predicted": decision.predicted_class,
            "confidence": round(decision.confidence, 4),
            "is_valid": decision.is_valid,
            "reason": decision.reason,
            "outcome": res,
            "probabilities": probs,
        })
        mark = {"correct": "✅", "rejected": "⚠️ ", "wrong": "❌"}[res]
        shown = TR[decision.predicted_class] if decision.is_valid else f"({decision.reason}: {TR[decision.predicted_class]})"
        print(f"  {mark} {TR[true_cls]:<7} → {shown:<32} %{decision.confidence * 100:5.1f}  {path.name}")

    # Özet
    per_class: dict[str, dict[str, int]] = defaultdict(lambda: {"correct": 0, "rejected": 0, "wrong": 0})
    for r in rows:
        per_class[r["true"]][r["outcome"]] += 1
    total = {k: sum(v[k] for v in per_class.values()) for k in ("correct", "rejected", "wrong")}
    n = sum(total.values())
    waste = [r for r in rows if r["true"] != "other"]
    top1 = sum(r["predicted"] == r["true"] for r in waste) / len(waste) if waste else None

    lines = [
        "# Gerçek Dünya Testi Sonuçları",
        "",
        f"Model: `{service.arch}` · Güven eşiği: {service.threshold} · Görsel sayısı: {n}",
        "",
        "| Gerçek sınıf | Görsel | ✅ Doğru | ⚠️ Emin değil (zararsız) | ❌ Yanlış (zararlı) |",
        "|---|---:|---:|---:|---:|",
    ]
    for cls in CLASSES:
        if cls in per_class:
            c = per_class[cls]
            lines.append(f"| {TR[cls]} | {sum(c.values())} | {c['correct']} | {c['rejected']} | {c['wrong']} |")
    lines += [
        f"| **Toplam** | **{n}** | **{total['correct']}** | **{total['rejected']}** | **{total['wrong']}** |",
        "",
        f"- Doğru sonuç oranı: **%{total['correct'] / n * 100:.1f}**",
        f"- Zararlı hata oranı (yanlış kategoriyi kesin sonuç olarak gösterme): **%{total['wrong'] / n * 100:.1f}**",
    ]
    if top1 is not None:
        lines.append(f"- Atık görsellerinde eşik uygulanmadan en yüksek olasılığın doğru olma oranı: **%{top1 * 100:.1f}**")
    lines += ["", "> \"Diğer\" için doğru sonuç, sistemin kesin bir atık kategorisi göstermemesidir."]

    report_dir.mkdir(parents=True, exist_ok=True)
    (report_dir / "results.json").write_text(json.dumps(rows, indent=2, ensure_ascii=False), encoding="utf-8")
    (report_dir / "results.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n" + "\n".join(lines))
    print(f"\nRapor: {report_dir / 'results.md'}")


if __name__ == "__main__":
    main()
