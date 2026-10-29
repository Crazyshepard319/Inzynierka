"""Zestawienia obrazow pary 14 do rozdzialow 5 i 6 (z plikow wynikow systemu).
    python zestawienia_para14.py <folder z obrazami> <folder wyjsciowy>"""
import sys
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

D, W = Path(sys.argv[1]), Path(sys.argv[2])
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9})
CM = 1 / 2.54


def zestaw(pliki, nazwa, wys=5.2, szer=(1, 1, 1)):
    fig, axy = plt.subplots(1, len(pliki), figsize=(16 * CM, wys * CM), gridspec_kw={"width_ratios": szer})
    for ax, (plik, litera) in zip(axy, zip(pliki, "abc")):
        ax.imshow(mpimg.imread(D / plik), interpolation="none" if "piksele" in plik else "antialiased")
        ax.set_axis_off()
        ax.set_title(f"{litera})", loc="left", fontsize=9)
    fig.tight_layout(pad=0.3, w_pad=0.6)
    fig.savefig(W / f"{nazwa}.pdf", dpi=300, bbox_inches="tight")
    fig.savefig(W / f"{nazwa}.png", dpi=200, bbox_inches="tight")
    plt.close(fig)


zestaw(["p14_debug_rgb.png", "p14_debug_termal.png", "p14_kontury.png"], "rejestracja_para14", wys=5.0,
       szer=(0.87, 1.33, 1.0))
zestaw(["p14_znacznik_modalnosci.png", "p14_nakladka_zblizenie.png"], "wyniki_para14", wys=6.5, szer=(1.24, 1.0))
print("ok")
