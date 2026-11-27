import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

# ------------------------------------------------------------------
# Chargement des données
# ------------------------------------------------------------------
df = pd.read_csv("images_ia_sample.csv", parse_dates=["date_published"])
df["year"] = df["date_published"].dt.year
DATASETS = ["LAION-5B", "LAION-400M", "COYO-700M", "DataComp-1B",
            "Conceptual Captions", "UA-DETRAC", "MOT17", "VIRAT"]
for d in DATASETS:                       # une colonne booléenne par dataset
    df[d] = df["found_in_datasets"].fillna("").str.split("|").apply(lambda l: d in l)

SAVE_FIGURES = True                       # True : enregistre aussi chaque figure en PNG dans ./figures
if SAVE_FIGURES:
    import os
    os.makedirs("figures", exist_ok=True)
    _show, _n = plt.show, [0]
    def _save_then_show(*a, **k):
        _n[0] += 1
        plt.savefig(f"figures/figure_{_n[0]:02d}.png", dpi=150, bbox_inches="tight")
        _show(*a, **k)
        plt.close()                       # repart d'une figure vierge
    plt.show = _save_then_show

print(df.shape)
print(df.groupby("source_group")["used_for_training"].agg(["count", "mean"]))


# ------------------------------------------------------------------
# 1. Line chart : % d'images retrouvées dans un dataset, par année
# ------------------------------------------------------------------
rate = df.groupby(["year", "source_group"])["used_for_training"].mean().unstack() * 100

plt.plot(rate.index, rate["Web"], marker="o", label="Web grand public")
plt.plot(rate.index, rate["Caméras"], marker="o", label="Caméras")
plt.title("Line Chart - Images retrouvées dans un dataset")
plt.xlabel("Année de publication")
plt.ylabel("% d'images retrouvées")
plt.ylim(0, 100)
plt.legend()
plt.show()


# ------------------------------------------------------------------
# 2. Bar chart : nombre d'images par type de source
# ------------------------------------------------------------------
counts = df["source_type"].value_counts()

plt.barh(counts.index[::-1], counts.values[::-1])
plt.title("Bar Chart - Images collectées par type de source")
plt.xlabel("Nombre d'images")
plt.ylabel("Type de source")
plt.tight_layout()
plt.show()


# ------------------------------------------------------------------
# 3. Stacked bar : retrouvées / non retrouvées par licence
# ------------------------------------------------------------------
lic = df.groupby("license")["used_for_training"].agg(found="sum", total="count")
lic["not_found"] = lic["total"] - lic["found"]
lic = lic.sort_values("total", ascending=False)

plt.bar(lic.index, lic["found"], label="Retrouvée", color="steelblue")
plt.bar(lic.index, lic["not_found"], bottom=lic["found"], label="Non retrouvée", color="lightgray")
plt.title("Stacked Bar - Licence et présence dans un dataset")
plt.xlabel("Licence")
plt.ylabel("Nombre d'images")
plt.xticks(rotation=20)
plt.legend()
plt.show()


# ------------------------------------------------------------------
# 4. Pie chart : répartition des sources de type caméra
# ------------------------------------------------------------------
cams = df[df.source_group == "Caméras"]["source_type"].value_counts()

plt.pie(cams.values, labels=cams.index, autopct="%1.0f%%", startangle=90)
plt.title("Pie Chart - Répartition des sources de type caméra")
plt.show()


