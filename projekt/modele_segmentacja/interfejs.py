"""
Wspolny interfejs modeli segmentacji znamion.

Kazdy model to podklasa ModelSegmentacji, ktora implementuje tylko
_prawdopodobienstwo(wycinek_bgr). Reszta (wycinanie obszaru, progowanie,
wklejanie maski z powrotem, pomiar czasu) jest wspolna, wiec aplikacja
uzywa kazdego modelu tak samo:

    model = wczytaj_model("panderm_upernet")
    wynik = model.segmentuj(obraz_bgr, roi=(x, y, w, h))
    wynik.maska            # uint8 0/255, rozmiar calego obrazu

Obszar ze znacznika (wnetrze ㄇ) - patrz znacznik.py:

    from modele_segmentacja.znacznik import segmentuj_w_znaczniku
    wynik = segmentuj_w_znaczniku(model, obraz_bgr)
"""
import time
from dataclasses import dataclass, field

import cv2
import numpy as np


@dataclass
class WynikSegmentacji:
    maska: np.ndarray                    # uint8 0/255, rozmiar obrazu wejsciowego
    prawdopodobienstwo: np.ndarray       # float32 0..1, rozmiar obrazu (0 poza ROI)
    roi: tuple                           # (x, y, w, h) analizowany obszar
    czas_s: float                        # czas samej segmentacji (bez wczytania wag)
    model: str                           # klucz modelu
    info: dict = field(default_factory=dict)


class ModelSegmentacji:
    klucz = ""                 # identyfikator = nazwa folderu w modele/
    nazwa = ""                 # nazwa wyswietlana w aplikacji
    opis = ""
    najwieksza_skladowa = True # zostaw tylko najwieksza spojna skladowa (jak u autorow PanDerm)
    prog = 0.5
    # Automatyczne przyblizenie (dla modeli uczonych na zdjeciach dermatoskopowych):
    # po znalezieniu znamienia kadr jest ustawiany tak, by znamie zajmowalo w nim
    # tyle, co w danych uczacych, i segmentacja jest powtarzana. None = wylaczone.
    kadr_docelowy = None       # dluzszy bok ramki znamienia / bok kadru (ISIC 2018: mediana 0.53)
    proporcje_kadru = 1.0      # szerokosc / wysokosc kadru (ISIC 2018: mediana 1.5)
    max_przebiegow = 3
    # Gdy podano obszar (wnetrze znacznika): piksele poza nim (jasna folia) zastepowane sa
    # mediana koloru skory z obszaru, zeby model nie widzial skory jako ciemnej plamy
    # otoczonej jasna ramka (w ISIC tak wyglada znamie na skorze).
    wypelniaj_poza_obszarem = True

    def __init__(self):
        self._wczytany = False

    # ── do nadpisania w modelu ──────────────────────────────────────────────
    def dostepnosc(self):
        """(True, "") gdy model mozna uruchomic, inaczej (False, powod)."""
        return True, ""

    def _wczytaj(self):
        """Wczytanie wag itp. Wolane raz, przy pierwszej segmentacji."""

    def _prawdopodobienstwo(self, wycinek_bgr):
        """Zwraca mape prawdopodobienstwa znamienia (float32 0..1) w rozmiarze wycinka."""
        raise NotImplementedError

    def nieaktualny(self):
        """True, gdy wczytane wagi sa starsze niz na dysku (np. trening zapisal nowsze)."""
        return False

    # ── wspolne ─────────────────────────────────────────────────────────────
    def wczytaj(self):
        if not self._wczytany or self.nieaktualny():
            ok, powod = self.dostepnosc()
            if not ok:
                raise RuntimeError(f"Model {self.nazwa} niedostepny: {powod}")
            self._wczytaj()
            self._wczytany = True
        return self

    def segmentuj(self, obraz_bgr, roi=None, przyblizaj=True, obszar=None):
        """obraz_bgr: caly obraz (BGR, uint8); roi: (x, y, w, h) albo None = caly obraz.
        przyblizaj: automatyczne przyblizenie do znamienia (gdy model ma kadr_docelowy).
        obszar: maska uint8 rozmiaru obrazu (np. wnetrze znacznika) - maska znamienia
        jest do niej ograniczana w kazdym przebiegu, takze po przyblizeniu."""
        self.wczytaj()
        H, W = obraz_bgr.shape[:2]
        x, y, w, h = roi if roi is not None else (0, 0, W, H)
        x, y = max(0, int(x)), max(0, int(y))
        w, h = min(W - x, int(w)), min(H - y, int(h))
        if w < 8 or h < 8:
            raise ValueError("Zaznaczony obszar jest za maly")

        wynik = self._jeden_przebieg(obraz_bgr, (x, y, w, h), obszar)
        kadry, czas = [wynik.roi], wynik.czas_s
        if przyblizaj and self.kadr_docelowy:
            for _ in range(self.max_przebiegow - 1):
                if not wynik.maska.any():
                    break
                kadr = self._kadr_wokol(wynik.maska, (H, W))
                if _iou_prostokatow(kadr, kadry[-1]) > 0.9:      # kadr sie ustabilizowal
                    break
                nowy = self._jeden_przebieg(obraz_bgr, kadr, obszar)
                czas += nowy.czas_s
                if not nowy.maska.any():
                    break
                wynik = nowy
                kadry.append(kadr)
        wynik.czas_s = czas
        wynik.info["kadry"] = kadry
        return wynik

    def _jeden_przebieg(self, obraz_bgr, roi, obszar=None):
        H, W = obraz_bgr.shape[:2]
        x, y, w, h = roi
        t0 = time.perf_counter()
        wycinek = obraz_bgr[y:y + h, x:x + w]
        if obszar is not None and self.wypelniaj_poza_obszarem:
            wycinek = wypelnij_poza_obszarem(wycinek, obszar[y:y + h, x:x + w])
        p = self._prawdopodobienstwo(wycinek)
        czas = time.perf_counter() - t0
        m = (p > self.prog).astype(np.uint8) * 255
        if obszar is not None:                        # np. tylko wnetrze znacznika
            m[obszar[y:y + h, x:x + w] == 0] = 0
        if self.najwieksza_skladowa:
            m = najwieksza_skladowa(m)
        maska = np.zeros((H, W), np.uint8)
        maska[y:y + h, x:x + w] = m
        prawd = np.zeros((H, W), np.float32)
        prawd[y:y + h, x:x + w] = p
        return WynikSegmentacji(maska, prawd, (x, y, w, h), czas, self.klucz)

    def _kadr_wokol(self, maska, ksztalt):
        """Kadr o proporcjach proporcje_kadru, w ktorym znamie zajmuje kadr_docelowy
        dluzszego boku po przeskalowaniu do wejscia modelu (jak w danych uczacych)."""
        H, W = ksztalt
        x, y, w, h = cv2.boundingRect(maska)
        a = self.proporcje_kadru
        kh = max(w / a, h) / self.kadr_docelowy
        kw = a * kh
        kw, kh = min(W, max(16, int(round(kw)))), min(H, max(16, int(round(kh))))
        kx = int(np.clip(x + w / 2 - kw / 2, 0, W - kw))      # przesun, by zmiescic sie w obrazie
        ky = int(np.clip(y + h / 2 - kh / 2, 0, H - kh))
        return kx, ky, kw, kh


# ── narzedzia ────────────────────────────────────────────────────────────────

def _iou_prostokatow(a, b):
    ax, ay, aw, ah = a
    bx, by, bw, bh = b
    iw = max(0, min(ax + aw, bx + bw) - max(ax, bx))
    ih = max(0, min(ay + ah, by + bh) - max(ay, by))
    wsp = iw * ih
    return wsp / (aw * ah + bw * bh - wsp)


def wypelnij_poza_obszarem(wycinek_bgr, maska):
    """Piksele wycinka poza maska (np. folia znacznika) -> mediana koloru pikseli w masce."""
    w = maska > 0
    if w.all() or not w.any():
        return wycinek_bgr
    out = wycinek_bgr.copy()
    out[~w] = np.median(wycinek_bgr[w], axis=0).astype(np.uint8)
    return out


def wczytaj_obraz(sciezka, flagi=cv2.IMREAD_COLOR):
    """cv2.imread odporny na polskie znaki w sciezce (Windows). None gdy brak pliku."""
    try:
        dane = np.fromfile(str(sciezka), dtype=np.uint8)
    except OSError:
        return None
    return cv2.imdecode(dane, flagi) if dane.size else None


def zapisz_obraz(sciezka, img):
    """cv2.imwrite odporny na polskie znaki w sciezce (Windows)."""
    from pathlib import Path
    ok, buf = cv2.imencode(Path(sciezka).suffix or ".png", img)
    if ok:
        buf.tofile(str(sciezka))
    return ok


def najwieksza_skladowa(maska):
    """Najwieksza spojna skladowa maski binarnej (odpowiednik largestConnectComponent)."""
    n, lab, st, _ = cv2.connectedComponentsWithStats((maska > 0).astype(np.uint8), connectivity=8)
    if n <= 2:
        return maska
    j = 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA]))
    return (lab == j).astype(np.uint8) * 255


def metryki(maska, wzorzec):
    """Porownanie maski z maska wzorcowa (obie: niezerowe = znamie)."""
    a, b = maska > 0, wzorzec > 0
    tp = np.count_nonzero(a & b)
    fp = np.count_nonzero(a & ~b)
    fn = np.count_nonzero(~a & b)
    return {
        "dice": 2 * tp / (2 * tp + fp + fn) if (tp + fp + fn) else 1.0,
        "iou": tp / (tp + fp + fn) if (tp + fp + fn) else 1.0,
        "precyzja": tp / (tp + fp) if (tp + fp) else 0.0,
        "czulosc": tp / (tp + fn) if (tp + fn) else 0.0,
    }


def maska_w_termalu(maska_rgb, macierz, ksztalt_termalu):
    """Przenosi maske znamienia ze zdjecia RGB do obrazu termalnego.
    macierz: 3x3 z pliku *_macierz.txt (piksel RGB -> piksel termalny),
    ksztalt_termalu: (wysokosc, szerokosc). Zwraca uint8 0/255."""
    h, w = ksztalt_termalu[:2]
    m = cv2.warpPerspective(maska_rgb.astype(np.float32), np.asarray(macierz, float), (w, h),
                            flags=cv2.INTER_LINEAR)
    return (m > 127).astype(np.uint8) * 255
