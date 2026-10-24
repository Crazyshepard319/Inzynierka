"""
Geometria: przenoszenie punktow i obszarow miedzy obrazami oraz przeliczenie pikseli na milimetry.

Macierz T (3x3, z rejestracji, plik <wynik>_macierz.txt): piksel RGB (x, y, 1) -> piksel termalny.
Obszary przenosimy jako kontury (wektorowo), a nie jako obraz maski: wierzcholki konturu przechodza
przez T, a w obrazie docelowym wypelniany jest dokladnie (srodek piksela w wielokacie). Dzieki temu
mala maska (znamie: kilkadziesiat-kilkaset pikseli termowizji) nie traci ksztaltu na interpolacji. Pole liczone z ulamka
pokrycia pikseli (siatka gestsza `skala` razy) ma blad ~1% (test: losowe kwadraty).
"""
import cv2
import numpy as np
from matplotlib.path import Path as MPath

# narozniki znacznika w kolejnosci wzorca (import_cvat.py): obrys 0..7, otwor = 5, 4, 3, 6
OBRYS = [0, 1, 2, 3, 4, 5, 6, 7]
OTWOR = [5, 4, 3, 6]


def przenies_punkty(pkt, M):
    """Punkty (N, 2) przez macierz 3x3."""
    return cv2.perspectiveTransform(np.asarray(pkt, np.float64).reshape(1, -1, 2), np.asarray(M, np.float64))[0]


def kontury(maska):
    """Kontury zewnetrzne maski jako lista tablic (N, 2) float, przesuniete o pol piksela na zewnatrz.
    cv2.findContours prowadzi kontur przez srodki pikseli brzegowych, wiec wielokat jest o pol piksela
    mniejszy od maski (dla znamienia ~50 px srednicy to ~4% pola); poprawka: skalowanie wzgledem srodka
    o (r + 0.5) / r, r = promien rownowazny konturu."""
    ks, _ = cv2.findContours((np.asarray(maska) > 0).astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    wynik = []
    for k in ks:
        if len(k) < 3:
            continue
        k = k[:, 0, :].astype(np.float64)
        r = np.sqrt(max(cv2.contourArea(k.astype(np.float32)), 1e-6) / np.pi)
        c = k.mean(0)
        wynik.append(c + (k - c) * (r + 0.5) / r)
    return wynik


def wypelnij(wielokaty, ksztalt, skala=1):
    """Maska bool w siatce `ksztalt` (h, w) zageszczonej `skala` razy; wielokaty we wsp. siatki 1x.
    Piksel nalezy do maski, gdy jego srodek lezy wewnatrz wielokata (bez systematycznego zawyzania pola,
    jakie daje cv2.fillPoly). Srodek piksela (i, j) siatki 1x = punkt (j, i)."""
    h, w = ksztalt[:2]
    H, W = h * skala, w * skala
    m = np.zeros((H, W), bool)
    for p in wielokaty:
        q = (np.asarray(p, np.float64) + 0.5) * skala - 0.5       # srodki pikseli siatki gestej = liczby calkowite
        x0, y0 = np.maximum(np.floor(q.min(0)).astype(int), 0)
        x1, y1 = np.minimum(np.ceil(q.max(0)).astype(int), [W - 1, H - 1])
        if x1 < x0 or y1 < y0:
            continue
        yy, xx = np.mgrid[y0:y1 + 1, x0:x1 + 1]
        wewn = MPath(q).contains_points(np.c_[xx.ravel(), yy.ravel()]).reshape(yy.shape)
        m[y0:y1 + 1, x0:x1 + 1] |= wewn
    return m


def przenies_maske(maska, M, ksztalt_celu, skala=1):
    """Maska (uint8/bool) z obrazu zrodlowego -> maska bool w obrazie celu (opcjonalnie `skala`x gesciej)."""
    return wypelnij([przenies_punkty(k, M) for k in kontury(maska)], ksztalt_celu, skala)


def ulamek_pokrycia(maska_gesta, skala):
    """Maska `skala`x gestsza -> ulamek pokrycia kazdego piksela siatki 1x (0..1)."""
    h, w = maska_gesta.shape[0] // skala, maska_gesta.shape[1] // skala
    return maska_gesta.reshape(h, skala, w, skala).mean(axis=(1, 3))


def mm_na_px(H, punkt):
    """Lokalna skala [mm/px] homografii px -> mm w punkcie (pierwiastek z wyznacznika jakobianu)."""
    H = np.asarray(H, np.float64)
    x, y = punkt
    w = H[2, 0] * x + H[2, 1] * y + H[2, 2]
    u = (H[0, 0] * x + H[0, 1] * y + H[0, 2]) / w
    v = (H[1, 0] * x + H[1, 1] * y + H[1, 2]) / w
    J = np.array([[(H[0, 0] - u * H[2, 0]) / w, (H[0, 1] - u * H[2, 1]) / w],
                  [(H[1, 0] - v * H[2, 0]) / w, (H[1, 1] - v * H[2, 1]) / w]])
    return float(np.sqrt(abs(np.linalg.det(J))))

