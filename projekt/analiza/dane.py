"""Wczytanie pary z dane/pary/N/ wraz z informacjami z plikow mapowania i znamiona.csv."""
import csv
import json
from dataclasses import dataclass, field
from pathlib import Path

import cv2
import numpy as np

INZ = Path(__file__).resolve().parents[2]          # folder Inzynierka
DANE = INZ / "dane"


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


def _csv(nazwa):
    p = DANE / nazwa
    if not p.exists():
        return []
    with open(p, encoding="utf-8-sig") as f:
        return list(csv.DictReader(f, delimiter=";"))


def wczytaj_pare(n):
    k = DANE / "pary" / str(n)
    wczyt = lambda nazwa, f=cv2.IMREAD_COLOR: cv2.imread(str(k / nazwa), f)
    nar = json.loads((k / "narozniki.json").read_text(encoding="utf-8"))
    info = {"para": n}
    for r in _csv("mapowanie_dane_RGB.csv"):
        if r["plik"] == f"{n}.jpg":
            info.update(rgb_oryginal=r["oryginal"], rgb_data=r["data_wykonania"])
    for r in _csv("mapowanie_dane_termowizja.csv"):
        if r["plik"] == f"{n}.jpg":
            info.update(termal_nagranie=r["nagranie"])
    for r in _csv("znamiona.csv"):
        if r["para"] == str(n):
            info.update(znamie=int(r["znamie"]), fold=int(r["fold"]))
    return Para(
        n=n, katalog=k, rgb=wczyt("rgb.jpg"), termal=wczyt("termal.jpg"),
        T=np.load(k / "termal_C.npy"),
        maska_znamie_rgb=wczyt("maska_znamie_rgb.png", cv2.IMREAD_GRAYSCALE),
        maska_znacznik_rgb=wczyt("maska_znacznik_rgb.png", cv2.IMREAD_GRAYSCALE),
        maska_znacznik_termal=wczyt("maska_znacznik_termal.png", cv2.IMREAD_GRAYSCALE),
        narozniki_rgb=np.array(nar["rgb"]["punkty_px"]), narozniki_termal=np.array(nar["termowizja"]["punkty_px"]),
        H_rgb=np.array(nar["rgb"]["homografia_px_na_mm"]), H_termal=np.array(nar["termowizja"]["homografia_px_na_mm"]),
        info=info)
