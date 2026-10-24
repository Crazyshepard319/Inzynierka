"""
Wykres przebiegu treningu PanDerm + UperNet (z log.csv) do pracy.

    python -m modele_segmentacja.modele.panderm_upernet.wykres_treningu [folder_przebiegu]

Domyslnie ostatni przebieg. Zapisuje PNG (300 dpi) i PDF (wektorowy) w Inzynierka/wyniki/wyniki_segmentacji/.
"""
import csv
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

from ...konfiguracja import WYNIKI
from . import KATALOG_WAG

# referencyjna paleta (skill dataviz): sloty 1-2 + atrament i siatka
NIEBIESKI, POMARANCZOWY = "#2a78d6", "#eb6834"
TLO, TEKST, TEKST2, OSIE, SIATKA = "#fcfcfb", "#0b0b0b", "#52514e", "#898781", "#e1e0d9"
PRZECINEK = FuncFormatter(lambda v, _: f"{v:g}".replace(".", ","))


def rysuj(katalog, wyjscie):
    log = list(csv.DictReader(open(katalog / "log.csv", encoding="utf-8")))
    ep = [int(r["epoka"]) for r in log]
    strata = [float(r["strata"]) for r in log]
    dice = [float(r["val_dice"]) for r in log]
    jac = [float(r["val_jaccard"]) for r in log]
    najl = max(range(len(log)), key=lambda i: jac[i])
    test = json.loads((katalog / "wynik_test.json").read_text()) if (katalog / "wynik_test.json").exists() else None

    plt.rcParams.update({"font.family": ["Segoe UI", "DejaVu Sans"], "font.size": 9,
                         "axes.edgecolor": OSIE, "axes.labelcolor": TEKST2, "xtick.color": OSIE,
                         "ytick.color": OSIE, "text.color": TEKST})
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(10, 3.6), facecolor=TLO)
    for a in (a1, a2):
        a.set_facecolor(TLO)
        a.grid(True, color=SIATKA, linewidth=0.6)
        a.set_axisbelow(True)
        for s in ("top", "right"):
            a.spines[s].set_visible(False)
        a.set_xlabel("Epoka")
        a.set_xlim(0, ep[-1] + 1)
        a.set_xticks(range(0, ep[-1] + 1, 20 if ep[-1] > 40 else 5))
        a.yaxis.set_major_formatter(PRZECINEK)
        a.tick_params(labelcolor=TEKST2, length=3)

    a1.plot(ep, strata, color=NIEBIESKI, linewidth=1.6)
    a1.set_title("Strata treningowa (entropia krzyżowa)", loc="left", fontsize=10, color=TEKST)
    a1.set_ylim(bottom=0)

    a2.plot(ep, dice, color=NIEBIESKI, linewidth=1.6, label="Dice")
    a2.plot(ep, jac, color=POMARANCZOWY, linewidth=1.6, label="Jaccard")
    for y, nazwa in ((dice, "Dice"), (jac, "Jaccard")):          # etykiety bezposrednio przy liniach
        a2.annotate(nazwa, (ep[-1], y[-1]), xytext=(4, 0), textcoords="offset points",
                    va="center", fontsize=8.5, color=TEKST2)
    e = ep[najl]
    a2.axvline(e, color=OSIE, linewidth=0.9, linestyle=(0, (3, 3)))
    a2.plot([e, e], [dice[najl], jac[najl]], "o", markersize=5, color=TEKST,
            markeredgecolor=TLO, markeredgewidth=1.2, zorder=5)
    a2.annotate(f"najlepszy model: epoka {e}\nDice {dice[najl]:.3f}, Jaccard {jac[najl]:.3f}".replace(".", ","),
                (e, dice[najl]), xytext=(8, 6), textcoords="offset points", fontsize=8, color=TEKST2)
    a2.set_title("Walidacja ISIC 2018 (100 obrazów)", loc="left", fontsize=10, color=TEKST)
    lo = min(min(jac), min(dice))
    a2.set_ylim(max(0.0, int(lo * 20) / 20), 1.0)             # zaokraglone w dol do 0,05
    a2.set_xlim(0, ep[-1] + 12)
    a2.legend(loc="lower right", frameon=False, fontsize=8.5, labelcolor=TEKST2)
    if test:
        a2.text(0.99, 0.97, f"Test (1000 obrazów): Dice {test['Dsc']:.3f}, Jaccard {test['Jac']:.3f}".replace(".", ","),
                transform=a2.transAxes, ha="right", va="top", fontsize=8, color=TEKST2)

    fig.tight_layout(w_pad=3)
    wyjscie.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(wyjscie.with_suffix(".png"), dpi=300, facecolor=TLO)
    fig.savefig(wyjscie.with_suffix(".pdf"), facecolor=TLO)
    return wyjscie


if __name__ == "__main__":
    if len(sys.argv) > 1:
        kat = Path(sys.argv[1])
    else:
        kat = sorted(p for p in (KATALOG_WAG / "przebiegi").glob("*") if (p / "log.csv").exists()
                     and not p.name.startswith("proba"))[-1]
    out = rysuj(kat, WYNIKI / f"panderm_trening_{kat.name}")
    print(f"Zapisano: {out.with_suffix('.png')}\n          {out.with_suffix('.pdf')}")
