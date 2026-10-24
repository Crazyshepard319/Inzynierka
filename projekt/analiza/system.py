"""
Etapy systemu dla jednej pary RGB - termowizja (schemat "Projekt systemu" w planie pracy).
Ten sam kod wykonuje aplikacja (aplikacja.py, krok po kroku) i potok wsadowy (potok_pary.py).

  1. Wejscie        Analiza(zdjecie, termowizja) albo Analiza.z_pary(n); dla par z bazy takze
                    wzorzec reczny z CVAT (maski, narozniki znacznika)
  2. Rejestracja    rejestruj()          macierz T: piksel RGB -> piksel termowizji (dopasowanie3.py;
                                         znacznik wykrywany automatycznie, adnotacje NIE sa uzywane)
  3. Segmentacja    ustaw_narozniki()    8 naroznikow znacznika 35 x 26 mm -> homografia px -> mm
                                         (CVAT albo automatycznie: wzorzec Π dopasowany do maski znacznika)
                    znamie_z_*()         maska znamienia na zdjeciu (CVAT, plik/PanDerm, obrys reczny)
  4. Przeniesienie  przenies()           znamie i znacznik: zdjecie -> termowizja (T)
                    z_termowizji()       obszar zaznaczony na termowizji -> zdjecie (T^-1)
  5. Pomiary        zmierz()             wymiary w mm i kolor znamienia, kontrola skali, zgodnosc
                                         z wzorcem z CVAT (badanie E1) i segmentacji znamienia z CVAT
  6. Raport         zapisz_raport()      raport.html + metryki.json + obrazy PNG

Temperatury (mapa °C z SEQ, dane/pary/N/termal_C.npy) nie sa czescia raportu - funkcja
pomiary.parametry_termiczne zostaje do ewentualnego uzycia.
"""
import contextlib
import io
import json
import re
import sys
from pathlib import Path

import cv2
import numpy as np

PROJEKT = Path(__file__).resolve().parents[1]
if str(PROJEKT) not in sys.path:
    sys.path.insert(0, str(PROJEKT))

import dopasowanie3 as dop                                  # noqa: E402
import import_cvat as cvat                                  # noqa: E402
from . import geometria as geo, miary, obrazy, pomiary, raport   # noqa: E402
from .dane import DANE, INZ, PARY, imread, info_pary, wzorzec_pary   # noqa: E402

GESTOSC = 4      # przeniesione obszary w siatce termowizji 4x gestszej (dokladnosc pola ~1%)
POLE_OTWORU_MM2 = (cvat.BELKA - 2 * cvat.PASEK) * (cvat.RAMIE - cvat.PASEK)     # 15 x 16 = 240 mm2
MODELE_REJESTRACJI = ("auto", "afiniczna", "homografia")
ZRODLA_NAROZNIKOW = {"cvat": "adnotacja z CVAT",
                     "auto": "automatycznie (wzorzec Π dopasowany do maski znacznika z rejestracji)"}
ZRODLA_ZNAMIENIA = {"cvat": "adnotacja z CVAT", "plik": "maska z pliku",
                    "obrys": "obrys zaznaczony ręcznie", "panderm": "PanDerm (model M1)"}
ETAPY = ("wejscie", "rejestracja", "segmentacja", "przeniesienie", "pomiary", "raport")


class BladEtapu(RuntimeError):
    """Etapu nie da sie wykonac (brak wyniku poprzedniego etapu, zle dane) - tresc dla uzytkownika."""


class _Tee(io.TextIOBase):
    def __init__(self, *cele):
        self.cele = cele

    def write(self, t):
        for c in self.cele:
            c.write(t)
        return len(t)

    def flush(self):
        for c in self.cele:
            with contextlib.suppress(Exception):
                c.flush()


def para_z_plikow(zdjecie, termowizja):
    """Numer pary, gdy wybrano dane/pary/N/{rgb,termal}.jpg albo dane/dane_RGB/N.jpg z dane_termowizja/N.jpg."""
    r, t = Path(zdjecie).resolve(), Path(termowizja).resolve()
    if r.parent == t.parent and r.parent.parent == PARY.resolve() and (r.name, t.name) == ("rgb.jpg", "termal.jpg"):
        n = r.parent.name
    elif (r.parent == (DANE / "dane_RGB").resolve() and t.parent == (DANE / "dane_termowizja").resolve()
          and r.stem == t.stem):
        n = r.stem
    else:
        return None
    return int(n) if n.isdigit() and (PARY / n).is_dir() else None


def narozniki_wzorca(maska, homografia=True):
    """8 naroznikow znacznika z jego maski: wzorzec Π (35 x 26 mm, pasek 10 mm) dopasowany do maski.
    Najpierw podobienstwo (srodek, skala z pola, kat z przeszukania 360°), potem ECC na rozmytych
    maskach: afiniczne i homografia (jak w dopasowanie3.py). Caly ksztalt ustala polozenie naroznikow,
    wiec postrzepiona krawedz maski (wlosy, odblaski) przesuwa je mniej niz przy szukaniu rogow konturu.
    Zwraca (narozniki 8 x 2 w px maski, IoU dopasowanego wzorca z maska)."""
    m = (np.asarray(maska) > 0).astype(np.uint8) * 255
    if cv2.countNonZero(m) < 50:
        raise BladEtapu("maska znacznika jest pusta albo za mala")
    R = np.sqrt(cv2.countNonZero(m) / cv2.contourArea(cvat.WZORZEC_MM.astype(np.float32)))   # px maski / mm
    marg = int(round(0.3 * cvat.BELKA * R))
    wz = cvat.WZORZEC_MM * R + marg
    t = np.zeros((int(np.ceil(cvat.RAMIE * R)) + 2 * marg, int(np.ceil(cvat.BELKA * R)) + 2 * marg), np.uint8)
    cv2.fillPoly(t, [np.round(wz * 16).astype(np.int32)], 255, cv2.LINE_AA, 4)
    with contextlib.redirect_stdout(io.StringIO()):
        W, _, _ = dop._podobienstwo(t, m)
        tf, mf = t.astype(np.float32) / 255, m.astype(np.float32) / 255
        W = dop._ecc(tf, mf, W, 1.0, cv2.MOTION_AFFINE, (6.0, 3.0, 1.5))
        if homografia:
            W = dop._ecc(tf, mf, W, 1.0, cv2.MOTION_HOMOGRAPHY, (3.0, 1.5))
    pkt = cv2.perspectiveTransform(wz[None], W / W[2, 2])[0]
    dopas = np.zeros_like(m)
    cv2.fillPoly(dopas, [np.round(pkt * 16).astype(np.int32)], 255, cv2.LINE_8, 4)
    iou = np.count_nonzero((dopas > 0) & (m > 0)) / max(1, np.count_nonzero((dopas > 0) | (m > 0)))
    return pkt, float(iou)


def _pole_wielokata_mm2(pkt_px, H_mm):
    q = cv2.perspectiveTransform(np.asarray(pkt_px, np.float64)[None], np.asarray(H_mm, np.float64))[0]
    return abs(float(cv2.contourArea(q.astype(np.float32))))


def bez_tablic(x):
    """Wyniki bez tablic numpy i kluczy prywatnych (_...) - do metryki.json."""
    if isinstance(x, dict):
        return {k: bez_tablic(v) for k, v in x.items() if not str(k).startswith("_")}
    if isinstance(x, (list, tuple)):
        return [bez_tablic(v) for v in x]
    if isinstance(x, np.ndarray):
        return x.tolist()
    if isinstance(x, (np.floating, np.integer, np.bool_)):
        return x.item()
    return x


class Analiza:
    """Stan analizy jednej pary; kazda metoda to jeden etap systemu (patrz opis modulu)."""

    def __init__(self, zdjecie, termowizja, para=None, folder=None):
        self.rgb_path, self.ter_path = Path(zdjecie), Path(termowizja)
        self.rgb = imread(self.rgb_path)
        self.termal = imread(self.ter_path)
        if self.rgb is None:
            raise BladEtapu(f"Nie można otworzyć zdjęcia: {self.rgb_path}")
        if self.termal is None:
            raise BladEtapu(f"Nie można otworzyć obrazu termowizyjnego: {self.ter_path}")
        self.para = para if para is not None else para_z_plikow(self.rgb_path, self.ter_path)
        self.info = {"para": self.para, "zdjecie": self.rgb_path.name, "termowizja": self.ter_path.name}
        self.wzorzec = None
        if self.para is not None:
            self.info.update(info_pary(self.para))
            self.wzorzec = wzorzec_pary(self.para)
            if self.wzorzec is not None and (self.wzorzec["maska_znamie_rgb"] is None or
                                             self.wzorzec["maska_znamie_rgb"].shape != self.rgb.shape[:2]):
                self.wzorzec = None                      # adnotacje nie pasuja do tych obrazow
        nazwa = f"para_{self.para}" if self.para is not None else f"{self.rgb_path.stem}__{self.ter_path.stem}"
        self.folder = Path(folder) if folder else INZ / "wyniki" / "wyniki_obu" / nazwa
        self.folder_rejestracji = INZ / "wyniki" / "wyniki_dopasowania" / nazwa
        self._wyczysc()

    @classmethod
    def z_pary(cls, n, folder=None):
        k = PARY / str(n)
        return cls(k / "rgb.jpg", k / "termal.jpg", para=n, folder=folder)

    # ── stan ────────────────────────────────────────────────────────────────
    def _wyczysc(self):
        """Stan poczatkowy: brak wynikow etapow 2-6."""
        self.M, self.rej = None, {}
        self.maska_znacznika_rgb = self.maska_znacznika_termal = None     # maski klasyczne z rejestracji
        self._maska_rgb_rob, self._sc = None, None
        self.narozniki_rgb = self.H_rgb = self.narozniki_termal = self.H_termal = None
        self.zrodlo_naroznikow, self.dopasowanie_naroznikow = None, {}
        self._folia_rgb = self._folia_termal = None
        self.maska_znamie, self.zrodlo_znamienia = None, None
        self.przeniesione, self.obszary_z_termowizji, self.wyniki = None, [], None
        self.ostatnie_obrazy = {}

    def _po_nowej_rejestracji(self):
        """Nowa macierz T uniewaznia przeniesienie i pomiary oraz narozniki automatyczne
        (licza sie z masek z rejestracji); maska znamienia i narozniki z CVAT zostaja."""
        if self.zrodlo_naroznikow == "auto":
            self.narozniki_rgb = self.H_rgb = self.narozniki_termal = self.H_termal = None
            self.zrodlo_naroznikow, self.dopasowanie_naroznikow = None, {}
            self._folia_rgb = self._folia_termal = None
        self.przeniesione, self.obszary_z_termowizji, self.wyniki = None, [], None

    def stan(self):
        """Ktore etapy sa wykonane (dla aplikacji)."""
        return {"wejscie": True, "rejestracja": self.M is not None,
                "segmentacja": self.maska_znamie is not None and self.H_rgb is not None,
                "przeniesienie": self.przeniesione is not None, "pomiary": self.wyniki is not None}

    @property
    def plik_wyrownany(self):
        """Termowizja w geometrii zdjecia (BGRA, alfa = pole widzenia kamery) z rejestracji."""
        return self.folder_rejestracji / "dopasowanie_termal_wyrownany.png"

    def _wymagaj(self, *co):
        braki = {"rejestracja": (self.M is None, "Najpierw wykonaj rejestrację (krok 2)."),
                 "narozniki": (self.H_rgb is None, "Najpierw wyznacz narożniki znacznika (krok 3)."),
                 "znamie": (self.maska_znamie is None, "Najpierw wyznacz znamię na zdjęciu (krok 3)."),
                 "przeniesienie": (self.przeniesione is None, "Najpierw przenieś obszary na termowizję (krok 4)."),
                 "pomiary": (self.wyniki is None, "Najpierw policz pomiary (krok 5).")}
        for c in co:
            if braki[c][0]:
                raise BladEtapu(braki[c][1])

    # ── 2. rejestracja ──────────────────────────────────────────────────────
    def rejestruj(self, model="auto", log=None):
        """Rejestracja dopasowanie3.run_registration; log: dodatkowy strumien na komunikaty (aplikacja)."""
        if model not in MODELE_REJESTRACJI:
            raise BladEtapu(f"Nieznany model rejestracji: {model}")
        kat = self.folder_rejestracji
        kat.mkdir(parents=True, exist_ok=True)
        bufor = io.StringIO()
        with contextlib.redirect_stdout(_Tee(bufor, log) if log is not None else bufor):
            dop.run_registration(self.rgb_path, self.ter_path, kat / "dopasowanie.png", model)
        (kat / "rejestracja_log.txt").write_text(bufor.getvalue(), encoding="utf-8")
        return self.wczytaj_rejestracje(model)

    def wczytaj_rejestracje(self, model=None):
        """Wynik rejestracji zapisany wczesniej w folderze_rejestracji (bez liczenia od nowa)."""
        kat = self.folder_rejestracji
        if not (kat / "dopasowanie_macierz.txt").exists():
            raise BladEtapu(f"Brak zapisanej rejestracji w {kat}")
        self._po_nowej_rejestracji()
        log = (kat / "rejestracja_log.txt").read_text(encoding="utf-8") if (kat / "rejestracja_log.txt").exists() else ""
        self.M = np.loadtxt(kat / "dopasowanie_macierz.txt")
        try:
            folder = kat.resolve().relative_to(INZ.resolve()).as_posix()
        except ValueError:
            folder = str(kat)
        rej = {"macierz_T": self.M.tolist(), "folder": folder}
        if model:
            rej["model_zadany"] = model
        if m := re.search(r"=> wybrany model: (\w+)", log):
            rej["model"] = m.group(1)
        if m := re.findall(r"Dice=([\d.]+)\s+sredni blad krawedzi=([\d.]+) px termal \(", log):
            rej["dice_wewnetrzny"], rej["blad_krawedzi_px"] = float(m[-1][0]), float(m[-1][1])
        self.rej = rej
        m = imread(kat / "dopasowanie_maska_rgb.png", cv2.IMREAD_GRAYSCALE)
        self.maska_znacznika_termal = imread(kat / "dopasowanie_maska_termal.png", cv2.IMREAD_GRAYSCALE)
        if m is not None:
            H0, W0 = self.rgb.shape[:2]
            self._maska_rgb_rob, self._sc = m, m.shape[1] / W0
            self.maska_znacznika_rgb = (cv2.resize(m, (W0, H0), interpolation=cv2.INTER_LINEAR) > 127).astype(np.uint8) * 255
        return rej

    # ── 3. segmentacja: znacznik (skala mm) i znamie ────────────────────────
    def ustaw_narozniki(self, zrodlo="cvat"):
        """Narozniki znacznika na zdjeciu i termowizji oraz homografie px -> mm."""
        if zrodlo == "cvat":
            if self.wzorzec is None:
                raise BladEtapu("Te obrazy nie mają adnotacji z CVAT - wybierz narożniki automatyczne.")
            wz = self.wzorzec
            self.narozniki_rgb, self.H_rgb = wz["narozniki_rgb"], wz["H_rgb"]
            self.narozniki_termal, self.H_termal = wz["narozniki_termal"], wz["H_termal"]
            self._folia_rgb, self._folia_termal = wz["maska_znacznik_rgb"], wz["maska_znacznik_termal"]
            self.dopasowanie_naroznikow = {"rgb_rms_mm": wz["rms_rgb_mm"], "termal_rms_mm": wz["rms_termal_mm"]}
        elif zrodlo == "auto":
            self._wymagaj("rejestracja")
            if self._maska_rgb_rob is None or self.maska_znacznika_termal is None:
                raise BladEtapu("Brak masek znacznika z rejestracji - uruchom rejestrację ponownie.")
            k, iou = narozniki_wzorca(self._maska_rgb_rob)
            q, H, _ = cvat.dopasuj_narozniki(k / self._sc)
            kt, iou_t = narozniki_wzorca(self.maska_znacznika_termal)
            qt, Ht, _ = cvat.dopasuj_narozniki(kt)
            self.narozniki_rgb, self.H_rgb, self.narozniki_termal, self.H_termal = q, H, qt, Ht
            self._folia_rgb, self._folia_termal = self.maska_znacznika_rgb, self.maska_znacznika_termal
            self.dopasowanie_naroznikow = {"rgb_iou_wzorca": iou, "termal_iou_wzorca": iou_t}
        else:
            raise BladEtapu(f"Nieznane źródło narożników: {zrodlo}")
        self.zrodlo_naroznikow = zrodlo
        self.przeniesione, self.obszary_z_termowizji, self.wyniki = None, [], None
        return self.narozniki_rgb

    def ustaw_znamie(self, maska, zrodlo):
        m = np.asarray(maska)
        if m.ndim == 3:
            m = m.max(axis=2)
        if m.shape != self.rgb.shape[:2]:
            raise BladEtapu(f"Maska ma rozmiar {m.shape[1]}×{m.shape[0]} px, a zdjęcie "
                            f"{self.rgb.shape[1]}×{self.rgb.shape[0]} px.")
        if not (m > 0).any():
            raise BladEtapu("Maska znamienia jest pusta.")
        self.maska_znamie = (m > 0).astype(np.uint8) * 255
        self.zrodlo_znamienia = zrodlo
        self.przeniesione, self.obszary_z_termowizji, self.wyniki = None, [], None
        return self.maska_znamie

    def znamie_z_cvat(self):
        if self.wzorzec is None:
            raise BladEtapu("Te obrazy nie mają adnotacji znamienia z CVAT.")
        return self.ustaw_znamie(self.wzorzec["maska_znamie_rgb"], "cvat")

    def znamie_z_pliku(self, sciezka, zrodlo="plik"):
        m = imread(sciezka, cv2.IMREAD_GRAYSCALE)
        if m is None:
            raise BladEtapu(f"Nie można otworzyć maski: {sciezka}")
        return self.ustaw_znamie(m, zrodlo)

    def znamie_z_obrysu(self, pkt):
        """Wielokat zaznaczony na zdjeciu (punkty w px zdjecia)."""
        if len(pkt) < 3:
            raise BladEtapu("Obrys musi mieć co najmniej 3 punkty.")
        return self.ustaw_znamie(geo.wypelnij([np.asarray(pkt, np.float64)], self.rgb.shape[:2]), "obrys")

    # ── 4. przeniesienie obszarow ───────────────────────────────────────────
    def przenies(self):
        """Znamie, obrys i otwor znacznika ze zdjecia na termowizje (przez T)."""
        self._wymagaj("rejestracja", "narozniki", "znamie")
        ks = self.termal.shape[:2]
        znamie_gesta = geo.przenies_maske(self.maska_znamie, self.M, ks, GESTOSC)
        self.przeniesione = {
            "narozniki": geo.przenies_punkty(self.narozniki_rgb, self.M),
            "kontury_znamienia": [geo.przenies_punkty(k, self.M) for k in geo.kontury(self.maska_znamie)],
            "znamie_gesta": znamie_gesta,
            "ulamek": geo.ulamek_pokrycia(znamie_gesta, GESTOSC),
        }
        self.wyniki = None
        return self.przeniesione

    def z_termowizji(self, pkt_termal):
        """Obszar zaznaczony na termowizji -> zdjecie (przez T^-1); zwraca opis obszaru."""
        self._wymagaj("rejestracja")
        if len(pkt_termal) < 3:
            raise BladEtapu("Obszar musi mieć co najmniej 3 punkty.")
        p = np.asarray(pkt_termal, np.float64)
        q = geo.przenies_punkty(p, np.linalg.inv(self.M))
        o = {"nr": len(self.obszary_z_termowizji) + 1, "termal_px": p, "rgb_px": q}
        if self.H_rgb is not None:
            o["pole_rgb_mm2"] = _pole_wielokata_mm2(q, self.H_rgb)
        if self.H_termal is not None:
            o["pole_termal_mm2"] = _pole_wielokata_mm2(p, self.H_termal)
        self.obszary_z_termowizji.append(o)
        if self.wyniki is not None:
            self.wyniki["obszary_z_termowizji"] = self._opis_obszarow()
        return o

    def _opis_obszarow(self):
        return [{k: v for k, v in o.items()} for o in self.obszary_z_termowizji]

    # ── 5. pomiary i zgodnosc ───────────────────────────────────────────────
    def zmierz(self):
        self._wymagaj("przeniesienie")
        p_rgb = pomiary.parametry_rgb(self.rgb, self.maska_znamie, self.H_rgb, self._folia_rgb)
        ul = self.przeniesione["ulamek"]
        s_t = geo.mm_na_px(self.H_termal, self.narozniki_termal.mean(0))
        kontrola = {
            "mm_na_px_termal": s_t,
            "piksele_znamienia_termal": float(ul.sum()),
            "pole_znamienia_termal_mm2": float(ul.sum() * s_t ** 2),
            "pole_znamienia_termal_do_rgb": float(ul.sum() * s_t ** 2 / p_rgb["pole_mm2"]),
            "pole_otworu_przeniesionego_mm2": _pole_wielokata_mm2(self.przeniesione["narozniki"][geo.OTWOR], self.H_termal),
            "pole_otworu_termal_mm2": _pole_wielokata_mm2(self.narozniki_termal[geo.OTWOR], self.H_termal),
            "pole_otworu_wzorzec_mm2": POLE_OTWORU_MM2,
        }
        kontrola["stosunek_pol_otworu"] = kontrola["pole_otworu_przeniesionego_mm2"] / kontrola["pole_otworu_termal_mm2"]
        w = {"info": dict(self.info),
             "zrodla": {"narozniki": ZRODLA_NAROZNIKOW[self.zrodlo_naroznikow],
                        "znamie": ZRODLA_ZNAMIENIA.get(self.zrodlo_znamienia, self.zrodlo_znamienia),
                        "narozniki_klucz": self.zrodlo_naroznikow, "znamie_klucz": self.zrodlo_znamienia},
             "rejestracja": self.rej, "narozniki": self.dopasowanie_naroznikow,
             "pomiary_rgb": p_rgb, "pierscien_mm": pomiary.PIERSCIEN_MM, "kontrola_skali": kontrola,
             "zgodnosc": None, "segmentacja_vs_cvat": None, "obszary_z_termowizji": self._opis_obszarow()}
        wz = self.wzorzec
        if wz is not None:                                   # badanie E1: wzorzec z CVAT na termowizji
            ks = self.termal.shape[:2]
            nar_T = self.przeniesione["narozniki"]
            s_wz = geo.mm_na_px(wz["H_termal"], wz["narozniki_termal"].mean(0))
            w["zgodnosc"] = {
                "tre": miary.tre(nar_T, wz["narozniki_termal"], wz["H_termal"]),
                "obrys": miary.zgodnosc_masek(geo.wypelnij([nar_T[geo.OBRYS]], ks, GESTOSC),
                                              geo.wypelnij([wz["narozniki_termal"][geo.OBRYS]], ks, GESTOSC),
                                              s_wz / GESTOSC),
                "otwor": miary.zgodnosc_masek(geo.wypelnij([nar_T[geo.OTWOR]], ks, GESTOSC),
                                              geo.wypelnij([wz["narozniki_termal"][geo.OTWOR]], ks, GESTOSC),
                                              s_wz / GESTOSC)}
            if self.zrodlo_znamienia != "cvat":
                w["segmentacja_vs_cvat"] = miary.zgodnosc_masek(self.maska_znamie > 0, wz["maska_znamie_rgb"] > 0,
                                                                p_rgb["mm_na_px"])
        self.wyniki = w
        return w

    # ── 6. raport ───────────────────────────────────────────────────────────
    def obrazy(self):
        self._wymagaj("pomiary")
        return obrazy.rysuj(self)

    def zapisz_raport(self, folder=None):
        """raport.html, metryki.json i obrazy PNG w folderze wynikow; zwraca sciezke raportu."""
        if self.wyniki is None:
            self.zmierz()
        kat = Path(folder) if folder else self.folder
        kat.mkdir(parents=True, exist_ok=True)
        ob = self.ostatnie_obrazy = self.obrazy()
        for nazwa, img in ob.items():
            dop.imwrite(kat / f"{nazwa}.png", img)
        (kat / "metryki.json").write_text(json.dumps(bez_tablic(self.wyniki), indent=1, ensure_ascii=False),
                                          encoding="utf-8")
        sciezka = kat / "raport.html"
        raport.zapisz(sciezka, self.wyniki, ob)
        return sciezka


def analizuj_pare(n, model="auto", narozniki="cvat", folder=None, log=None):
    """Caly potok dla pary z bazy na wzorcu z CVAT (znamie i narozniki) - jak potok_pary.py."""
    a = Analiza.z_pary(n, folder)
    a.rejestruj(model, log)
    a.ustaw_narozniki(narozniki)
    a.znamie_z_cvat()
    a.przenies()
    a.zmierz()
    return a
