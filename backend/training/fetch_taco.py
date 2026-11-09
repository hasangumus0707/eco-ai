"""
TACO (Trash Annotations in Context) veri setinden gerçek ortam atık görselleri hazırlar.

Neden? Kaggle görselleri çoğunlukla sade arka planlı ürün fotoğrafları. TACO'daki
fotoğraflar ise sokakta, çimde, kumsalda, elde çekilmiş gerçek atıklar. Modeli bunlarla
ince ayar (fine-tuning) yaparak "gerçek hayattaki" başarısını artırmayı hedefliyoruz.

Kaynak : http://tacodataset.org  (Proença & Simões, 2020) · Lisans: CC BY 4.0
Çalıştırma (backend klasöründeyken):
    python -m training.fetch_taco

Ne yapar?
  1. dataset/raw/taco/annotations.json dosyasını okur (yoksa indirir).
  2. Bizim 4 sınıfımıza karşılık gelen nesneleri içeren fotoğrafları indirir.
  3. Her nesneyi çevresiyle birlikte (%30 pay bırakarak) kare olarak kırpar.
  4. Fotoğraf bazında %80 train / %20 val olarak böler. Aynı fotoğraftan çıkan
     kırpıntılar hep aynı kümede kalır, böylece val sonucu sahte yüksek çıkmaz.

Çıktı : dataset/extra/taco/{train,val}/{plastic,paper,metal,glass}/*.jpg
        dataset/extra/taco/stats.json
"""

import json
import random
import time
import urllib.request
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from io import BytesIO
from pathlib import Path

from PIL import Image, ImageOps

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = PROJECT_ROOT / "dataset" / "raw" / "taco"
OUT_DIR = PROJECT_ROOT / "dataset" / "extra" / "taco"
ANN_URL = "https://raw.githubusercontent.com/pedropro/TACO/master/data/annotations.json"
USER_AGENT = "eco-ai-student-project/1.0"

SEED = 42
VAL_RATIO = 0.2
MIN_SIDE = 64       # orijinal fotoğrafta bu pikselden küçük nesneler atlanır
CONTEXT = 0.30      # nesnenin etrafına bırakılan pay (her yönde)
OUT_SIZE = 384      # kırpıntılar bu boyuta küçültülür (eğitimde zaten 224'e iner)

# TACO kategori adı -> bizim sınıfımız
CATEGORY_MAP = {
    "Clear plastic bottle": "plastic",
    "Other plastic bottle": "plastic",
    "Disposable plastic cup": "plastic",
    "Other plastic cup": "plastic",
    "Disposable food container": "plastic",
    "Other plastic container": "plastic",
    "Spread tub": "plastic",
    "Tupperware": "plastic",
    "Glass bottle": "glass",
    "Glass jar": "glass",
    "Glass cup": "glass",
    "Drink can": "metal",
    "Food Can": "metal",
    "Corrugated carton": "paper",
    "Other carton": "paper",
    "Normal paper": "paper",
    "Paper bag": "paper",
    "Magazine paper": "paper",
    "Wrapping paper": "paper",
    "Pizza box": "paper",
    "Egg carton": "paper",
    "Toilet tube": "paper",
}


def http_get(url: str, retries: int = 3) -> bytes:
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(req, timeout=60) as r:
                return r.read()
        except Exception:
            if attempt == retries - 1:
                raise
            time.sleep(2 * (attempt + 1))
    raise RuntimeError("unreachable")


def square_crop_box(bbox, img_w, img_h):
    """COCO bbox (x, y, w, h) -> çevresiyle birlikte kare kırpma kutusu."""
    x, y, w, h = bbox
    side = max(w, h) * (1 + 2 * CONTEXT)
    cx, cy = x + w / 2, y + h / 2
    side = min(side, img_w, img_h)
    left = min(max(cx - side / 2, 0), img_w - side)
    top = min(max(cy - side / 2, 0), img_h - side)
    return int(left), int(top), int(left + side), int(top + side)


def iou(a, b) -> float:
    """İki kutunun (l, t, r, b) örtüşme oranı (intersection over union)."""
    iw = max(0, min(a[2], b[2]) - max(a[0], b[0]))
    ih = max(0, min(a[3], b[3]) - max(a[1], b[1]))
    inter = iw * ih
    union = (a[2] - a[0]) * (a[3] - a[1]) + (b[2] - b[0]) * (b[3] - b[1]) - inter
    return inter / union if union else 0.0


def process_image(img_info: dict, anns: list[dict], cat_names: dict, split: str) -> Counter:
    counts: Counter = Counter()
    raw_path = RAW_DIR / "images" / img_info["file_name"]
    if raw_path.exists():
        data = raw_path.read_bytes()
    else:
        data = http_get(img_info["flickr_url"])
        raw_path.parent.mkdir(parents=True, exist_ok=True)
        raw_path.write_bytes(data)
    image = ImageOps.exif_transpose(Image.open(BytesIO(data))).convert("RGB")
    # EXIF döndürmesi sonrası boyut etiket dosyasındakiyle uyuşmuyorsa ölçekle
    sx = image.width / img_info["width"]
    sy = image.height / img_info["height"]
    if abs(sx - sy) > 0.01:  # döndürülmüş ve etiketler eşleşmiyor: güvenli değil, atla
        return counts
    candidates = []
    for ann in anns:
        cls = CATEGORY_MAP[cat_names[ann["category_id"]]]
        x, y, w, h = (v * sx for v in ann["bbox"])
        if min(w, h) < MIN_SIDE:
            continue
        candidates.append((ann, cls, square_crop_box((x, y, w, h), image.width, image.height)))
    # Çelişkili etiket: neredeyse aynı kırpıntı iki farklı sınıfla etiketlenmişse ikisini de at
    conflicted = {
        a["id"] for a, ca, ba in candidates for b, cb, bb in candidates
        if ca != cb and iou(ba, bb) > 0.8
    }
    for ann, cls, box in candidates:
        if ann["id"] in conflicted:
            continue
        crop = image.crop(box).resize((OUT_SIZE, OUT_SIZE), Image.LANCZOS)
        # Dosya adında TACO kategorisi de var (ör. ..._clear_plastic_bottle.jpg); eğitimde
        # belirli alt türleri (şeffaf plastik şişe gibi) daha sık göstermek için kullanılır.
        cat_slug = cat_names[ann["category_id"]].lower().replace(" ", "_")
        out = OUT_DIR / split / cls / f"taco_{img_info['id']:04d}_{ann['id']:05d}_{cat_slug}.jpg"
        out.parent.mkdir(parents=True, exist_ok=True)
        crop.save(out, quality=92)
        counts[cls] += 1
    return counts


def overlaps(box, bboxes, margin: float = 0.1) -> bool:
    """box (l, t, r, b) herhangi bir etiketli nesneyle (biraz pay bırakarak) kesişiyor mu?"""
    l, t, r, b = box
    for x, y, w, h in bboxes:
        mx, my = w * margin, h * margin
        if l < x + w + mx and r > x - mx and t < y + h + my and b > y - my:
            return True
    return False


def make_background_crops(img_info: dict, all_bboxes: list, split: str, rng: random.Random) -> int:
    """
    Fotoğrafın hiçbir atık içermeyen bir bölgesinden (çim, asfalt, toprak...) kare parça keser
    ve "other" sınıfına koyar. Model böylece "zemin var ama üstünde atık yok -> diğer"
    ayrımını öğrenir. Bunu yapmazsak tüm gerçek ortam görselleri atık olacağı için model
    "karışık arka plan = atık" diye yanlış bir kısayol öğrenebilir.
    """
    raw_path = RAW_DIR / "images" / img_info["file_name"]
    if not raw_path.exists():
        return 0
    image = ImageOps.exif_transpose(Image.open(raw_path)).convert("RGB")
    sx, sy = image.width / img_info["width"], image.height / img_info["height"]
    if abs(sx - sy) > 0.01:
        return 0
    bboxes = [(x * sx, y * sy, w * sx, h * sy) for x, y, w, h in all_bboxes]
    short = min(image.width, image.height)
    for _ in range(40):  # uygun boş bölge bulmak için en fazla 40 deneme
        side = int(short * rng.uniform(0.2, 0.45))
        left = rng.randint(0, image.width - side)
        top = rng.randint(0, image.height - side)
        box = (left, top, left + side, top + side)
        if not overlaps(box, bboxes):
            crop = image.crop(box).resize((OUT_SIZE, OUT_SIZE), Image.LANCZOS)
            out = OUT_DIR / split / "other" / f"taco_bg_{img_info['id']:04d}.jpg"
            out.parent.mkdir(parents=True, exist_ok=True)
            crop.save(out, quality=92)
            return 1
    return 0


def main() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    ann_path = RAW_DIR / "annotations.json"
    if not ann_path.exists():
        print("annotations.json indiriliyor...")
        ann_path.write_bytes(http_get(ANN_URL))
    data = json.loads(ann_path.read_text(encoding="utf-8"))

    cat_names = {c["id"]: c["name"] for c in data["categories"]}
    images = {img["id"]: img for img in data["images"]}
    by_image: dict[int, list[dict]] = defaultdict(list)
    for ann in data["annotations"]:
        if cat_names[ann["category_id"]] in CATEGORY_MAP:
            by_image[ann["image_id"]].append(ann)

    image_ids = sorted(by_image)
    random.Random(SEED).shuffle(image_ids)
    n_val = int(len(image_ids) * VAL_RATIO)
    split_of = {iid: ("val" if i < n_val else "train") for i, iid in enumerate(image_ids)}
    print(f"{len(image_ids)} fotoğraf işlenecek ({n_val} val). İndiriliyor ve kırpılıyor...")

    totals: dict[str, Counter] = {"train": Counter(), "val": Counter()}
    failed = 0
    with ThreadPoolExecutor(max_workers=8) as pool:
        futures = {pool.submit(process_image, images[iid], by_image[iid], cat_names, split_of[iid]): iid
                   for iid in image_ids}
        for i, fut in enumerate(as_completed(futures), 1):
            try:
                totals[split_of[futures[fut]]] += fut.result()
            except Exception as exc:
                failed += 1
                print(f"  HATA (fotoğraf {futures[fut]}): {exc}")
            if i % 100 == 0:
                print(f"  {i}/{len(image_ids)}")

    # Atıksız arka plan parçaları ("other"). Her fotoğraftaki TÜM etiketler (sigara izmariti
    # dahil) hesaba katılır, böylece parçada küçük bir atık bile kalmaz.
    all_boxes: dict[int, list] = defaultdict(list)
    for ann in data["annotations"]:
        all_boxes[ann["image_id"]].append(ann["bbox"])
    rng = random.Random(SEED)
    print("Atıksız arka plan parçaları ('other') hazırlanıyor...")
    for iid in image_ids:
        totals[split_of[iid]]["other"] += make_background_crops(images[iid], all_boxes[iid], split_of[iid], rng)

    stats = {
        "source": "TACO (http://tacodataset.org), CC BY 4.0",
        "seed": SEED, "val_ratio": VAL_RATIO, "min_side": MIN_SIDE, "context": CONTEXT,
        "images_used": len(image_ids) - failed, "images_failed": failed,
        "crops": {s: dict(sorted(c.items())) for s, c in totals.items()},
    }
    (OUT_DIR / "stats.json").write_text(json.dumps(stats, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(stats, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
