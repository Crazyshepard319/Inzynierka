"""Uzycie: python para_rgb_termowizja.py [numer_pary]. Rys. do rozdz. 1/4: para 14 – zdjęcie RGB i obraz termowizyjny (dane własne, seria 23.10.2026)."""
import cv2
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import sys
from pathlib import Path
para = sys.argv[1] if len(sys.argv) > 1 else "14"
# plik lezy w Inzynierka/praca/rysunki -> dane w Inzynierka/dane/pary/N
INZ = Path(__file__).resolve().parents[2]
U = str(INZ / "dane" / "pary" / para) + "/"
if not Path(U).exists():
    U = f"/mnt/user-data/uploads/Inzynierka/dane/pary/{para}/"
rgb = cv2.cvtColor(cv2.imread(U + "rgb.jpg"), cv2.COLOR_BGR2RGB)
ter = cv2.cvtColor(cv2.imread(U + "termal.jpg"), cv2.COLOR_BGR2RGB)
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10})
r1 = rgb.shape[1] / rgb.shape[0]; r2 = ter.shape[1] / ter.shape[0]
fig, ax = plt.subplots(1, 2, figsize=(6.3, 6.3 / (r1 + r2) + 0.35), gridspec_kw={"width_ratios": [r1, r2]})
for a, im, lit in ((ax[0], rgb, "a)"), (ax[1], ter, "b)")):
    a.imshow(im, interpolation="nearest" if im is ter else "antialiased")
    a.set_xticks([]); a.set_yticks([])
    a.set_xlabel(lit)
fig.tight_layout(pad=0.3, w_pad=0.6)
fig.savefig(f"para_{para}_rgb_termowizja.pdf", dpi=300)
fig.savefig(f"para_{para}_rgb_termowizja.png", dpi=250)
