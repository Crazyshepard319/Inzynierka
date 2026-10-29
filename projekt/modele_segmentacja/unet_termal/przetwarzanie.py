"""
Przetwarzanie obrazu termowizyjnego wspolne dla treningu i wnioskowania U-Netu (tylko numpy i OpenCV,
bez PyTorch - z tego modulu korzysta tez aplikacja).

Wejscie sieci: jeden kanal 240 x 320 (rozdzielczosc kamery z serii 23.10), skala szarosci jak w
dopasowanie3.wczytaj_termal (paleta inferno ma jasnosc rosnaca z temperatura), standaryzowana osobno dla
kazdego obrazu (srednia 0, odchylenie 1), wiec wynik nie zalezy od zakresu temperatur nagrania.
Obraz o innej rozdzielczosci (np. 640 x 480 z FLIR A655sc) jest skalowany do 320 x 240, a maska wraca
do rozmiaru obrazu.
"""
import cv2
import numpy as np

WEJSCIE = (320, 240)        # (szerokosc, wysokosc) wejscia sieci
PROG = 0.5                  # prog prawdopodobienstwa maski
MAX_DZIURA = 0.02           # wypelniane dziury w masce (odblaski na folii) < 2% pola obiektu


def szarosc(obraz):
    """Obraz termowizyjny (BGR z paleta albo jednokanalowy 8/16 bit) -> float32 0..255."""
    img = np.asarray(obraz)
    if img.ndim == 3:
        return cv2.cvtColor(img[:, :, :3], cv2.COLOR_BGR2GRAY).astype(np.float32)
    g = img.astype(np.float32)
    return (g - g.min()) / max(1e-6, float(g.max() - g.min())) * 255


def normalizuj(g):
    """Standaryzacja jednego obrazu: srednia 0, odchylenie 1."""
    return ((g - float(g.mean())) / max(float(g.std()), 1e-3)).astype(np.float32)


def do_rozmiaru_sieci(g, interpolacja=cv2.INTER_AREA):
    return g if g.shape[::-1] == WEJSCIE else cv2.resize(g, WEJSCIE, interpolation=interpolacja)


def wejscie_sieci(obraz):
    """Obraz termowizyjny -> tablica (1, 1, 240, 320) float32 dla sieci."""
    return normalizuj(do_rozmiaru_sieci(szarosc(obraz)))[None, None]


def maska_z_prawdopodobienstwa(p, ksztalt, prog=PROG):
    """Prawdopodobienstwo (240, 320) -> maska uint8 0/255 w rozmiarze obrazu `ksztalt`:
    skalowanie, prog, najwieksza skladowa (znacznik jest jeden), wypelnienie malych dziur."""
    h, w = ksztalt[:2]
    p = np.asarray(p, np.float32)
    if p.shape != (h, w):
        p = cv2.resize(p, (w, h), interpolation=cv2.INTER_LINEAR)
    m = (p >= prog).astype(np.uint8)
    n, lab, st, _ = cv2.connectedComponentsWithStats(m, connectivity=8)
    if n <= 1:
        return np.zeros((h, w), np.uint8)
    m = (lab == 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA]))).astype(np.uint8)
    pole = int(m.sum())
    n, lab, st, _ = cv2.connectedComponentsWithStats(1 - m, connectivity=4)
    for j in range(1, n):
        x, y, ww, hh, a = st[j]
        brzeg = x == 0 or y == 0 or x + ww == w or y + hh == h
        if not brzeg and a < MAX_DZIURA * pole:          # otwor znacznika (ok. 45% pola folii) zostaje
            m[lab == j] = 1
    return m * 255
