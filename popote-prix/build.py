"""Construit les fichiers de prix de La Popote (prix.json, statcan-qc.json) dans le dossier site/."""
import csv, io, json, os, re, sys, urllib.request, zipfile, datetime

HAMMER = "https://jacobfilipp.com/hammerdata/hammer-5-csv.zip"
STATCAN = "https://www150.statcan.gc.ca/n1/tbl/csv/18100245-eng.zip"
V = {"NoFrills": "N", "Metro": "M", "Sobeys": "S", "Walmart": "W"}
OUT = "site"
os.makedirs(OUT, exist_ok=True)

def download(url, path):
    if os.path.exists(path): return path
    req = urllib.request.Request(url, headers={"User-Agent": "LaPopote/1.0 (personal price builder)"})
    with urllib.request.urlopen(req, timeout=600) as r, open(path, "wb") as f:
        while chunk := r.read(1 << 20): f.write(chunk)
    return path

hz = zipfile.ZipFile(download(HAMMER, sys.argv[1] if len(sys.argv) > 1 else "hammer.zip"))
names = hz.namelist()
prod_name = next(n for n in names if n.endswith("product.csv"))
raw_name = next(n for n in names if n.endswith("raw.csv"))

prod = {}
with hz.open(prod_name) as f:
    for r in csv.DictReader(io.TextIOWrapper(f, encoding="utf-8")):
        if r["vendor"] in V: prod[r["id"]] = r

cutoff = (datetime.date.today() - datetime.timedelta(days=21)).strftime("%Y%m%d")
latest = {}
with hz.open(raw_name) as f:
    rd = csv.reader(io.TextIOWrapper(f, encoding="utf-8", errors="replace"))
    next(rd, None)
    for row in rd:
        if len(row) < 6 or row[0] < cutoff: continue
        t, cp, op, ppu, other, pid = row[:6]
        if pid in prod and (pid not in latest or t >= latest[pid][0]):
            latest[pid] = (t, cp, op, ppu, other)

items, seen, dates = [], set(), []
for pid, (t, cp, op, ppu, other) in latest.items():
    r = prod[pid]
    try: p = float(cp)
    except ValueError: continue
    if p <= 0 or "out of stock" in other.lower(): continue
    name = re.sub(r"\s+", " ", r["product_name"]).strip()
    k = (r["vendor"], name.lower(), r["units"])
    if k in seen: continue
    seen.add(k)
    try: o = float(op)
    except ValueError: o = 0
    rec = [V[r["vendor"]], name, r["units"].strip(), p, ppu.strip()]
    if o > p: rec.append(o)
    items.append(rec); dates.append(t)
if len(items) < 1000: sys.exit(f"Trop peu de prix récents ({len(items)}), fichier non mis à jour.")
dates.sort()
meta = {"source": "Project Hammer (jacobfilipp.com/hammer), prix en magasin, Toronto", "du": dates[0], "au": dates[-1],
        "genere": datetime.date.today().isoformat(),
        "magasins": {"N": "No Frills (≈ Maxi/Super C)", "M": "Metro", "S": "Sobeys (≈ IGA)", "W": "Walmart"},
        "champs": ["magasin", "nom", "format", "prix", "prix_unitaire", "prix_regulier_si_special"]}
json.dump({"meta": meta, "items": items}, open(f"{OUT}/prix.json", "w"), ensure_ascii=False, separators=(",", ":"))
print("prix:", len(items), dates[0], dates[-1])

sz = zipfile.ZipFile(download(STATCAN, "statcan.zip"))
with sz.open("18100245.csv") as f:
    rows = list(csv.DictReader(io.TextIOWrapper(f, encoding="utf-8-sig")))
months = sorted({r["REF_DATE"] for r in rows})[-3:]
qc = {}
for r in rows:
    if r["GEO"] == "Quebec" and r["REF_DATE"] in months and r["VALUE"]:
        qc.setdefault(r["Products"], {})[r["REF_DATE"]] = float(r["VALUE"])
json.dump({"meta": {"source": "Statistique Canada, tableau 18-10-0245-01, Québec", "mois": months}, "items": qc},
          open(f"{OUT}/statcan-qc.json", "w"), ensure_ascii=False, separators=(",", ":"))
import shutil
if os.path.exists("app.html"): shutil.copy("app.html", f"{OUT}/app.html")
open(f"{OUT}/index.html", "w").write(f"<meta charset=utf-8><p>Prix La Popote, générés le {meta['genere']} ({len(items)} produits).</p>")
print("statcan:", len(qc), months)
