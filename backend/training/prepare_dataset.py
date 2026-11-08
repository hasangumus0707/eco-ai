"""
Veri seti hazırlama scripti.

Kaggle'daki 12 sınıflı "Garbage Classification" veri setini bizim
5 sınıfımıza (4 atık sınıfı + "other") dönüştürür ve
train / val / test olarak böler.

Çalıştırma (backend klasöründeyken):
    python -m training.prepare_dataset

Girdi : dataset/raw/garbage_classification/<12 orijinal sınıf>/
Çıktı : dataset/processed/{train,val,test}/<5 sınıf>/
        dataset/stats.json  (sınıf sayıları, sunum ve README için)

Yapılan işlemler:
  1. Sınıf eşleştirme   : 12 orijinal klasör -> 5 hedef sınıf
  2. Kopya temizleme    : Birebir aynı görseller tek bir kez tutulur
                          (aksi hâlde aynı resim hem train hem test'e düşebilir)
  3. Çelişki temizleme  : İki farklı sınıfta etiketlenmiş görseller atılır
  4. "other" dengeleme  : Kıyafet gibi çok kalabalık sınıflar kırpılır
  5. Katmanlı bölme     : Her sınıf ayrı ayrı %70 / %15 / %15 bölünür
"""

import hashlib
import json
import random
import shutil
from collections import defaultdict
from pathlib import Path

# --- Yollar (bu dosyanın konumuna göre hesaplanır; her bilgisayarda çalışır) ---
PROJECT_ROOT = Path(__file__).resolve().parents[2]  # eco-ai/
RAW_DIR = PROJECT_ROOT / "dataset" / "raw" / "garbage_classification"
OUT_DIR = PROJECT_ROOT / "dataset" / "processed"
STATS_FILE = PROJECT_ROOT / "dataset" / "stats.json"

# --- 1. Sınıf eşleştirme tablosu ---
# Sol: Kaggle'daki klasör adı, Sağ: bizim sınıfımız
CLASS_MAPPING: dict[str, str] = {
    "plastic": "plastic",
    "metal": "metal",
    "paper": "paper",
    "cardboard": "paper",      # Karton, kâğıt atık kutusuna gider
    "brown-glass": "glass",
    "green-glass": "glass",
    "white-glass": "glass",
    # Aşağıdakiler 4 geri dönüşüm sınıfına girmez -> "other"
    # Model bunları görerek "bu bir plastik/kâğıt/metal/cam değil" demeyi öğrenir.
    "battery": "other",        # Pil tehlikeli atıktır, metal kutusuna atılmamalı
    "biological": "other",
    "clothes": "other",
    "shoes": "other",
    "trash": "other",
}

# --- 4. "other" için kaynak başına üst sınır ---
# clothes tek başına 5325 görsel; kırpılmazsa model çoğu şeye "other" der.
# 5 kaynak x 400 = en fazla 2000 görsel -> paper/glass sınıflarıyla benzer büyüklük.
OTHER_CAP_PER_SOURCE = 400

SPLIT_RATIOS = {"train": 0.70, "val": 0.15, "test": 0.15}
SEED = 42  # Aynı seed = her çalıştırmada aynı bölme (tekrarlanabilirlik)
IMAGE_EXTS = {".jpg", ".jpeg", ".png"}


def file_hash(path: Path) -> str:
    """Dosyanın içeriğinden parmak izi çıkarır. Aynı içerik = aynı hash."""
    return hashlib.md5(path.read_bytes()).hexdigest()


def collect_images() -> dict[str, list[tuple[Path, str]]]:
    """
    Tüm görselleri tarar, kopyaları ve çelişkili etiketleri temizler.
    Dönüş: {hedef_sınıf: [(dosya_yolu, kaynak_klasör), ...]}
    """
    if not RAW_DIR.exists():
        raise FileNotFoundError(
            f"Ham veri bulunamadı: {RAW_DIR}\n"
            "Kaggle'dan indirdiğin zip'i dataset/raw/ klasörüne açtığından emin ol."
        )

    missing = [c for c in CLASS_MAPPING if not (RAW_DIR / c).is_dir()]
    if missing:
        raise FileNotFoundError(f"Beklenen klasörler eksik: {missing}")

    # hash -> bu içeriğe sahip tüm dosyalar
    by_hash: dict[str, list[tuple[Path, str]]] = defaultdict(list)
    for source in sorted(CLASS_MAPPING):
        for path in sorted((RAW_DIR / source).iterdir()):
            if path.suffix.lower() in IMAGE_EXTS:
                by_hash[file_hash(path)].append((path, source))

    result: dict[str, list[tuple[Path, str]]] = defaultdict(list)
    n_duplicates = n_conflicts = 0
    for entries in by_hash.values():
        targets = {CLASS_MAPPING[src] for _, src in entries}
        if len(targets) > 1:
            # Aynı görsel farklı hedef sınıflarda -> hangisi doğru belli değil, at.
            n_conflicts += len(entries)
            continue
        n_duplicates += len(entries) - 1
        path, source = entries[0]  # kopyalardan yalnızca birini tut
        result[CLASS_MAPPING[source]].append((path, source))

    print(f"Atılan kopya görsel     : {n_duplicates}")
    print(f"Atılan çelişkili görsel : {n_conflicts}")
    return result


def cap_other(items: list[tuple[Path, str]], rng: random.Random) -> list[tuple[Path, str]]:
    """'other' sınıfında her kaynaktan en fazla OTHER_CAP_PER_SOURCE görsel tutar."""
    by_source: dict[str, list[tuple[Path, str]]] = defaultdict(list)
    for item in items:
        by_source[item[1]].append(item)
    capped: list[tuple[Path, str]] = []
    for source in sorted(by_source):
        group = by_source[source]
        rng.shuffle(group)
        capped.extend(group[:OTHER_CAP_PER_SOURCE])
    return capped


def split(items: list[tuple[Path, str]], rng: random.Random) -> dict[str, list[tuple[Path, str]]]:
    """Listeyi karıştırıp train/val/test olarak böler."""
    items = items[:]
    rng.shuffle(items)
    n = len(items)
    n_train = round(n * SPLIT_RATIOS["train"])
    n_val = round(n * SPLIT_RATIOS["val"])
    return {
        "train": items[:n_train],
        "val": items[n_train:n_train + n_val],
        "test": items[n_train + n_val:],
    }


def main() -> None:
    rng = random.Random(SEED)
    images = collect_images()
    images["other"] = cap_other(images["other"], rng)

    # Önceki çalıştırmadan kalan çıktıyı temizle (yalnızca processed/ klasörü)
    if OUT_DIR.exists():
        shutil.rmtree(OUT_DIR)

    stats: dict[str, dict[str, int]] = {}
    sources: dict[str, dict[str, int]] = {}
    for cls in sorted(images):
        parts = split(images[cls], rng)
        stats[cls] = {name: len(files) for name, files in parts.items()}
        stats[cls]["total"] = len(images[cls])
        sources[cls] = {}
        for _, src in images[cls]:
            sources[cls][src] = sources[cls].get(src, 0) + 1
        for part_name, files in parts.items():
            dest = OUT_DIR / part_name / cls
            dest.mkdir(parents=True, exist_ok=True)
            for path, src in files:
                # Kaynak klasör adını dosya adına ekle: hem çakışma olmaz
                # hem de sonradan görselin nereden geldiği anlaşılır.
                shutil.copy2(path, dest / f"{src}__{path.name}")

    STATS_FILE.write_text(
        json.dumps({"seed": SEED, "split_ratios": SPLIT_RATIOS,
                    "other_cap_per_source": OTHER_CAP_PER_SOURCE,
                    "classes": stats, "sources": sources}, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    # Özet tablo
    print(f"\n{'Sınıf':<10}{'Train':>8}{'Val':>8}{'Test':>8}{'Toplam':>9}")
    print("-" * 43)
    for cls, s in stats.items():
        print(f"{cls:<10}{s['train']:>8}{s['val']:>8}{s['test']:>8}{s['total']:>9}")
    total = {k: sum(s[k] for s in stats.values()) for k in ("train", "val", "test", "total")}
    print("-" * 43)
    print(f"{'TOPLAM':<10}{total['train']:>8}{total['val']:>8}{total['test']:>8}{total['total']:>9}")
    print(f"\n✅ Hazırlanan veri: {OUT_DIR}")
    print(f"✅ İstatistikler  : {STATS_FILE}")


if __name__ == "__main__":
    main()
