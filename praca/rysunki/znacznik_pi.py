"""Rysunek wymiarowy znacznika Π (wymiary z dopasowanie3.py: BELKA=35, RAMIE=26, PASEK=9 mm)."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Rectangle, Ellipse

B, R, P = 35.0, 26.0, 9.0
W = [(0, 0), (B, 0), (B, R), (B - P, R), (B - P, P), (P, P), (P, R), (0, R)]   # kolejnosc jak WZORZEC_MM

plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9})
fig, ax = plt.subplots(figsize=(5.6, 4.6))
ax.add_patch(Polygon(W, closed=True, facecolor="#d9d9d9", edgecolor="black", lw=1.2, hatch="////"))
ax.add_patch(Rectangle((P, P), B - 2 * P, R - P, fill=False, ls="--", lw=1.0, edgecolor="black"))
ax.add_patch(Ellipse((B / 2, P + (R - P) / 2 + 1), 4.0, 3.2, facecolor="#7f7f7f", edgecolor="black", lw=0.8))
ax.text(B / 2, P + (R - P) / 2 + 4.6, "znamię", ha="center", va="center")
ax.text(B / 2, P + 2.6, "otwór (ROI)\n17 × 17 mm = 289 mm²", ha="center", va="center", fontsize=8.5)

# numery naroznikow
off = {0: (-1.6, -1.4), 1: (1.6, -1.4), 2: (1.6, 1.4), 3: (-1.4, 1.4), 4: (-1.6, -1.2), 5: (1.6, -1.2), 6: (1.4, 1.4), 7: (-1.6, 1.4)}
for i, (x, y) in enumerate(W):
    ax.plot(x, y, "o", ms=3.5, color="black")
    dx, dy = off[i]
    ax.text(x + dx, y + dy, f"P{i + 1}", ha="center", va="center", fontsize=8.5, fontweight="bold")

def wym(x0, y0, x1, y1, txt, odsun=(0, 0), rot=0):
    ax.annotate("", xy=(x0, y0), xytext=(x1, y1), arrowprops=dict(arrowstyle="<->", lw=0.8, shrinkA=0, shrinkB=0))
    ax.text((x0 + x1) / 2 + odsun[0], (y0 + y1) / 2 + odsun[1], txt, ha="center", va="center", rotation=rot,
            bbox=dict(fc="white", ec="none", pad=0.6))

wym(0, -4.5, B, -4.5, "35 mm")                       # belka
ax.plot([0, 0], [-0.8, -5.3], lw=0.5, color="black"); ax.plot([B, B], [-0.8, -5.3], lw=0.5, color="black")
wym(B + 4.5, 0, B + 4.5, R, "26 mm", rot=90)          # ramie (wysokosc calkowita)
ax.plot([B + 0.8, B + 5.3], [0, 0], lw=0.5, color="black"); ax.plot([B + 0.8, B + 5.3], [R, R], lw=0.5, color="black")
wym(0, R + 3.2, P, R + 3.2, "9 mm")                   # szerokosc paska (ramie)
ax.plot([0, 0], [R + 0.8, R + 4.0], lw=0.5, color="black"); ax.plot([P, P], [R + 0.8, R + 4.0], lw=0.5, color="black")
wym(-4.0, 0, -4.0, P, "9 mm", rot=90)                 # grubosc belki
ax.plot([-0.8, -4.8], [0, 0], lw=0.5, color="black"); ax.plot([-0.8, -4.8], [P, P], lw=0.5, color="black")
wym(P, R + 3.2, B - P, R + 3.2, "17 mm")              # szerokosc otworu
ax.plot([B - P, B - P], [R + 0.8, R + 4.0], lw=0.5, color="black")

ax.set_xlim(-7.5, B + 7.5)
ax.set_ylim(R + 6.5, -7.5)
ax.set_aspect("equal")
ax.axis("off")
ax.text(B / 2 + 9.5, 3.3, "folia aluminiowa", ha="center", va="center", fontsize=8.5,
        bbox=dict(fc="white", ec="black", lw=0.6, pad=1.5))
fig.tight_layout()
fig.savefig("znacznik_pi_wymiary.pdf")
fig.savefig("znacznik_pi_wymiary.png", dpi=250)
