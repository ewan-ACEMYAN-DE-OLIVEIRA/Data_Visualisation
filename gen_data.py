"""Génère un jeu de données FICTIF d'images scrappées + présence dans des datasets d'entraînement IA."""
import csv, random, datetime

random.seed(7)
N = 1800

# (domaine, type de source, groupe, poids)
SOURCES = [
    # --- Web grand public ---
    ("flickr.com", "Photo sharing", "Web", 9),
    ("wikimedia.org", "Encyclopédie", "Web", 7),
    ("unsplash.com", "Banque d'images", "Web", 5),
    ("shutterstock.com", "Banque d'images", "Web", 4),
    ("pinterest.com", "Réseau social", "Web", 7),
    ("instagram.com", "Réseau social", "Web", 5),
    ("facebook.com", "Réseau social", "Web", 4),
    ("x.com", "Réseau social", "Web", 3),
    ("reddit.com", "Réseau social", "Web", 4),
    ("youtube.com", "Vidéo (miniatures)", "Web", 4),
    ("deviantart.com", "Art en ligne", "Web", 4),
    ("artstation.com", "Art en ligne", "Web", 3),
    ("500px.com", "Photo sharing", "Web", 3),
    ("lemonde.fr", "Presse", "Web", 2),
    ("blogspot.com", "Blog", "Web", 4),
    ("wordpress.com", "Blog", "Web", 4),
    ("etsy.com", "E-commerce", "Web", 3),
    # --- Caméras (domaines fictifs en .example) ---
    ("traficam-idf.example", "Caméra de trafic", "Caméras", 7),
    ("villecam-centre.example", "Caméra municipale", "Caméras", 5),
    ("parking-securite.example", "Caméra de surveillance", "Caméras", 5),
    ("magasin-cctv.example", "Caméra de surveillance", "Caméras", 5),
    ("gare-live.example", "Caméra de surveillance", "Caméras", 3),
    ("ipcam-open.example", "Caméra IP non protégée", "Caméras", 4),
    ("webcam-plages.example", "Webcam publique", "Caméras", 3),
    ("stationski-cam.example", "Webcam publique", "Caméras", 2),
    ("dashcam-share.example", "Dashcam", "Caméras", 4),
]
LICENSES = ["CC0", "CC-BY", "CC-BY-SA", "CC-BY-NC", "Tous droits réservés", "Inconnue"]
LIC_BY_DOMAIN = {
    "wikimedia.org": [.15, .4, .35, .02, .03, .05],
    "unsplash.com": [.6, .3, 0, 0, .05, .05],
    "flickr.com": [.05, .25, .15, .2, .3, .05],
    "shutterstock.com": [0, 0, 0, 0, .97, .03],
    "lemonde.fr": [0, 0, 0, 0, .98, .02],
    "etsy.com": [0, 0, 0, 0, .9, .1],
}
LIC_WEB = [.03, .10, .05, .07, .55, .20]
LIC_CAM = [0, .01, 0, 0, .35, .64]          # caméras : presque toujours inconnue / réservée

CAT_WEB = {"Portrait": .2, "Paysage": .17, "Art/Illustration": .2, "Produit": .12,
           "Architecture": .08, "Animaux": .09, "Nourriture": .08, "Document": .06}
CAM_CONTEXT = {  # contexte -> (faces, plaques)
    "Rue / trafic": (.35, .75), "Parking": (.25, .85), "Magasin / intérieur": (.8, 0.0),
    "Gare / transport": (.85, .05), "Plage / ville": (.5, .05), "Domicile / bureau": (.7, 0.0),
}
CTX_BY_SOURCE = {
    "Caméra de trafic": ["Rue / trafic"], "Caméra municipale": ["Rue / trafic", "Plage / ville", "Gare / transport"],
    "Caméra de surveillance": ["Parking", "Magasin / intérieur", "Gare / transport"],
    "Caméra IP non protégée": ["Domicile / bureau", "Magasin / intérieur", "Parking"],
    "Webcam publique": ["Plage / ville"], "Dashcam": ["Rue / trafic"],
}
DS_WEB = {"LAION-5B": .55, "LAION-400M": .30, "COYO-700M": .20, "DataComp-1B": .35, "Conceptual Captions": .10}
DS_CAM = {"UA-DETRAC": .0, "MOT17": .0, "VIRAT": .0}       # datasets de vidéosurveillance


def pick(d, w): return random.choices(list(d), w)[0]


rows = []
start = datetime.date(2018, 1, 1)
for i in range(1, N + 1):
    dom, stype, grp, _ = random.choices(SOURCES, [s[3] for s in SOURCES])[0]
    date = start + datetime.timedelta(days=random.randint(0, 365 * 8 + 300))
    cam = grp == "Caméras"
    if cam:
        ctx = random.choice(CTX_BY_SOURCE[stype])
        fp, pp = CAM_CONTEXT[ctx]
        faces, plates = random.random() < fp, random.random() < pp
        cat = ctx
        lic = random.choices(LICENSES, LIC_CAM)[0]
        w = random.choice([352, 640, 704, 1280, 1920])
        h = int(w * random.choice([.56, .75]))
        t = f"{random.randint(0,23):02d}{random.randint(0,59):02d}{random.randint(0,59):02d}"
        img = f"https://{dom}/snapshots/{date:%Y/%m/%d}/cam_{random.randint(1,400):04d}_{t}.jpg"
        size = int(w * h / 1000 * random.uniform(.08, .3))
    else:
        ctx = ""
        cat = pick(CAT_WEB, CAT_WEB.values())
        faces = cat == "Portrait" and random.random() < .9 or random.random() < .05
        plates = False
        lic = random.choices(LICENSES, LIC_BY_DOMAIN.get(dom, LIC_WEB))[0]
        w = random.choice([512, 640, 800, 1024, 1280, 1920, 2048, 3000, 4000])
        h = int(w * random.choice([.56, .67, .75, 1, 1.33, 1.5]))
        img = f"https://{'upload.' if dom == 'wikimedia.org' else 'i.'}{dom}/{cat.lower().replace('/', '-')}/img_{i:05d}.jpg"
        size = int(w * h / 1000 * random.uniform(.15, .5))

    ds = []
    if cam:
        probs = {"LAION-5B": .22, "LAION-400M": .10, "COYO-700M": .12, "DataComp-1B": .18}
        if stype in ("Caméra de trafic", "Dashcam", "Caméra municipale"): probs["UA-DETRAC"] = .30
        if ctx in ("Rue / trafic", "Gare / transport", "Plage / ville"): probs["MOT17"] = .18
        if ctx in ("Parking", "Rue / trafic"): probs["VIRAT"] = .14
        if stype == "Caméra IP non protégée": probs = {k: v * 1.8 for k, v in probs.items()}
    else:
        probs = dict(DS_WEB)
        for k in probs:
            p = probs[k]
            if lic in ("CC0", "CC-BY", "CC-BY-SA"): p *= 1.3
            if dom in ("pinterest.com", "blogspot.com", "wordpress.com", "flickr.com", "reddit.com"): p *= 1.4
            if dom in ("lemonde.fr", "shutterstock.com"): p *= .5
            if k == "DataComp-1B" and date.year < 2021: p *= .3
            if k == "LAION-5B" and date.year < 2020: p *= .5
            probs[k] = p
    for k, p in probs.items():
        if random.random() < min(p, .95): ds.append(k)

    rows.append({
        "id": i, "image_url": img, "page_url": f"https://www.{dom}/page/{random.randint(100000, 999999)}",
        "domain": dom, "source_type": stype, "source_group": grp, "category": cat,
        "width": w, "height": h, "file_size_kb": size, "license": lic,
        "date_published": date.isoformat(), "scraped_date": "2026-11-20",
        "found_in_datasets": "|".join(ds), "n_datasets": len(ds), "used_for_training": len(ds) > 0,
        "similarity_score": round(min(.45, max(.18, random.gauss(.30 if not cam else .26, .045))), 3),
    })

with open("images_ia_sample.csv", "w", newline="", encoding="utf-8") as f:
    wr = csv.DictWriter(f, fieldnames=rows[0].keys()); wr.writeheader(); wr.writerows(rows)
print(len(rows), "lignes ;", sum(r["used_for_training"] for r in rows), "retrouvées ;",
      sum(r["source_group"] == "Caméras" for r in rows), "issues de caméras")