"""
Obszar analizy z wnetrza znacznika ㄇ (Π) na zdjeciu RGB - bez obrazu termalnego.

Znamie lezy miedzy ramionami znacznika, wiec model segmentacji dostaje tylko
wnetrze znacznika, a nie cale zdjecie:
  1. Folia: te same kryteria co w dopasowanie3.py (niskie nasycenie barwy,
     odleglosc od koloru skory), dodatkowo z warunkiem jasnosci (oddziela folie
     od ciemnych wlosow). Ksztalt kandydata porownywany jest z syntetycznym
     szablonem ㄇ (max IoU po obrocie) zamiast z maska z termowizji.
  2. Wnetrze = otoczka wypukla folii minus folia (otwor miedzy ramionami).
  3. Obszar = wnetrze poszerzone o margines (znamie moze wystawac za linie
     konca ramion), bez folii. ROI = prostokat obejmujacy obszar.

Uzycie:
    from modele_segmentacja.znacznik import wykryj_znacznik, segmentuj_w_znaczniku
    z = wykryj_znacznik(obraz_bgr)                 # Znacznik albo wyjatek BrakZnacznika
    wynik = segmentuj_w_znaczniku(model, obraz_bgr)  # WynikSegmentacji, maska tylko w obszarze

Sprawdzenie calego folderu zdjec (np. przed adnotacja w CVAT):
    python -m modele_segmentacja.znacznik <folder> [--wyjscie <folder>]
    -> podglady z konturami + znaczniki.csv (zgodnosc ksztaltu, udzial wnetrza, ROI)
"""
import sys
import time
from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np

try:
    import dopasowanie3 as _d
except ImportError:                                   # uruchomienie spoza folderu projekt
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    import dopasowanie3 as _d

DET_PX = 800            # dluzszy bok obrazu roboczego (detekcja); ROI nie wymaga pelnej rozdzielczosci

# Ksztalt znacznika: belka o dlugosci 1, ramiona o dlugosci GLEBOKOSC, pasek tasmy o szerokosci PASEK.
# Zmierzone na 5 zdjeciach z 17.10.2026 (dopasowanie szablonu: IoU ksztaltu 0,91-0,95).
GLEBOKOSC = 0.70
PASEK = 0.24

MIN_ZGODNOSC = 0.70            # IoU z szablonem: znaczniki 0,91-0,95, inne obiekty na zdjeciach <= 0,55
MIN_ZGODNOSC_POD_KATEM = 0.58  # zdjecie mocno pod katem (perspektywa) obniza IoU do ~0,64-0,75 -
UDZIAL_TYPOWY = (0.22, 0.48)   # wtedy wystarczy nizsza zgodnosc, jesli otwor ma typowy udzial
UDZIAL_WNETRZA = (0.15, 0.60)  # pole otworu / pole otoczki wypuklej (dla ksztaltu wyzej: 0,34)
MIN_POLE_ZNACZNIKA = 0.02      # otoczka wypukla znacznika / pole zdjecia (na zdjeciach z 17.10: 0,4-0,55)
MARGINES = 0.08                # poszerzenie otworu, ulamek sqrt(pola otworu)


class BrakZnacznika(RuntimeError):
    """Na zdjeciu nie znaleziono znacznika ㄇ (powod w tresci wyjatku)."""


@dataclass
class Znacznik:
    maska: np.ndarray        # tasma (folia), uint8 0/255, rozmiar zdjecia
    wnetrze: np.ndarray      # otwor miedzy ramionami (otoczka wypukla - tasma)
    obszar: np.ndarray       # gdzie wolno szukac znamienia: wnetrze + margines, bez tasmy
    roi: tuple               # (x, y, w, h) prostokat obejmujacy obszar
    zgodnosc: float          # IoU ksztaltu z szablonem ㄇ
    udzial_wnetrza: float    # pole otworu / pole otoczki wypuklej
    opis: str                # kryterium, ktore dalo najlepszy ksztalt
    czas_s: float = 0.0


# ── detekcja ─────────────────────────────────────────────────────────────────

def szablon(rozmiar=200, glebokosc=GLEBOKOSC, pasek=PASEK):
    """Syntetyczna maska ㄇ: belka u gory, ramiona w dol."""
    W, H, t = rozmiar, int(round(rozmiar * glebokosc)), int(round(rozmiar * pasek))
    m = np.zeros((H + 20, W + 20), np.uint8)
    m[10:10 + t, 10:10 + W] = 255
    m[10:10 + H, 10:10 + t] = 255
    m[10:10 + H, 10 + W - t:10 + W] = 255
    return m


def _najlepszy_ksztalt(im, wzor):
    """(zgodnosc, opis, maska) najlepszego kandydata na folie w obrazie roboczym albo None."""
    H, W = im.shape[:2]
    k = _d._kolo(max(2, min(H, W) // 200))
    min_pole = 0.0007 * H * W
    lab = cv2.cvtColor(im, cv2.COLOR_BGR2LAB).astype(np.float32)
    C = cv2.GaussianBlur(np.hypot(lab[..., 1] - 128, lab[..., 2] - 128), (0, 0), 1.5)
    L = cv2.GaussianBlur(lab[..., 0], (0, 0), 1.5)
    c_skora = float(np.percentile(C, 90))
    progi_L = {q: float(np.percentile(L, q)) for q in (35, 60)}

    najl = None
    # przebieg 1: folia = niskie nasycenie barwy; z warunkiem jasnosci oddziela sie od ciemnych
    # wlosow (tez maja niskie nasycenie i zlewaja sie z folia w plame dotykajaca brzegu zdjecia)
    for f in (0.15, 0.22, 0.30, 0.38, 0.46, 0.55, 0.65):
        niskie = C < f * c_skora
        warianty = [(niskie, f"chroma < {f:.2f}*skora")]
        warianty += [(niskie & (L > l), f"chroma < {f:.2f}*skora, L > p{q}") for q, l in progi_L.items()]
        for b, opis in warianty:
            najl = _d._najlepszy_kandydat(_d._skladowe(b.astype(np.uint8) * 255, k, min_pole),
                                          wzor, False, najl, opis)
    if najl is None:
        return None
    # przebieg 2: wszystko, co odbiega od koloru skory wokol najlepszego kandydata
    # (lustrzana folia odbijajaca biel albo skore)
    D, roi = _d.odleglosc_od_skory(im, najl[2])
    for t in (2.5, 3.5, 5.0, 7.0):
        najl = _d._najlepszy_kandydat(_d._skladowe((D > t).astype(np.uint8) * 255, k, min_pole, roi),
                                      wzor, False, najl, f"odl. od skory > {t}")
    return najl


def _odstep_od_folii(maska):
    """Pas przy krawedzi folii pomijany w obszarze (ciemny brzeg tasmy i jej cien), w px maski."""
    return max(1, int(round(0.004 * max(maska.shape))))


def wnetrze_znacznika(maska):
    """Otwor miedzy ramionami: najwieksza skladowa (otoczka wypukla - tasma).
    Zwraca (wnetrze uint8 0/255, udzial pola otworu w polu otoczki)."""
    pkt = cv2.findNonZero(maska)
    if pkt is None:
        return np.zeros_like(maska), 0.0
    otoczka = np.zeros_like(maska)
    cv2.fillConvexPoly(otoczka, cv2.convexHull(pkt), 255)
    r = _odstep_od_folii(maska)
    otwor = cv2.subtract(otoczka, cv2.dilate(maska, _d._kolo(r)))
    otwor = cv2.morphologyEx(otwor, cv2.MORPH_OPEN, _d._kolo(2 * r))     # odetnij waskie paski przy brzegach
    n, lab, st, _ = cv2.connectedComponentsWithStats(otwor, connectivity=4)
    if n < 2:
        return np.zeros_like(maska), 0.0
    j = 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA]))
    return (lab == j).astype(np.uint8) * 255, st[j, cv2.CC_STAT_AREA] / max(1, cv2.countNonZero(otoczka))


def znacznik_z_maski(maska, ksztalt_obrazu, sc=1.0, zgodnosc=float("nan"), opis="maska z zewnatrz"):
    """Znacznik z gotowej maski folii, np. z rejestracji (dopasowanie3.wykryj_znacznik_rgb:
    rgb['maska'] w skali roboczej rgb['sc']). ksztalt_obrazu: (wysokosc, szerokosc) zdjecia."""
    H0, W0 = ksztalt_obrazu[:2]
    wnetrze, udzial = wnetrze_znacznika(maska)
    if not wnetrze.any():
        raise BrakZnacznika("znacznik nie ma otworu (wnetrza) - to nie jest ksztalt Pi")
    if not UDZIAL_WNETRZA[0] <= udzial <= UDZIAL_WNETRZA[1]:
        raise BrakZnacznika(f"nietypowe wnetrze znacznika (udzial {udzial:.2f}, oczekiwane "
                            f"{UDZIAL_WNETRZA[0]:.2f}-{UDZIAL_WNETRZA[1]:.2f})")
    m = max(1, int(round(MARGINES * np.sqrt(cv2.countNonZero(wnetrze)))))
    obszar = cv2.subtract(cv2.dilate(wnetrze, _d._kolo(m)), cv2.dilate(maska, _d._kolo(_odstep_od_folii(maska))))

    def pelna(x):                                  # skala robocza -> rozdzielczosc zdjecia
        if sc == 1.0 and x.shape[:2] == (H0, W0):
            return x
        return (cv2.resize(x, (W0, H0), interpolation=cv2.INTER_LINEAR) > 127).astype(np.uint8) * 255

    maska, wnetrze, obszar = pelna(maska), pelna(wnetrze), pelna(obszar)
    roi = tuple(int(v) for v in cv2.boundingRect(obszar))
    return Znacznik(maska, wnetrze, obszar, roi, float(zgodnosc), float(udzial), opis)


def _podpowiedz(im):
    """Czy na zdjeciu jest duzy jasny, szary obiekt dotykajacy brzegu (uciety znacznik)?"""
    H, W = im.shape[:2]
    lab = cv2.cvtColor(im, cv2.COLOR_BGR2LAB).astype(np.float32)
    C = np.hypot(lab[..., 1] - 128, lab[..., 2] - 128)
    b = ((C < 0.38 * np.percentile(C, 90)) & (lab[..., 0] > np.percentile(lab[..., 0], 35))).astype(np.uint8)
    n, _, st, _ = cv2.connectedComponentsWithStats(b, connectivity=8)
    for x, y, w, h, a in st[1:]:
        if a > 0.03 * H * W and (x == 0 or y == 0 or x + w == W or y + h == H):
            return " Duzy jasny obiekt dotyka krawedzi zdjecia - znacznik moze byc uciety (musi byc caly w kadrze)."
    return ""


def wykryj_znacznik(obraz_bgr, min_zgodnosc=MIN_ZGODNOSC):
    """Znacznik ㄇ na zdjeciu RGB (BGR, uint8). Wyjatek BrakZnacznika, gdy go nie ma."""
    t0 = time.perf_counter()
    H0, W0 = obraz_bgr.shape[:2]
    sc = min(1.0, DET_PX / max(H0, W0))
    im = cv2.resize(obraz_bgr, (int(round(W0 * sc)), int(round(H0 * sc))), interpolation=cv2.INTER_AREA)
    najl = _najlepszy_ksztalt(im, szablon())
    if najl is None:
        raise BrakZnacznika("brak kandydatow na folie (jasne, szare obszary)." + _podpowiedz(im))
    zgodnosc, opis, maska = najl
    if zgodnosc < min(min_zgodnosc, MIN_ZGODNOSC_POD_KATEM):
        raise BrakZnacznika(f"najbardziej podobny obiekt ma zgodnosc ksztaltu z Pi {zgodnosc:.2f} "
                            f"(potrzeba >= {min_zgodnosc:.2f})." + _podpowiedz(im))
    udzial_otoczki = cv2.contourArea(cv2.convexHull(cv2.findNonZero(maska))) / (im.shape[0] * im.shape[1])
    if udzial_otoczki < MIN_POLE_ZNACZNIKA:
        raise BrakZnacznika(f"najbardziej podobny obiekt jest za maly ({100 * udzial_otoczki:.1f}% zdjecia) "
                            f"- to raczej nie znacznik.")
    z = znacznik_z_maski(maska, (H0, W0), sc, zgodnosc, opis)
    if zgodnosc < min_zgodnosc and not UDZIAL_TYPOWY[0] <= z.udzial_wnetrza <= UDZIAL_TYPOWY[1]:
        raise BrakZnacznika(f"najbardziej podobny obiekt ma zgodnosc ksztaltu z Pi {zgodnosc:.2f} "
                            f"i nietypowe wnetrze ({z.udzial_wnetrza:.2f}).")
    z.czas_s = time.perf_counter() - t0
    return z


# ── segmentacja i podglad ────────────────────────────────────────────────────

def segmentuj_w_znaczniku(model, obraz_bgr, znacznik=None, przyblizaj=True):
    """Segmentacja znamienia tylko we wnetrzu znacznika (maska ograniczona do z.obszar).
    Wynik: WynikSegmentacji z info["znacznik"]. Wyjatek BrakZnacznika, gdy nie ma znacznika."""
    z = znacznik if znacznik is not None else wykryj_znacznik(obraz_bgr)
    wynik = model.segmentuj(obraz_bgr, roi=z.roi, przyblizaj=przyblizaj, obszar=z.obszar)
    wynik.info["znacznik"] = z
    return wynik


def podglad(obraz_bgr, z, maks_px=1200):
    """Zdjecie z konturami: tasma (zielony), wnetrze (zolty), ROI (pomaranczowy)."""
    H, W = obraz_bgr.shape[:2]
    s = min(1.0, maks_px / max(H, W))
    img = cv2.resize(obraz_bgr, (int(W * s), int(H * s)), interpolation=cv2.INTER_AREA)
    for m, kol, gr in ((z.maska, (0, 220, 0), 2), (z.wnetrze, (0, 230, 255), 2)):
        ms = cv2.resize(m, (img.shape[1], img.shape[0]), interpolation=cv2.INTER_NEAREST)
        ks, _ = cv2.findContours(ms, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cv2.drawContours(img, ks, -1, kol, gr, cv2.LINE_AA)
    x, y, w, h = (int(round(v * s)) for v in z.roi)
    cv2.rectangle(img, (x, y), (x + w, y + h), (0, 140, 255), 2, cv2.LINE_AA)
    cv2.putText(img, f"zgodnosc {z.zgodnosc:.2f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8,
                (0, 0, 0), 4, cv2.LINE_AA)
    cv2.putText(img, f"zgodnosc {z.zgodnosc:.2f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8,
                (255, 255, 255), 2, cv2.LINE_AA)
    return img


# ── sprawdzenie folderu ──────────────────────────────────────────────────────

ROZSZERZENIA = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff"}


def sprawdz_folder(folder, wyjscie=None):
    """Detekcja znacznika na wszystkich zdjeciach w folderze (rekurencyjnie: folder na znamie).
    Zapisuje podglady i znaczniki.csv. Zwraca liste wierszy."""
    import csv
    from datetime import datetime
    from .interfejs import wczytaj_obraz, zapisz_obraz
    from .konfiguracja import WYNIKI

    folder = Path(folder)
    if wyjscie is None:
        wyjscie = WYNIKI / "znaczniki" / f"{folder.name}_{datetime.now():%Y%m%d_%H%M%S}"
    wyjscie = Path(wyjscie)
    pliki = sorted(p for p in folder.rglob("*") if p.suffix.lower() in ROZSZERZENIA and p.is_file()
                   and not p.stem.endswith("_wzorzec") and not p.name.startswith("_")
                   and wyjscie not in p.parents)
    heic = [p for p in folder.rglob("*") if p.suffix.lower() in (".heic", ".heif")]
    if heic:
        print(f"UWAGA: {len(heic)} plikow HEIC/HEIF - OpenCV ich nie czyta, wyeksportuj je jako JPG.")
    if not pliki:
        print(f"Brak zdjec w {folder}")
        return []
    wyjscie.mkdir(parents=True, exist_ok=True)
    print(f"Zdjecia: {len(pliki)}   podglady: {wyjscie}")

    wiersze = []
    for i, p in enumerate(pliki, 1):
        wzgl = p.relative_to(folder)
        znamie = wzgl.parent.as_posix() if wzgl.parent != Path(".") else ""
        img = wczytaj_obraz(p)
        w = dict(plik=wzgl.as_posix(), znamie=znamie, znaleziono=0, zgodnosc="", udzial_wnetrza="",
                 roi_x="", roi_y="", roi_w="", roi_h="", roi_udzial_zdjecia="",
                 czas_s="", uwagi="")
        if img is None:
            w["uwagi"] = "nie mozna wczytac pliku"
        else:
            try:
                z = wykryj_znacznik(img)
                x, y, rw, rh = z.roi
                w.update(znaleziono=1, zgodnosc=f"{z.zgodnosc:.3f}", udzial_wnetrza=f"{z.udzial_wnetrza:.3f}",
                         roi_x=x, roi_y=y, roi_w=rw, roi_h=rh,
                         roi_udzial_zdjecia=f"{rw * rh / (img.shape[0] * img.shape[1]):.3f}",
                         czas_s=f"{z.czas_s:.2f}")
                cel = wyjscie / wzgl.with_suffix(".jpg")
                cel.parent.mkdir(parents=True, exist_ok=True)
                zapisz_obraz(cel, podglad(img, z))
            except BrakZnacznika as e:
                w["uwagi"] = str(e)
        wiersze.append(w)
        stan = f"OK  zgodnosc {w['zgodnosc']}" if w["znaleziono"] else f"BRAK  {w['uwagi']}"
        print(f"  [{i}/{len(pliki)}] {wzgl.as_posix()}: {stan}")

    with open(wyjscie / "znaczniki.csv", "w", newline="", encoding="utf-8-sig") as f:
        wr = csv.DictWriter(f, fieldnames=list(wiersze[0]), delimiter=";")
        wr.writeheader()
        wr.writerows(wiersze)

    ok = sum(w["znaleziono"] for w in wiersze)
    print(f"\nZnacznik znaleziony na {ok}/{len(wiersze)} zdjeciach. Wyniki: {wyjscie / 'znaczniki.csv'}")
    znamiona = {}
    for w in wiersze:
        znamiona.setdefault(w["znamie"], []).append(w)
    if len(znamiona) > 1 or "" not in znamiona:
        pojedyncze = [k for k, v in znamiona.items() if len(v) == 1]
        print(f"Znamiona (foldery): {len(znamiona)}" + (f"; z jednym zdjeciem: {', '.join(pojedyncze)}"
                                                         if pojedyncze else ""))
    else:
        print("Wskazowka: zdjecia leza w jednym folderze - do podzialu train/test daj kazde znamie "
              "do osobnego podfolderu (znamie_01/, znamie_02/, ...).")
    return wiersze


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="Detekcja znacznika Pi na wszystkich zdjeciach w folderze")
    ap.add_argument("folder", help="folder ze zdjeciami (podfoldery = znamiona)")
    ap.add_argument("--wyjscie", default=None, help="folder na podglady i CSV (domyslnie wyniki/znaczniki/...)")
    a = ap.parse_args()
    sprawdz_folder(a.folder, a.wyjscie)
