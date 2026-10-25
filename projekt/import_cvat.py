"""
Import adnotacji z CVAT (format "CVAT for images 1.1") do bazy par.

    python import_cvat.py            # dane/adnotacje/rgb.zip + termowizja.zip -> dane/pary/N/

Wejscie: eksporty zadan "RGB" (etykiety: znamię, znacznik) i "Termowizja" (znacznik); nazwy obrazow N.jpg.
Dla kazdej pary N zapisuje w dane/pary/N/:
    maska_znamie_rgb.png, maska_znacznik_rgb.png, maska_znacznik_termal.png   (uint8, 255 = obiekt)
    narozniki.json   8 naroznikow znacznika w obu obrazach, w kolejnosci wzorca (mm), + homografie px -> mm
Raporty:
    dane/adnotacje/podsumowanie.csv     pole i srednica znamienia [mm], dopasowanie naroznikow do wzorca
    wyniki/kontrola_adnotacji/N.jpg     podglad pary z konturami i numerami naroznikow
    wyniki/kontrola_adnotacji/przeglad.jpg   wszystkie pary na jednej planszy
Pliki zip nie sa zmieniane; po poprawkach w CVAT wystarczy wyeksportowac je ponownie i uruchomic import.

Wzorzec znacznika Π [mm]: belka 35, ramiona 26, szerokosc paska 9 (otwor 17 x 17 mm = 289 mm2).
Kolejnosc naroznikow wzorca (zgodnie z ruchem wskazowek zegara, belka u gory):
    0 (0,0) lewy gorny   1 (35,0) prawy gorny   2 (35,26) koniec prawego ramienia (zewn.)
    3 (26,26) koniec prawego ramienia (wewn.)    4 (26,9) wewn. naroznik prawy
    5 (9,9) wewn. naroznik lewy   6 (9,26) koniec lewego ramienia (wewn.)   7 (0,26) (zewn.)
Kolejnosc i kierunek klikniec w CVAT sa dowolne - dopasowanie do wzorca robi skrypt.
"""
import csv
import json
import re
import sys
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

import cv2
import numpy as np

INZ = Path(__file__).resolve().parent.parent
ADNOTACJE = INZ / "dane" / "adnotacje"
PARY = INZ / "dane" / "pary"
KONTROLA = INZ / "wyniki" / "kontrola_adnotacji"

BELKA, RAMIE, PASEK = 35.0, 26.0, 9.0
WZORZEC_MM = np.array([[0, 0], [BELKA, 0], [BELKA, RAMIE], [BELKA - PASEK, RAMIE], [BELKA - PASEK, PASEK],
                       [PASEK, PASEK], [PASEK, RAMIE], [0, RAMIE]], np.float64)
PROG_RMS_MM = 1.0          # dopasowanie naroznikow gorsze niz 1 mm -> do sprawdzenia
ETYKIETY = {"rgb": {"znamie": "znamie", "znacznik": "znacznik"}, "termowizja": {"znacznik": "znacznik"}}


def _bez_ogonkow(s):
    return s.translate(str.maketrans("ąćęłńóśźżĄĆĘŁŃÓŚŹŻ", "acelnoszzACELNOSZZ")).strip().lower()


def wczytaj_cvat(sciezka):
    """{nazwa_obrazu: {"rozmiar": (w, h), "ksztalty": [(etykieta, np.array Nx2), ...]}}"""
    sciezka = Path(sciezka)
    if sciezka.suffix.lower() == ".zip":
        with zipfile.ZipFile(sciezka) as z:
            nazwa = next(n for n in z.namelist() if n.endswith("annotations.xml"))
            korzen = ET.fromstring(z.read(nazwa))
    else:
        korzen = ET.parse(sciezka).getroot()
    wynik = {}
    for im in korzen.iter("image"):
        ksztalty = []
        for el in im:
            et = _bez_ogonkow(el.get("label", ""))
            if el.tag in ("polygon", "polyline"):
                pkt = np.array([[float(v) for v in p.split(",")] for p in el.get("points").split(";")])
                ksztalty.append((et, el.tag, pkt))
            elif el.tag == "mask":            # pedzel: RLE w ramce left/top/width/height
                ksztalty.append((et, "mask", el))
            else:
                ksztalty.append((et, el.tag, None))
        wynik[Path(im.get("name")).name] = {"rozmiar": (int(im.get("width")), int(im.get("height"))),
                                            "ksztalty": ksztalty}
    return wynik


def rasteryzuj(ksztalt, rozmiar):
    w, h = rozmiar
    m = np.zeros((h, w), np.uint8)
    _, rodzaj, dane = ksztalt
    if rodzaj == "polygon":
        cv2.fillPoly(m, [np.round(dane * 16).astype(np.int32)], 255, lineType=cv2.LINE_8, shift=4)
    elif rodzaj == "mask":
        rle = [int(v) for v in dane.get("rle").split(",")]
        l, t, ww, hh = (int(float(dane.get(k))) for k in ("left", "top", "width", "height"))
        flat = np.zeros(ww * hh, np.uint8)
        poz, wart = 0, 0
        for n in rle:
            flat[poz:poz + n] = wart
            poz, wart = poz + n, 255 - wart
        m[t:t + hh, l:l + ww] = flat.reshape(hh, ww)
    return m


def _pole_ze_znakiem(p):
    x, y = p[:, 0], p[:, 1]
    return 0.5 * float(np.dot(x, np.roll(y, -1)) - np.dot(np.roll(x, -1), y))


def dopasuj_narozniki(pkt_px):
    """8 punktow z CVAT -> (punkty w kolejnosci wzorca, homografia px->mm, rms [mm]).
    Kierunek ujednolicony z wzorcem (bez odbicia), potem najlepsze z 8 przesuniec cyklicznych."""
    p = np.asarray(pkt_px, np.float64)
    if np.sign(_pole_ze_znakiem(p)) != np.sign(_pole_ze_znakiem(WZORZEC_MM)):
        p = p[::-1]
    najl = None
    for k in range(8):
        q = np.roll(p, -k, axis=0)
        H, _ = cv2.findHomography(q, WZORZEC_MM, 0)
        if H is None:
            continue
        r = cv2.perspectiveTransform(q[None], H)[0] - WZORZEC_MM
        rms = float(np.sqrt((r ** 2).sum(1).mean()))
        if najl is None or rms < najl[2]:
            najl = (q, H, rms)
    return najl


def mm_na_px(H, punkt):
    """Lokalna skala [mm/px] w punkcie: pierwiastek z wyznacznika jakobianu homografii."""
    x, y = punkt
    w = H[2, 0] * x + H[2, 1] * y + H[2, 2]
    u = (H[0, 0] * x + H[0, 1] * y + H[0, 2]) / w
    v = (H[1, 0] * x + H[1, 1] * y + H[1, 2]) / w
    J = np.array([[(H[0, 0] - u * H[2, 0]) / w, (H[0, 1] - u * H[2, 1]) / w],
                  [(H[1, 0] - v * H[2, 0]) / w, (H[1, 1] - v * H[2, 1]) / w]])
    return float(np.sqrt(abs(np.linalg.det(J))))


def podglad_pary(rgb, ter, n, kont_znamie, nar_rgb, nar_ter):
    """RGB (z konturem znamienia i naroznikami) obok termowizji (narozniki), ta sama wysokosc."""
    def rysuj(img, nar, kont, sc, gr):
        v = cv2.resize(img, None, fx=sc, fy=sc, interpolation=cv2.INTER_AREA if sc < 1 else cv2.INTER_CUBIC)
        cv2.polylines(v, [np.round(nar * sc).astype(np.int32)], True, (0, 230, 0), gr, cv2.LINE_AA)
        if kont is not None:
            cv2.polylines(v, [np.round(kont * sc).astype(np.int32)], True, (0, 0, 255), gr, cv2.LINE_AA)
        for i, (x, y) in enumerate(nar * sc):
            cv2.circle(v, (int(x), int(y)), 4, (0, 230, 0), -1, cv2.LINE_AA)
            for kol, g in (((0, 0, 0), 4), ((255, 255, 255), 1)):
                cv2.putText(v, str(i), (int(x) + 6, int(y) - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.6, kol, g, cv2.LINE_AA)
        return v
    hh = 480
    a = rysuj(rgb, nar_rgb, kont_znamie, hh / rgb.shape[0], 2)
    b = rysuj(ter, nar_ter, None, hh / ter.shape[0], 2)
    out = np.hstack([a, np.full((hh, 8, 3), 255, np.uint8), b])
    for kol, g in (((0, 0, 0), 5), ((255, 255, 255), 2)):
        cv2.putText(out, f"para {n}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.9, kol, g, cv2.LINE_AA)
    return out


def main():
    pliki = {k: next((ADNOTACJE / f"{k}{e}" for e in (".zip", ".xml") if (ADNOTACJE / f"{k}{e}").exists()), None)
             for k in ("rgb", "termowizja")}
    if None in pliki.values():
        sys.exit(f"Brak eksportow w {ADNOTACJE}: potrzebne rgb.zip i termowizja.zip (CVAT for images 1.1)")
    dane = {k: wczytaj_cvat(p) for k, p in pliki.items()}
    numery = sorted(int(p.name) for p in PARY.iterdir() if p.is_dir() and re.fullmatch(r"\d+", p.name))
    KONTROLA.mkdir(parents=True, exist_ok=True)

    problemy, wiersze, kafle = [], [], []
    for n in numery:
        katalog, nazwa = PARY / str(n), f"{n}.jpg"
        obrazy = {"rgb": cv2.imread(str(katalog / "rgb.jpg")), "termowizja": cv2.imread(str(katalog / "termal.jpg"))}
        maski, narozniki, ok = {}, {}, True
        for mod in ("rgb", "termowizja"):
            ad = dane[mod].get(nazwa)
            if ad is None:
                problemy.append(f"para {n}: brak obrazu {nazwa} w eksporcie {mod}")
                ok = False
                continue
            h, w = obrazy[mod].shape[:2]
            if ad["rozmiar"] != (w, h):
                problemy.append(f"para {n} ({mod}): rozmiar w CVAT {ad['rozmiar']} != plik {(w, h)} - inny obraz?")
                ok = False
                continue
            for et in ETYKIETY[mod]:
                ks = [k for k in ad["ksztalty"] if k[0] == et]
                if len(ks) != 1:
                    problemy.append(f"para {n} ({mod}): '{et}' wystepuje {len(ks)} razy (powinno 1)")
                    ok = False
                    continue
                if et == "znacznik":
                    if ks[0][1] != "polygon" or len(ks[0][2]) != 8:
                        ile = len(ks[0][2]) if ks[0][1] == "polygon" else ks[0][1]
                        problemy.append(f"para {n} ({mod}): znacznik ma {ile} wierzcholkow (powinno 8)")
                        ok = False
                        continue
                    pkt, H, rms = dopasuj_narozniki(ks[0][2])
                    narozniki[mod] = {"punkty_px": np.round(pkt, 2).tolist(), "homografia_px_na_mm": H.tolist(),
                                      "rms_mm": round(rms, 3), "mm_na_px": round(mm_na_px(H, pkt.mean(0)), 4)}
                    if rms > PROG_RMS_MM:
                        problemy.append(f"para {n} ({mod}): narozniki pasuja do wzorca z bledem {rms:.2f} mm "
                                        f"(> {PROG_RMS_MM}) - sprawdz polozenie wierzcholkow")
                maski[(mod, et)] = (rasteryzuj(ks[0], ad["rozmiar"]), ks[0])
        if not ok:
            continue

        cv2.imwrite(str(katalog / "maska_znamie_rgb.png"), maski[("rgb", "znamie")][0])
        cv2.imwrite(str(katalog / "maska_znacznik_rgb.png"), maski[("rgb", "znacznik")][0])
        cv2.imwrite(str(katalog / "maska_znacznik_termal.png"), maski[("termowizja", "znacznik")][0])
        (katalog / "narozniki.json").write_text(json.dumps(
            {"wzorzec_mm": WZORZEC_MM.tolist(), "rgb": narozniki["rgb"], "termowizja": narozniki["termowizja"]},
            indent=1), encoding="utf-8")

        # znamie w mm: poligon (albo kontur maski) przez homografie px -> mm
        _, rodzaj, d = maski[("rgb", "znamie")][1]
        kont = d if rodzaj == "polygon" else max(cv2.findContours(maski[("rgb", "znamie")][0], cv2.RETR_EXTERNAL,
                                                                  cv2.CHAIN_APPROX_NONE)[0], key=cv2.contourArea)[:, 0].astype(float)
        H = np.array(narozniki["rgb"]["homografia_px_na_mm"])
        kont_mm = cv2.perspectiveTransform(kont[None].astype(np.float64), H)[0]
        pole_mm2 = abs(_pole_ze_znakiem(kont_mm))
        wiersze.append({"para": n, "pole_znamienia_px": int(np.count_nonzero(maski[("rgb", "znamie")][0])),
                        "pole_znamienia_mm2": round(pole_mm2, 2),
                        "srednica_rownowazna_mm": round(2 * np.sqrt(pole_mm2 / np.pi), 2),
                        "mm_na_px_rgb": narozniki["rgb"]["mm_na_px"], "mm_na_px_termal": narozniki["termowizja"]["mm_na_px"],
                        "rms_naroznikow_rgb_mm": narozniki["rgb"]["rms_mm"],
                        "rms_naroznikow_termal_mm": narozniki["termowizja"]["rms_mm"]})
        pg = podglad_pary(obrazy["rgb"], obrazy["termowizja"], n, kont,
                          np.array(narozniki["rgb"]["punkty_px"]), np.array(narozniki["termowizja"]["punkty_px"]))
        cv2.imwrite(str(KONTROLA / f"{n}.jpg"), pg, [cv2.IMWRITE_JPEG_QUALITY, 90])
        kafle.append(cv2.resize(pg, (pg.shape[1] * 200 // pg.shape[0], 200), interpolation=cv2.INTER_AREA))

    if wiersze:
        with open(ADNOTACJE / "podsumowanie.csv", "w", newline="", encoding="utf-8-sig") as f:
            wr = csv.DictWriter(f, fieldnames=list(wiersze[0]), delimiter=";")
            wr.writeheader()
            wr.writerows(wiersze)
    if kafle:
        sz = max(k.shape[1] for k in kafle)
        kafle = [cv2.copyMakeBorder(k, 2, 2, 2, sz - k.shape[1] + 2, cv2.BORDER_CONSTANT, value=(255, 255, 255)) for k in kafle]
        kol = 6
        kafle += [np.full_like(kafle[0], 255)] * (-len(kafle) % kol)
        cv2.imwrite(str(KONTROLA / "przeglad.jpg"),
                    np.vstack([np.hstack(kafle[i:i + kol]) for i in range(0, len(kafle), kol)]),
                    [cv2.IMWRITE_JPEG_QUALITY, 85])
    (KONTROLA / "problemy.txt").write_text("\n".join(problemy) or "brak", encoding="utf-8")

    print(f"Pary: {len(numery)}, zaimportowane: {len(wiersze)}, problemy: {len(problemy)}")
    for p in problemy:
        print("  -", p)
    if wiersze:
        a = np.array([w["pole_znamienia_mm2"] for w in wiersze])
        d = np.array([w["srednica_rownowazna_mm"] for w in wiersze])
        r1 = np.array([w["rms_naroznikow_rgb_mm"] for w in wiersze])
        r2 = np.array([w["rms_naroznikow_termal_mm"] for w in wiersze])
        print(f"Znamie: pole {np.median(a):.1f} mm2 (mediana; {a.min():.1f}-{a.max():.1f}), "
              f"srednica rown. {np.median(d):.2f} mm ({d.min():.2f}-{d.max():.2f})")
        print(f"Narozniki vs wzorzec 35x26 mm: RMS RGB {np.median(r1):.2f} mm (max {r1.max():.2f}), "
              f"termowizja {np.median(r2):.2f} mm (max {r2.max():.2f})")
        print(f"Wyniki: {PARY}/N/, {ADNOTACJE / 'podsumowanie.csv'}, podglady: {KONTROLA}")


if __name__ == "__main__":
    main()
