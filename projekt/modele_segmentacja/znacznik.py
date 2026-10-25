"""
Obszar analizy z wnetrza znacznika ㄇ (Π) na zdjeciu RGB - bez obrazu termalnego.

Znamie lezy miedzy ramionami znacznika, wiec model segmentacji dostaje tylko
wnetrze znacznika, a nie cale zdjecie:
  1. Folia: ta sama detekcja co w rejestracji (dopasowanie3.wykryj_folie_rgb: barwa chlodniejsza
     od skory i tekstura, wybor kandydata po podobienstwie do wzorca Π 35 x 26 mm, pasek 9 mm).
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

UDZIAL_WNETRZA = (0.15, 0.60)  # pole otworu / pole otoczki wypuklej (dla ksztaltu wyzej: 0,34)
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


def wykryj_znacznik(obraz_bgr, min_zgodnosc=None):
    """Znacznik Π na zdjeciu RGB (BGR, uint8) - ta sama detekcja co w rejestracji
    (dopasowanie3.wykryj_folie_rgb). Wyjatek BrakZnacznika, gdy go nie ma."""
    t0 = time.perf_counter()
    min_zgodnosc = _d.MIN_ZGODNOSC if min_zgodnosc is None else min_zgodnosc
    try:
        w = _d.wykryj_folie_rgb(obraz_bgr)
    except RuntimeError as e:
        raise BrakZnacznika(str(e) + "." + _podpowiedz(obraz_bgr)) from None
    if w["zgodnosc"] < min_zgodnosc:
        raise BrakZnacznika(f"najbardziej podobny obiekt ma zgodnosc ksztaltu z Pi {w['zgodnosc']:.2f} "
                            f"(potrzeba >= {min_zgodnosc:.2f})." + _podpowiedz(w["im"]))
    z = znacznik_z_maski(w["maska"], obraz_bgr.shape[:2], w["sc"], w["zgodnosc"], w["opis"])
    z.czas_s = time.perf_counter() - t0
    return z


# ── segmentacja i podglad ────────────────────────────────────────────────────

ILE_PROPOZYCJI = 3          # ilu kandydatow na znamie segmentuje model
SPADEK_KONTRASTU = 0.7      # patrz _segmentuj_kandydatow


def segmentuj_w_znaczniku(model, obraz_bgr, znacznik=None, przyblizaj=True, ile_propozycji=ILE_PROPOZYCJI):
    """Segmentacja znamienia tylko we wnetrzu znacznika (maska ograniczona do z.obszar).

    Modele z kadrem jak w ISIC (kadr_docelowy, np. PanDerm) nie dostaja calego wnetrza: najpierw
    propozycje.py wskazuje do ile_propozycji ciemnych plam (kandydatow), model segmentuje kazda w kadrze
    ustawionym jak w ISIC (z automatycznym przyblizeniem), a wybierany jest wynik o najwiekszym
    kontrascie brzegu (srednia ciemnosc w masce minus tuz za jej brzegiem, propozycje.kontrast_brzegu).
    Gdy nie ma kandydatow - jak dawniej: kadr = cale wnetrze i automatyczne przyblizenie.
    Wynik: WynikSegmentacji z info["znacznik"], info["metoda"]. Wyjatek BrakZnacznika, gdy nie ma znacznika."""
    z = znacznik if znacznik is not None else wykryj_znacznik(obraz_bgr)
    wynik = None
    if przyblizaj and model.kadr_docelowy and ile_propozycji:
        wynik = _segmentuj_kandydatow(model, obraz_bgr, z, ile_propozycji)
    if wynik is None:
        wynik = model.segmentuj(obraz_bgr, roi=z.roi, przyblizaj=przyblizaj, obszar=z.obszar)
        wynik.info["metoda"] = "kadr = cale wnetrze znacznika"
    wynik.info["znacznik"] = z
    return wynik


def _segmentuj_kandydatow(model, obraz_bgr, z, ile):
    from .interfejs import _iou_prostokatow
    from .propozycje import kontrast_brzegu, mapa_ciemnosci, propozycje
    mapa = mapa_ciemnosci(obraz_bgr, z)
    kandydaci = propozycje(obraz_bgr, z, ile, mapa)
    H, W = obraz_bgr.shape[:2]
    najlepszy, czas, oceny = None, 0.0, []
    for i, (maska_k, ocena) in enumerate(kandydaci):
        kadr, kadry, przebiegi = model._kadr_wokol(maska_k, (H, W)), [], []
        for _ in range(model.max_przebiegow):          # automatyczne przyblizanie jak w model.segmentuj
            wy = model._jeden_przebieg(obraz_bgr, kadr, z.obszar)
            czas += wy.czas_s
            kadry.append(kadr)
            if not wy.maska.any():
                break
            wy.info["kontrast"] = kontrast_brzegu(mapa, wy.maska)
            przebiegi.append(wy)
            nowy = model._kadr_wokol(wy.maska, (H, W))
            if _iou_prostokatow(nowy, kadr) > 0.9:
                break
            kadr = nowy
        if not przebiegi:
            continue
        # zostaje ostatni przebieg; gdy przyblizanie "odplynelo" na skore (kontrast spadl ponizej
        # SPADEK_KONTRASTU najlepszego przebiegu) - przebieg o najwiekszym kontrascie brzegu
        wyn_k, maks = przebiegi[-1], max(przebiegi, key=lambda r: r.info["kontrast"])
        if wyn_k.info["kontrast"] < SPADEK_KONTRASTU * maks.info["kontrast"]:
            wyn_k = maks
        wyn_k.info.update(kandydat=i, ocena_kandydata=ocena, kadry=kadry)
        oceny.append(round(wyn_k.info["kontrast"], 1))
        if najlepszy is None or wyn_k.info["kontrast"] > najlepszy.info["kontrast"]:
            najlepszy = wyn_k
    if najlepszy is not None:
        najlepszy.czas_s = czas
        najlepszy.info["metoda"] = (f"kandydat {najlepszy.info['kandydat'] + 1} z {len(kandydaci)} "
                                    f"(kontrast brzegu: {', '.join(map(str, oceny))})")
    return najlepszy


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
