"""
Testy funkcjonalne systemu bez interfejsu graficznego (rozdzial 6.6 pracy).

Kazdy test sprawdza wymaganie z rozdzialu 3 (WF - funkcjonalne, WN - pozafunkcjonalne) na danych ze zbioru
(para 14 - z adnotacjami CVAT, zapisana rejestracja i maska PanDerm; para 75 - znacznik niewykrywalny).
Wyniki zapisywane sa do folderow tymczasowych; baza danych testow jest osobnym plikiem tymczasowym,
wiec dane/baza.sqlite i wyniki/ nie sa zmieniane.

Uruchomienie (folder projekt, srodowisko aplikacji):
    uruchom_testy.bat
    python -m unittest discover -s testy -v
Testy wymagajace wag U-Net (E2) albo biblioteki flirpy sa pomijane, gdy ich brak (komunikat "skipped").
"""
import json
import shutil
import sqlite3
import sys
import tempfile
import time
import unittest
from pathlib import Path

import cv2
import numpy as np

PROJEKT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJEKT))

from analiza import baza, geometria as geo, miary, pomiary, raport     # noqa: E402
from analiza.dane import PARY, PLIK_SUROWYCH, imread                   # noqa: E402
from analiza.system import PLIK_PIKSELI, Analiza, BladEtapu            # noqa: E402

PARA = 14                  # para z adnotacjami CVAT i zapisanymi wynikami
PARA_BEZ_ZNACZNIKA = 75    # znacznik na zdjeciu wykrywany niepewnie (zgodnosc z Pi < 0,65)
WYNIKI_PARY = PROJEKT.parent / "wyniki" / "wyniki_obu" / f"para_{PARA}"


def _analiza_z_zapisanych(folder):
    """Para 14: zapisana rejestracja + zapisana maska PanDerm (bez PyTorch), przeniesienie i pomiary."""
    a = Analiza.z_pary(PARA, folder=folder)
    a.wczytaj_rejestracje()
    a.ustaw_narozniki()
    a.ustaw_znamie(imread(WYNIKI_PARY / "maska_znamie_panderm.png", cv2.IMREAD_GRAYSCALE))
    try:
        a.segmentuj_znacznik_termal()                    # U-Net (E2) - gdy sa wagi modelu
    except BladEtapu:
        pass
    a.przenies()
    a.zmierz()
    return a


class TestSystemu(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.tmp = Path(tempfile.mkdtemp(prefix="testy_systemu_"))
        cls._plik_bazy = baza.PLIK_BAZY
        baza.PLIK_BAZY = cls.tmp / "baza_testowa.sqlite"   # testy nie zmieniaja dane/baza.sqlite
        cls.a = _analiza_z_zapisanych(cls.tmp / "para")

    @classmethod
    def tearDownClass(cls):
        baza.PLIK_BAZY = cls._plik_bazy
        shutil.rmtree(cls.tmp, ignore_errors=True)

    # ── wejscie ──────────────────────────────────────────────────────────────
    def test_T01_wczytanie_pary(self):
        """WF1: para ze zbioru - oba obrazy, termowizja 320 x 240, numer znamienia i foldu, adnotacje CVAT."""
        a = Analiza.z_pary(PARA, folder=self.tmp / "t01")
        self.assertEqual(a.termal.shape[:2], (240, 320))
        self.assertEqual(a.rgb.ndim, 3)
        self.assertIn("znamie", a.info)
        self.assertIsNotNone(a.wzorzec)

    def test_T02_brak_pliku(self):
        """WF1, WN6: nieistniejacy plik - wyjatek BladEtapu z czytelnym komunikatem."""
        with self.assertRaises(BladEtapu) as k:
            Analiza(self.tmp / "brak.jpg", PARY / str(PARA) / "termal.jpg")
        self.assertIn("Nie można otworzyć", str(k.exception))

    def test_T03_kolejnosc_etapow(self):
        """WN6: etap bez wyniku poprzedniego (przeniesienie przed rejestracja) - komunikat zamiast awarii."""
        a = Analiza.z_pary(PARA, folder=self.tmp / "t03")
        with self.assertRaises(BladEtapu) as k:
            a.przenies()
        self.assertIn("rejestrację", str(k.exception))

    # ── rejestracja ──────────────────────────────────────────────────────────
    def test_T04_rejestracja(self):
        """WF2, WN1, WN4: pelna rejestracja pary 14 - czas < 15 s, model afiniczny lub homografia, TRE < 1 mm."""
        a = Analiza.z_pary(PARA, folder=self.tmp / "t04")
        a.folder_rejestracji = self.tmp / "t04_rejestracja"
        t0 = time.perf_counter()
        rej = a.rejestruj()
        czas = time.perf_counter() - t0
        self.assertLess(czas, 15.0)
        self.assertIn(rej.get("model"), ("afiniczna", "homografia"))
        wz = a.wzorzec
        tre = miary.tre(geo.przenies_punkty(wz["narozniki_rgb"], a.M), wz["narozniki_termal"], wz["H_termal"])
        self.assertLess(tre["tre_srednie"], 1.0)
        print(f"\n    T04: czas rejestracji {czas:.1f} s, model {rej.get('model')}, TRE {tre['tre_srednie']:.2f} mm",
              end=" ")

    def test_T05_brak_znacznika_termowizja(self):
        """WN6: obraz termowizyjny bez znacznika - rejestracja oznaczona jako niepewna (zgodnosc z Pi < 0,65), ostrzezenie w raporcie."""
        import dopasowanie3 as dop
        plik = self.tmp / "bez_znacznika.png"
        y, x = np.mgrid[0:240, 0:320]
        cv2.imwrite(str(plik), (150 + 0.1 * x).astype(np.uint8))       # gladki gradient, brak folii
        a = Analiza(PARY / str(PARA) / "rgb.jpg", plik, folder=self.tmp / "t05")
        a.folder_rejestracji = self.tmp / "t05_rejestracja"
        rej = a.rejestruj()
        self.assertLess(rej["zgodnosc_termal"], dop.MIN_ZGODNOSC)
        uwagi = raport.uwagi(dict(self.a.wyniki, rejestracja=rej))
        self.assertTrue(any("na termowizji wykryty niepewnie" in u for u in uwagi))
        print(f"\n    T05: zgodnosc ksztaltu z Pi na termowizji {rej['zgodnosc_termal']:.2f}", end=" ")

    def test_T06_niepewny_znacznik_zdjecie(self):
        """WN6: para 75 - znacznik o ksztalcie niezgodnym z wzorcem Pi jest odrzucany z komunikatem."""
        from modele_segmentacja.znacznik import BrakZnacznika, wykryj_znacznik
        with self.assertRaises(BrakZnacznika) as k:
            wykryj_znacznik(imread(PARY / str(PARA_BEZ_ZNACZNIKA) / "rgb.jpg"))
        self.assertIn("zgodnosc ksztaltu z Pi", str(k.exception))

    # ── segmentacja, przeniesienie, pomiary ──────────────────────────────────
    def test_T07_narozniki_i_skala(self):
        """WF4: 8 naroznikow w obu modalnosciach, IoU dopasowanego wzorca Pi >= 0,8."""
        a = self.a
        self.assertEqual(a.narozniki_rgb.shape, (8, 2))
        self.assertEqual(a.narozniki_termal.shape, (8, 2))
        self.assertGreaterEqual(a.dopasowanie_naroznikow["rgb_iou_wzorca"], 0.8)
        self.assertGreaterEqual(a.dopasowanie_naroznikow["termal_iou_wzorca"], 0.8)

    def test_T08_przeniesienie_i_pomiary(self):
        """WF7, WF8: pole znamienia na termowizji zgodne z polem na zdjeciu (+-15 %), komplet parametrow znamienia."""
        w = self.a.wyniki
        self.assertTrue(0.85 <= w["kontrola_skali"]["pole_znamienia_termal_do_rgb"] <= 1.15)
        for k in ("pole_mm2", "obwod_mm", "srednica_rownowazna_mm", "feret_max_mm", "feret_min_mm",
                  "kolistosc", "asymetria_os_glowna", "lab_znamie"):
            self.assertIn(k, w["pomiary_rgb"])
        self.assertGreater(w["pomiary_rgb"]["pole_mm2"], 0)

    def test_T09_zgodnosc_modalnosci(self):
        """WF6, WF9: maska znacznika z U-Netu i miary zgodnosci E2 (Dice folii >= 0,9)."""
        e2 = self.a.wyniki["zgodnosc_modalnosci"]
        if e2 is None:
            self.skipTest("brak wag modelu U-Net (modele_dane/wagi/unet_termal)")
        self.assertGreaterEqual(e2["obrys"]["dice"], 0.9)
        for k in ("dice", "iou", "hd95_mm", "assd_mm", "przesuniecie_srodkow_mm", "stosunek_pol"):
            self.assertIn(k, e2["otwor"])

    # ── piksele znamienia na termowizji ──────────────────────────────────────
    def test_T10_piksele_wspolrzedne_i_intensywnosc(self):
        """WF15: dla kazdego piksela w masce - wspolrzedne w obrazie 320 x 240 i surowa intensywnosc z nagrania .SEQ."""
        pk, ul = self.a.piksele, self.a.przeniesione["ulamek"]
        self.assertIsNotNone(pk)
        I = np.load(PARY / str(PARA) / PLIK_SUROWYCH)
        np.testing.assert_array_equal(pk["intensywnosc"], I[pk["y"], pk["x"]])
        self.assertEqual(int(pk["w_masce"].sum()), int((ul >= 0.5).sum()))
        self.assertTrue(((pk["ulamek"] > 0) & (pk["ulamek"] <= 1)).all())
        self.assertTrue((pk["x"] < 320).all() and (pk["y"] < 240).all())
        self.assertAlmostEqual(float(pk["ulamek"].sum()), self.a.wyniki["kontrola_skali"]["piksele_znamienia_termal"], 6)

    def test_T11_piksele_csv(self):
        """WF15: zapis pikseli do CSV i odczyt bez utraty danych."""
        plik = self.tmp / "piksele.csv"
        pomiary.zapisz_piksele(plik, self.a.piksele)
        wcz = pomiary.wczytaj_piksele(plik)
        for k in pomiary.KOLUMNY_PIKSELI:
            np.testing.assert_allclose(wcz[k], self.a.piksele[k], atol=1e-4)

    def test_T12_piksele_bez_nagrania(self):
        """WF15, WN6: wlasne pliki bez nagrania .SEQ - analiza dziala, pikseli brak, uwaga w raporcie."""
        kat = self.tmp / "t12"
        kat.mkdir()
        shutil.copy(PARY / str(PARA) / "rgb.jpg", kat / "zdjecie.jpg")
        shutil.copy(PARY / str(PARA) / "termal.jpg", kat / "termowizja.jpg")
        a = Analiza(kat / "zdjecie.jpg", kat / "termowizja.jpg", folder=kat / "wyniki")
        self.assertIsNone(a.para)
        self.assertIsNone(a.wczytaj_intensywnosc())
        w = dict(self.a.wyniki, piksele_termal={"zrodlo": a.zrodlo_intensywnosci})
        self.assertTrue(any("intensywności" in u for u in raport.uwagi(w)))

    def test_T13_piksele_z_nagrania_seq(self):
        """WF15: wlasne pliki z nagraniem .SEQ o tej samej nazwie - intensywnosc odczytana z nagrania (flirpy)."""
        try:
            import flirpy  # noqa: F401
        except ImportError:
            self.skipTest("brak biblioteki flirpy")
        from analiza.dane import NAGRANIA, info_pary
        kat = self.tmp / "t13"
        kat.mkdir()
        shutil.copy(PARY / str(PARA) / "termal.jpg", kat / "termowizja.jpg")
        shutil.copy(NAGRANIA / info_pary(PARA)["termal_nagranie"], kat / "termowizja.SEQ")
        a = Analiza(PARY / str(PARA) / "rgb.jpg", kat / "termowizja.jpg", folder=kat / "wyniki")
        np.testing.assert_array_equal(a.wczytaj_intensywnosc(), np.load(PARY / str(PARA) / PLIK_SUROWYCH))

    # ── raport i baza danych ─────────────────────────────────────────────────
    def test_T14_raport(self):
        """WF11: raport HTML, metryki.json (poprawny JSON), obrazy PNG i CSV pikseli w folderze wynikow."""
        sciezka = self.a.zapisz_raport()
        kat = sciezka.parent
        for plik in ("raport.html", "metryki.json", PLIK_PIKSELI, "rgb.png", "termal.png", "nakladka.png",
                     "nakladka_zblizenie.png", "piksele_termal.png"):
            self.assertTrue((kat / plik).is_file(), plik)
        w = json.loads((kat / "metryki.json").read_text(encoding="utf-8"))
        self.assertIn("piksele_termal", w)
        self.assertIn("Piksele znamienia na termowizji", sciezka.read_text(encoding="utf-8"))

    def test_T15_zapis_w_bazie(self):
        """WF12, WN9: analiza w bazie (status, modele, macierz T, wersja kodu), jej miary i piksele."""
        aid = self.a.zapisz_w_bazie(folder=self.tmp / "para")
        self.assertIsNotNone(aid)
        with baza.Baza() as b:
            r = b.db.execute("SELECT * FROM analiza WHERE id = ?", (aid,)).fetchone()
            self.assertEqual(r["status"], "ok")
            self.assertIsNotNone(r["macierz_T"])
            n_miar = b.db.execute("SELECT COUNT(*) FROM miara WHERE analiza_id = ?", (aid,)).fetchone()[0]
            n_pik = b.db.execute("SELECT COUNT(*) FROM piksel WHERE analiza_id = ?", (aid,)).fetchone()[0]
        self.assertGreater(n_miar, 50)
        self.assertEqual(n_pik, len(self.a.piksele["x"]))

    def test_T16_migracja_bazy(self):
        """WF12: baza w starszej wersji schematu (bez tabeli piksel) jest uzupelniana przy otwarciu."""
        plik = self.tmp / "stara.sqlite"
        db = sqlite3.connect(plik)
        db.executescript(baza.SCHEMAT.replace("CREATE TABLE IF NOT EXISTS piksel", "CREATE TABLE IF NOT EXISTS stara_piksel"))
        db.execute("DROP TABLE stara_piksel")
        db.execute("PRAGMA user_version = 1")
        db.commit()
        db.close()
        with baza.Baza(plik) as b:
            tabele = {r[0] for r in b.db.execute("SELECT name FROM sqlite_master WHERE type = 'table'")}
            self.assertIn("piksel", tabele)
            self.assertEqual(b.db.execute("PRAGMA user_version").fetchone()[0], baza.WERSJA_SCHEMATU)

    # ── miary i geometria (testy jednostkowe) ────────────────────────────────
    def test_T17_miary_zgodnosci(self):
        """WF9: miary na maskach o znanym wyniku - identyczne, rozlaczne i przesuniete o 5 px."""
        A = np.zeros((100, 100), bool)
        A[20:60, 20:60] = True
        B = np.roll(A, 5, axis=1)
        self.assertAlmostEqual(miary.zgodnosc_masek(A, A, 1.0)["dice"], 1.0)
        self.assertAlmostEqual(miary.zgodnosc_masek(A, np.roll(A, 50, axis=0), 1.0)["dice"], 0.0)
        z = miary.zgodnosc_masek(A, B, 0.5)                       # 0,5 mm/px
        self.assertAlmostEqual(z["dice"], 2 * 35 * 40 / (2 * 40 * 40))
        self.assertAlmostEqual(z["iou"], z["dice"] / (2 - z["dice"]), 6)
        self.assertAlmostEqual(z["przesuniecie_srodkow_mm"], 2.5, 3)
        self.assertAlmostEqual(z["hd95_mm"], 2.5, delta=0.5)

    def test_T18_geometria(self):
        """WF7: przeniesienie punktow macierza jednostkowa i ulamek pokrycia w siatce 4x gestszej."""
        p = np.array([[10.0, 20.0], [30.5, 40.25]])
        np.testing.assert_allclose(geo.przenies_punkty(p, np.eye(3)), p)
        gesta = np.zeros((8, 8), bool)
        gesta[:4, :4] = True                                       # piksel (0, 0) pokryty w calosci
        gesta[4:6, 4:8] = True                                     # piksel (1, 1) pokryty w polowie
        ul = geo.ulamek_pokrycia(gesta, 4)
        np.testing.assert_allclose(ul, [[1.0, 0.0], [0.0, 0.5]])


if __name__ == "__main__":
    unittest.main(verbosity=2)
