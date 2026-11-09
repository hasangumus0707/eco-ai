"""
Wikimedia Commons'tan açık lisanslı ek eğitim görselleri indirir.

Amaç: Modelin en çok zorlandığı durumlar için takviye. Özellikle şeffaf cam şişe ve
kavanozlar (plastikle karıştırılıyordu), ayrıca ev ortamında çekilmiş şişe ve kutular.

Çalıştırma (backend klasöründeyken):
    python -m training.fetch_commons
    python -m training.fetch_commons --classes plastic   # yalnızca bir sınıfı güncelle

Önemli: ornek-gorseller/ altındaki 48 gerçek dünya TEST görseli (KAYNAKLAR.csv)
kesinlikle indirilmez. Aksi hâlde model test sorularını ezberler ve sonuç sahte çıkar.

İndirme sonrası görseller elle kontrol edilir. Alakasız olanlar
dataset/extra/commons/reddedilen.txt dosyasına yazılır ve script tekrar
çalıştırıldığında onlar atlanır.

Çıktı : dataset/extra/commons/{train,val}/<sınıf>/*.jpg + KAYNAKLAR.csv
"""

import csv
import json
import hashlib
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = PROJECT_ROOT / "dataset" / "extra" / "commons"
TEST_SOURCES = PROJECT_ROOT / "ornek-gorseller" / "KAYNAKLAR.csv"
REJECTED = OUT_DIR / "reddedilen.txt"
USER_AGENT = "eco-ai-student-project/1.0 (educational dataset builder)"
VAL_RATIO = 0.2
PER_QUERY = 25

QUERIES = {
    "glass": [
        "clear glass bottle", "empty glass bottle", "glass soda bottle", "glass milk bottle",
        "glass water bottle", "transparent glass bottle", "glass bottle on table",
        "glass jar empty", "jam jar", "glass bottles recycling", "glass bottle hand",
        "lemonade glass bottle", "glass bottle litter",
    ],
    "plastic": [
        "plastic bottle hand", "PET bottle table", "empty plastic water bottle",
        "plastic bottle litter",
        # 2. tur: şeffaf plastik şişeler (cam ile karıştırılıyordu)
        "clear plastic bottle", "plastic water bottle", "PET bottle", "mineral water bottle plastic",
        "soda bottle plastic", "crushed plastic bottle", "empty PET bottle", "plastic bottles",
        "drinking water bottle", "bottled water",
    ],
    "metal": ["crushed aluminium can", "drink can litter", "empty tin can"],
}
OK_LICENSE = re.compile(r"^(cc0|public domain|pd|cc by(-sa)? [0-9.]+)", re.I)


def split_for(fname: str) -> str:
    """
    Dosya adından sabit train/val ayrımı. Rastgele sayı kullanılmaz; böylece script
    yeniden çalıştırılsa ya da bazı görseller reddedilse bile aynı dosya hep aynı
    kümeye düşer ve bir görsel asla hem train'de hem val'de bulunmaz.
    """
    h = int(hashlib.md5(fname.encode("utf-8")).hexdigest(), 16) % 1000
    return "val" if h < VAL_RATIO * 1000 else "train"


def api(params: dict) -> dict:
    url = "https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode(params)
    for attempt in range(5):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.load(r)
        except urllib.error.HTTPError as exc:
            if exc.code != 429:
                raise
            time.sleep(30 * (attempt + 1))  # rate limit: bekle ve tekrar dene
    raise RuntimeError("Commons API sürekli 429 döndürdü")


def download(url: str) -> bytes:
    for attempt in range(5):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(req, timeout=60) as r:
                return r.read()
        except urllib.error.HTTPError as exc:
            if exc.code != 429:
                raise
            time.sleep(30 * (attempt + 1))
    raise RuntimeError("indirme sürekli 429 döndürdü")


def main() -> None:
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--classes", nargs="+", choices=list(QUERIES), default=list(QUERIES))
    args = ap.parse_args()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    excluded = set()
    if TEST_SOURCES.exists():
        for row in csv.DictReader(TEST_SOURCES.open(encoding="utf-8")):
            excluded.add("File:" + row["baslik"])
    rejected = set(REJECTED.read_text(encoding="utf-8").split("\n")) if REJECTED.exists() else set()
    print(f"{len(excluded)} test görseli ve {len(rejected) - (1 if '' in rejected else 0)} reddedilen görsel hariç tutuluyor.")

    rows, seen = [], set()
    for cls, queries in QUERIES.items():
        if cls not in args.classes:
            continue
        n = 0
        for q in queries:
            data = api({"action": "query", "format": "json", "generator": "search",
                        "gsrsearch": f"{q} filetype:bitmap", "gsrnamespace": 6, "gsrlimit": 50,
                        "prop": "imageinfo", "iiprop": "url|extmetadata|mime", "iiurlwidth": 960})
            time.sleep(1)
            pages = sorted(data.get("query", {}).get("pages", {}).values(), key=lambda p: p.get("index", 0))
            got = 0
            for p in pages:
                if got >= PER_QUERY:
                    break
                title = p["title"]
                if title in seen or title in excluded:
                    continue
                ii = (p.get("imageinfo") or [{}])[0]
                meta = ii.get("extmetadata", {})
                lic = meta.get("LicenseShortName", {}).get("value", "").strip()
                if ii.get("mime") not in ("image/jpeg", "image/png") or not OK_LICENSE.match(lic):
                    continue
                if not ii.get("thumburl"):
                    continue
                seen.add(title)
                # Dosya adı başlıktan türetilir; böylece tekrar çalıştırmada aynı ad oluşur
                slug = re.sub(r"[^a-z0-9]+", "_", title.lower().removeprefix("file:"))[:60].strip("_")
                fname = f"{cls}_{slug}.jpg"
                got += 1
                if fname in rejected:
                    continue
                split = split_for(fname)
                out = OUT_DIR / split / cls / fname
                for other in ("train", "val"):  # başka kümede kalmışsa taşı, tekrar indirme
                    old = OUT_DIR / other / cls / fname
                    if other != split and old.exists():
                        out.parent.mkdir(parents=True, exist_ok=True)
                        old.replace(out)
                if not out.exists():
                    try:
                        out.parent.mkdir(parents=True, exist_ok=True)
                        out.write_bytes(download(ii["thumburl"]))
                        time.sleep(0.5)
                    except Exception as exc:
                        print(f"  HATA {title}: {exc}")
                        continue
                artist = re.sub(r"<[^>]+>", "", meta.get("Artist", {}).get("value", "")).strip()
                rows.append([f"{split}/{cls}/{fname}", title, artist, lic, ii.get("descriptionurl", ""), q])
                n += 1
        print(f"{cls}: {n} görsel")

    # Bu çalıştırmada işlenmeyen sınıfların lisans kayıtlarını koru
    csv_path = OUT_DIR / "KAYNAKLAR.csv"
    if csv_path.exists():
        old = list(csv.reader(csv_path.open(encoding="utf-8")))[1:]
        rows = [r for r in old if r[0].split("/")[1] not in args.classes] + rows
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["dosya", "baslik", "yazar", "lisans", "kaynak_url", "arama"])
        w.writerows(rows)
    print(f"Toplam {len(rows)} görsel -> {OUT_DIR}")


if __name__ == "__main__":
    main()
