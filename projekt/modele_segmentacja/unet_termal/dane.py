"""
Zbior uczacy U-Netu: obrazy termowizyjne par (dane/pary/N/termal.jpg) i maski znacznika oznaczone
recznie w CVAT (dane/pary/N/maska_znacznik_termal.png), podzial na foldy po znamionach z dane/znamiona.csv
(wszystkie zdjecia jednego znamienia sa w tym samym foldzie, wiec test nie widzi znamienia z treningu).

Augmentacja (tylko trening): obrot o dowolny kat, skala 0,75-1,3, przesuniecie do 15%, odbicia,
zmiana gamma i kontrastu, rozmycie i szum - znacznik moze lezec pod dowolnym katem i w roznej odleglosci,
a jasnosc zalezy od temperatury skory i otoczenia odbijanego w folii.
"""
import csv
from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np

from .przetwarzanie import do_rozmiaru_sieci, normalizuj, szarosc

INZ = Path(__file__).resolve().parents[3]           # folder Inzynierka
PARY = INZ / "dane" / "pary"
ZNAMIONA = INZ / "dane" / "znamiona.csv"


@dataclass
class Zbior:
    obrazy: np.ndarray       # (N, 240, 320) float32 0..255 (skala szarosci)
    maski: np.ndarray        # (N, 240, 320) bool
    pary: np.ndarray         # numery par
    znamie: np.ndarray       # numer znamienia
    fold: np.ndarray         # fold 1..5

    def wybierz(self, idx):
        return Zbior(self.obrazy[idx], self.maski[idx], self.pary[idx], self.znamie[idx], self.fold[idx])


def _imread(p, flagi):
    b = np.fromfile(str(p), np.uint8)
    return cv2.imdecode(b, flagi) if b.size else None


def wczytaj_z_par(pary_dir=PARY, znamiona_csv=ZNAMIONA):
    """Pary, ktore maja termal.jpg i maske znacznika z CVAT oraz wpis w znamiona.csv."""
    with open(znamiona_csv, encoding="utf-8-sig") as f:
        podzial = {int(r["para"]): (int(r["znamie"]), int(r["fold"])) for r in csv.DictReader(f, delimiter=";")}
    X, Y, P = [], [], []
    for n in sorted(podzial):
        k = Path(pary_dir) / str(n)
        t, m = _imread(k / "termal.jpg", cv2.IMREAD_UNCHANGED), _imread(k / "maska_znacznik_termal.png", cv2.IMREAD_GRAYSCALE)
        if t is None or m is None:
            continue
        X.append(do_rozmiaru_sieci(szarosc(t)))
        Y.append(do_rozmiaru_sieci(m.astype(np.float32), cv2.INTER_NEAREST) > 127)
        P.append(n)
    if not P:
        raise FileNotFoundError(f"Brak par z termal.jpg i maska_znacznik_termal.png w {pary_dir}")
    return Zbior(np.array(X, np.float32), np.array(Y), np.array(P),
                 np.array([podzial[n][0] for n in P]), np.array([podzial[n][1] for n in P]))


def wczytaj_npz(sciezka):
    """Ten sam zbior zapisany w jednym pliku (obrazy BGR, maski, pary, znamie, fold)."""
    d = np.load(sciezka)
    X = np.array([do_rozmiaru_sieci(szarosc(t)) for t in d["obrazy"]], np.float32)
    Y = np.array([do_rozmiaru_sieci(m.astype(np.float32), cv2.INTER_NEAREST) > 0.5 for m in d["maski"]])
    return Zbior(X, Y, d["pary"], d["znamie"], d["fold"])


def augmentuj(g, m, rng):
    """Losowe przeksztalcenie pary (obraz 0..255, maska bool) - ta sama geometria dla obu."""
    h, w = g.shape
    A = cv2.getRotationMatrix2D((w / 2, h / 2), rng.uniform(0, 360), rng.uniform(0.75, 1.3))
    A[:, 2] += rng.uniform(-0.15, 0.15, 2) * (w, h)
    g = cv2.warpAffine(g, A, (w, h), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT_101)
    m = cv2.warpAffine(m.astype(np.float32), A, (w, h), flags=cv2.INTER_LINEAR,
                       borderMode=cv2.BORDER_REFLECT_101) > 0.5
    if rng.random() < 0.5:
        g, m = g[:, ::-1], m[:, ::-1]
    if rng.random() < 0.5:
        g, m = g[::-1], m[::-1]
    g = 255 * (np.clip(g, 0, 255) / 255) ** rng.uniform(0.7, 1.5)
    g = (g - g.mean()) * rng.uniform(0.8, 1.2) + g.mean()
    if rng.random() < 0.3:
        g = cv2.GaussianBlur(np.ascontiguousarray(g, np.float32), (0, 0), rng.uniform(0.3, 1.2))
    g = g + rng.normal(0, rng.uniform(0, 6), g.shape)
    return np.ascontiguousarray(g, np.float32), np.ascontiguousarray(m)


def paczka(zbior, idx, rng=None):
    """Tablice (B, 1, H, W) dla sieci: obrazy znormalizowane, maski float 0/1; rng = augmentacja."""
    X, Y = [], []
    for i in idx:
        g, m = zbior.obrazy[i], zbior.maski[i]
        if rng is not None:
            g, m = augmentuj(g, m, rng)
        X.append(normalizuj(g))
        Y.append(m.astype(np.float32))
    return np.stack(X)[:, None], np.stack(Y)[:, None]
