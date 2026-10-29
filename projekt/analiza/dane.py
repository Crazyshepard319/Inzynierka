"""Dane par z dane/pary/N/: informacje z bazy SQLite albo plikow mapowania i znamiona.csv, adnotacje z CVAT
oraz surowa intensywnosc termowizji z nagrania .SEQ."""
import csv
import json
from dataclasses import dataclass, field
from pathlib import Path

import cv2
import numpy as np

INZ = Path(__file__).resolve().parents[2]          # folder Inzynierka
DANE = INZ / "dane"
PARY = DANE / "pary"


def imread(sciezka, flagi=cv2.IMREAD_COLOR):
    """cv2.imread odporny na polskie znaki w sciezce (Windows); None, gdy brak pliku."""
    try:
        bufor = np.fromfile(str(sciezka), dtype=np.uint8)
    except OSError:
        return None
    return cv2.imdecode(bufor, flagi) if bufor.size else None


def _csv(nazwa):
    p = DANE / nazwa
    if not p.exists():
        return []
    with open(p, encoding="utf-8-sig") as f:
        return list(csv.DictReader(f, delimiter=";"))


def dostepne_pary():
    """Numery par, ktore maja rgb.jpg i termal.jpg (rosnaco)."""
    if not PARY.is_dir():
        return []
    return sorted(int(k.name) for k in PARY.iterdir()
                  if k.name.isdigit() and (k / "rgb.jpg").exists() and (k / "termal.jpg").exists())


NAGRANIA = DANE / "Termowizja"               # nagrania .SEQ par (nazwy w mapowanie_dane_termowizja.csv)
PLIK_SUROWYCH = "termal_surowe.npy"          # dane/pary/N/: surowe wartosci detektora (temperatury_par.py)


def nagranie_seq(termowizja, nazwa_nagrania=None):
    """Nagranie .SEQ obrazu termowizyjnego: dane/Termowizja/<nazwa_nagrania> (para z bazy, nazwa z mapowania)
    albo plik .seq/.SEQ o tej samej nazwie obok obrazu (wlasne pliki). None, gdy nie ma."""
    kandydaci = [NAGRANIA / nazwa_nagrania] if nazwa_nagrania else []
    t = Path(termowizja)
    kandydaci += [t.with_suffix(".SEQ"), t.with_suffix(".seq")]
    return next((p for p in kandydaci if p.is_file()), None)


def intensywnosc_surowa(termowizja, para=None, nazwa_nagrania=None):
    """Surowe wartosci detektora (uint16) z pierwszej klatki nagrania .SEQ, piksel w piksel jak obraz
    termowizyjny (te same poprawki odczytu co read_flirpy.wczytaj_klatki: obciete wiersze telemetrii,
    przesuniecie kolumn). Para z bazy: dane/pary/N/termal_surowe.npy (bez flirpy); inaczej odczyt nagrania
    biblioteka flirpy. Zwraca (tablica albo None, zrodlo albo powod braku - tekst)."""
    if para is not None and (PARY / str(para) / PLIK_SUROWYCH).is_file():
        return np.load(PARY / str(para) / PLIK_SUROWYCH), f"dane/pary/{para}/{PLIK_SUROWYCH}"
    seq = nagranie_seq(termowizja, nazwa_nagrania)
    if seq is None:
        return None, "brak nagrania .SEQ do tego obrazu"
    try:
        from read_flirpy import wczytaj_klatki          # wymaga flirpy (srodowisko aplikacji)
    except ImportError as e:
        return None, f"nie mozna odczytac {seq.name}: brak biblioteki ({e.name})"
    return np.rint(wczytaj_klatki(seq, 1)[0]).astype(np.uint16), seq.name


def info_pary(n):
    """Oryginalne nazwy plikow, data zdjecia, numer znamienia i fold - z bazy SQLite (dane/baza.sqlite),
    gdy para jest w bazie, a inaczej z plikow CSV (mapowanie_*.csv, znamiona.csv)."""
    if (DANE / "baza.sqlite").exists():
        try:
            from .baza import Baza
            with Baza(utworz=False) as b:
                info = b.info_pary(n)
            if info is not None:
                return info
        except Exception:                                    # noqa: BLE001 - baza niedostepna: pliki CSV
            pass
    info = {}
    for r in _csv("mapowanie_dane_RGB.csv"):
        if r["plik"] == f"{n}.jpg":
            info.update(rgb_oryginal=r["oryginal"], rgb_data=r["data_wykonania"])
    for r in _csv("mapowanie_dane_termowizja.csv"):
        if r["plik"] == f"{n}.jpg":
            info.update(termal_nagranie=r["nagranie"])
    for r in _csv("znamiona.csv"):
        if r["para"] == str(n):
            info.update(znamie=int(r["znamie"]), fold=int(r["fold"]))
    return info


def wzorzec_pary(n):
    """Adnotacje z CVAT (wzorzec ręczny) albo None, gdy para nie jest oznaczona."""
    k = PARY / str(n)
    if not (k / "narozniki.json").exists():
        return None
    nar = json.loads((k / "narozniki.json").read_text(encoding="utf-8"))
    szary = lambda nazwa: imread(k / nazwa, cv2.IMREAD_GRAYSCALE)
    return {
        "maska_znamie_rgb": szary("maska_znamie_rgb.png"),
        "maska_znacznik_rgb": szary("maska_znacznik_rgb.png"),
        "maska_znacznik_termal": szary("maska_znacznik_termal.png"),
        "narozniki_rgb": np.array(nar["rgb"]["punkty_px"], np.float64),
        "narozniki_termal": np.array(nar["termowizja"]["punkty_px"], np.float64),
        "H_rgb": np.array(nar["rgb"]["homografia_px_na_mm"], np.float64),
        "H_termal": np.array(nar["termowizja"]["homografia_px_na_mm"], np.float64),
        "rms_rgb_mm": nar["rgb"].get("rms_mm"),
        "rms_termal_mm": nar["termowizja"].get("rms_mm"),
    }


@dataclass
class Para:
    n: int
    katalog: Path
    rgb: np.ndarray                  # BGR, zdjecie z telefonu
    termal: np.ndarray               # BGR, obraz termowizyjny z paleta (podglad)
    T: np.ndarray                    # °C, float32, piksel w piksel jak termal
    maska_znamie_rgb: np.ndarray     # uint8 0/255, wzorzec z CVAT
    maska_znacznik_rgb: np.ndarray
    maska_znacznik_termal: np.ndarray
    narozniki_rgb: np.ndarray        # 8 x 2 px, kolejnosc wzorca
    narozniki_termal: np.ndarray
    H_rgb: np.ndarray                # homografia px -> mm (plaszczyzna znacznika)
    H_termal: np.ndarray
    info: dict = field(default_factory=dict)


def wczytaj_pare(n):
    """Cala para naraz (obrazy, mapa °C, adnotacje) - np. do analiz wsadowych w notatniku."""
    k = PARY / str(n)
    wz = wzorzec_pary(n)
    if wz is None:
        raise FileNotFoundError(f"Para {n} nie ma adnotacji z CVAT (brak {k / 'narozniki.json'})")
    return Para(
        n=n, katalog=k, rgb=imread(k / "rgb.jpg"), termal=imread(k / "termal.jpg"),
        T=np.load(k / "termal_C.npy"),
        maska_znamie_rgb=wz["maska_znamie_rgb"], maska_znacznik_rgb=wz["maska_znacznik_rgb"],
        maska_znacznik_termal=wz["maska_znacznik_termal"],
        narozniki_rgb=wz["narozniki_rgb"], narozniki_termal=wz["narozniki_termal"],
        H_rgb=wz["H_rgb"], H_termal=wz["H_termal"], info={"para": n, **info_pary(n)})
