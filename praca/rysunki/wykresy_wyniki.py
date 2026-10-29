"""
Wykresy do rozdzialu 6 (Testy i wyniki) z wynikow systemu.

    python praca\rysunki\liczby_wynikow.py      (najpierw: zbiera dane do praca/rysunki/dane_wynikow/)
    python praca\rysunki\wykresy_wyniki.py      [folder z danymi] [folder wyjsciowy]

Domyslnie dane z praca/rysunki/dane_wynikow/, wykresy do praca/rysunki/. Pliki danych:
    pary.csv                    metryki.json wszystkich par (n = 92 w wynikach z 28.10.2026)
    porownanie_rejestracji.csv  badanie E4 (projekt/porownaj_rejestracje.py)
    unet_ocena.csv              ocena U-Netu i detektora klasycznego wzgledem CVAT (n = 94)
Wyjscie: wyk_e4_tre, wyk_e2_tre, wyk_segmentacja (.pdf + .png). Wymaga numpy i matplotlib >= 3.10.
"""
import csv
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mt
import numpy as np

TU = Path(__file__).resolve().parent
DANE = Path(sys.argv[1]) if len(sys.argv) > 1 else TU / "dane_wynikow"
WYJ = Path(sys.argv[2]) if len(sys.argv) > 2 else TU
WYJ.mkdir(parents=True, exist_ok=True)
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9, "axes.spines.top": False,
                     "axes.spines.right": False, "axes.titlesize": 9.5, "savefig.dpi": 300})
NIEB, POM, SZARY, CZERW = "#1f5fa8", "#d9822b", "#8a8a8a", "#b3261e"
CM = 1 / 2.54


def wczytaj(nazwa):
    with open(DANE / nazwa, encoding="utf-8-sig") as f:
        return list(csv.DictReader(f, delimiter=";"))


def liczba(x):
    try:
        return float(str(x).replace(",", "."))
    except ValueError:
        return np.nan


def kolumna(wiersze, k):
    return np.array([liczba(w[k]) for w in wiersze])


def przecinek(fmt="{:g}"):
    return mt.FuncFormatter(lambda v, _: fmt.format(v).replace(".", ","))


def zapisz(fig, nazwa):
    fig.savefig(WYJ / f"{nazwa}.pdf", bbox_inches="tight")
    fig.savefig(WYJ / f"{nazwa}.png", bbox_inches="tight", dpi=200)
    plt.close(fig)


def pudelka(ax, dane, etykiety, kolory, poziomo=False):
    rng = np.random.default_rng(0)
    bp = ax.boxplot(dane, orientation="horizontal" if poziomo else "vertical", widths=0.5, showfliers=False, patch_artist=True,
                    medianprops=dict(color="black", lw=1.4), whiskerprops=dict(color=SZARY),
                    capprops=dict(color=SZARY), boxprops=dict(edgecolor=SZARY))
    for p, k in zip(bp["boxes"], kolory):
        p.set_facecolor(k)
        p.set_alpha(0.25)
    for i, (v, k) in enumerate(zip(dane, kolory), 1):
        j = i + rng.uniform(-0.17, 0.17, len(v))
        (ax.scatter(v, j, s=7, color=k, alpha=0.7, lw=0) if poziomo else
         ax.scatter(j, v, s=7, color=k, alpha=0.7, lw=0))
    (ax.set_yticks if poziomo else ax.set_xticks)(range(1, len(dane) + 1))
    (ax.set_yticklabels if poziomo else ax.set_xticklabels)(etykiety)


P = wczytaj("pary.csv" if (DANE / "pary.csv").exists() else "pary_28_10.csv")
pary = {int(w["para"]) for w in P}
E4 = [w for w in wczytaj("porownanie_rejestracji.csv") if int(w["para"]) in pary]
U = wczytaj("unet_ocena.csv")

# ── E4: TRE czterech metod (skala logarytmiczna) ─────────────────────────────
metody = [("start_tre_mm", "dopasowanie wstępne\n(bez optymalizacji)", SZARY),
          ("mi_caly_tre_mm", "informacja wzajemna\n– cały obraz", POM),
          ("mi_otoczenie_tre_mm", "informacja wzajemna\n– otoczenie znacznika", POM),
          ("d3_tre_mm", "ECC na maskach\nznacznika (system)", NIEB)]
dane = [kolumna(E4, k) for k, _, _ in metody]
fig, ax = plt.subplots(figsize=(15 * CM, 6.4 * CM))
pudelka(ax, dane, [e for _, e, _ in metody], [k for _, _, k in metody], poziomo=True)
ax.set_xscale("log")
ax.xaxis.set_major_formatter(przecinek())
ax.set_xticks([0.3, 0.5, 1, 2, 5, 10, 20, 50])
ax.axvline(1.0, color=CZERW, lw=1, ls="--")
ax.text(1.05, 4.42, "1 mm (WN4)", color=CZERW, fontsize=8, va="bottom")
for i, v in enumerate(dane, 1):
    ax.text(ax.get_xlim()[1] * 0.97, i + 0.3, f"mediana {np.median(v):.2f} mm".replace(".", ",")
            + f";  ≤ 1 mm: {(v <= 1).sum()}/{len(v)}", ha="right", fontsize=7.5, color="0.25")
ax.set_xlabel("TRE – średni błąd położenia 8 narożników znacznika [mm] (skala logarytmiczna)")
zapisz(fig, "wyk_e4_tre")

# ── E2 a TRE: zgodnosc masek bez adnotacji wykrywa zla rejestracje ──────────
tre, e2f, e2o = kolumna(P, "tre"), kolumna(P, "e2_folia_dice"), kolumna(P, "e2_otwor_dice")
rangi = lambda v: np.argsort(np.argsort(v))
rho = float(np.corrcoef(rangi(e2f), rangi(tre))[0, 1])          # wspolczynnik Spearmana (bez remisow)
fig, ax = plt.subplots(figsize=(15 * CM, 6.6 * CM))
zle = tre > 1
ax.scatter(tre[~zle], e2f[~zle], s=14, color=NIEB, alpha=0.75, lw=0, label="TRE ≤ 1 mm")
ax.scatter(tre[zle], e2f[zle], s=18, color=CZERW, alpha=0.85, lw=0, marker="D", label="TRE > 1 mm")
for w, x, y in zip(P, tre, e2f):
    if x > 1.6 or y < 0.9:
        ax.annotate(f"para {w['para']}", (x, y), xytext=((-40, 2) if x > 10 else (4, -9)), textcoords="offset points",
                    fontsize=7, color="0.3")
ax.set_xscale("log")
ax.set_xticks([0.3, 0.5, 1, 2, 5, 10, 20])
ax.xaxis.set_major_formatter(przecinek())
ax.yaxis.set_major_formatter(przecinek("{:.2f}"))
ax.axvline(1.0, color=SZARY, lw=0.8, ls="--")
ax.set_xlabel("TRE względem adnotacji CVAT [mm] (badanie E1, skala logarytmiczna)")
ax.set_ylabel("Dice folii – badanie E2\n(bez adnotacji)")
ax.text(0.98, 0.90, f"współczynnik Spearmana ρ = {rho:.2f}".replace(".", ","), transform=ax.transAxes,
        ha="right", fontsize=8)
ax.legend(loc="lower left", fontsize=7.5, frameon=False)
zapisz(fig, "wyk_e2_tre")

# ── segmentacja: Dice wzgledem CVAT ──────────────────────────────────────────
seg = [(kolumna(P, "panderm_dice"), f"M1 PanDerm + UperNet\nznamię, zdjęcie\nn = {len(P)}", NIEB),
       (kolumna(U, "unet_dice"), f"M3 U-Net\nznacznik, termowizja\nn = {len(U)}", POM),
       (kolumna(U, "klasyczny_dice"), f"detektor klasyczny\nznacznik, termowizja\nn = {len(U)}", SZARY)]
fig, ax = plt.subplots(figsize=(15 * CM, 6.2 * CM))
pudelka(ax, [d for d, _, _ in seg], [e for _, e, _ in seg], [k for _, _, k in seg])
ax.yaxis.set_major_formatter(przecinek("{:.1f}"))
ax.set_ylim(0.25, 1.0)
ax.set_ylabel("współczynnik Dice'a\nwzględem adnotacji CVAT")
for i, (d, _, _) in enumerate(seg, 1):
    ax.text(i + 0.3, 0.30, f"mediana\n{np.median(d):.3f}".replace(".", ","), fontsize=7.5, ha="left", color="0.25")
zapisz(fig, "wyk_segmentacja")
print("zapisano:", sorted(p.name for p in WYJ.glob("wyk_*")))
