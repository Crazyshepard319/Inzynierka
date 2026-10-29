"""
Baza danych systemu (SQLite, plik dane/baza.sqlite): znamiona, pary obrazow, adnotacje z CVAT, analizy
i ich miary. Pliki obrazow i masek zostaja w folderach (dane/pary/N/, wyniki/), baza przechowuje ich
sciezki (wzgledem folderu Inzynierka) i wszystkie wyniki liczbowe.

    znamie     (id, fold, opis)                                   z dane/znamiona.csv
    para       (id, znamie_id, plik_rgb, plik_termal, ...)        z dane/pary/N i dane/mapowanie_*.csv
    adnotacja  (para_id, modalnosc, obiekt, plik_maski, narozniki, homografia_mm, rms_mm)   z CVAT
    analiza    (id, para_id, data, status, modele, macierz_T, folder_wynikow, ...)          kazde uruchomienie
    miara      (analiza_id, grupa, nazwa, wartosc, jednostka)     liczby z metryki.json
    piksel     (analiza_id, x, y, ulamek, w_masce, intensywnosc)  piksele termowizji objete znamieniem
                                                                  (surowa intensywnosc z nagrania .SEQ)
    widoki: ostatnia_analiza (najnowsza udana analiza pary), wyniki_par (jej miary z numerem znamienia i foldem)

Baza tworzy sie sama przy pierwszym zapisie analizy (aplikacja, potok_pary.py). Recznie:
    baza_danych.bat utworz             schemat + import znamion, par i adnotacji (ponowne = aktualizacja)
    baza_danych.bat importuj_wyniki    dotychczasowe wyniki z wyniki/wyniki_obu/para_N/metryki.json
    baza_danych.bat pokaz              podsumowanie
    baza_danych.bat eksport [plik]     ostatnie wyniki par jako CSV (jedna kolumna na miare)
    baza_danych.bat eksport_piksele [plik]   piksele znamion na termowizji z ostatnich analiz par (CSV)
    baza_danych.bat sql "SELECT ..."   dowolne zapytanie
"""
import argparse
import csv
import json
import math
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

import numpy as np

if __package__ in (None, ""):                         # uruchomienie jako skrypt: python analiza/baza.py
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    __package__ = "analiza"

from .dane import DANE, INZ, PARY                     # noqa: E402
from .pomiary import wczytaj_piksele                  # noqa: E402

PLIK_BAZY = DANE / "baza.sqlite"
WERSJA_SCHEMATU = 2          # 2: tabela piksel

SCHEMAT = """
CREATE TABLE IF NOT EXISTS znamie (
    id      INTEGER PRIMARY KEY,                -- numer znamienia (dane/znamiona.csv)
    fold    INTEGER NOT NULL CHECK (fold BETWEEN 1 AND 5),   -- fold walidacji krzyzowej
    opis    TEXT
);
CREATE TABLE IF NOT EXISTS para (
    id              INTEGER PRIMARY KEY,        -- numer pary (dane/pary/N)
    znamie_id       INTEGER REFERENCES znamie(id),
    plik_rgb        TEXT NOT NULL,              -- sciezki wzgledem folderu Inzynierka
    plik_termal     TEXT NOT NULL,
    plik_termal_c   TEXT,                       -- mapa temperatur °C (.npy)
    oryginal_rgb    TEXT,                       -- IMG_xxxx.heic
    oryginal_termal TEXT,                       -- thermalNNNN.SEQ
    data_zdjecia    TEXT,
    szer_rgb INTEGER, wys_rgb INTEGER, szer_termal INTEGER, wys_termal INTEGER,
    zaktualizowano  TEXT
);
CREATE TABLE IF NOT EXISTS adnotacja (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    para_id       INTEGER NOT NULL REFERENCES para(id) ON DELETE CASCADE,
    modalnosc     TEXT NOT NULL CHECK (modalnosc IN ('rgb', 'termal')),
    obiekt        TEXT NOT NULL CHECK (obiekt IN ('znamie', 'znacznik')),
    plik_maski    TEXT NOT NULL,
    narozniki     TEXT,                         -- JSON 8 x 2 [px], kolejnosc wzorca Π (tylko znacznik)
    homografia_mm TEXT,                         -- JSON 3 x 3, px -> mm (tylko znacznik)
    rms_mm        REAL,                         -- dopasowanie narozników do wzorca Π
    zrodlo        TEXT NOT NULL DEFAULT 'CVAT',
    UNIQUE (para_id, modalnosc, obiekt)
);
CREATE TABLE IF NOT EXISTS analiza (
    id                      INTEGER PRIMARY KEY AUTOINCREMENT,
    para_id                 INTEGER REFERENCES para(id),     -- NULL dla obrazow spoza bazy
    plik_rgb                TEXT,
    plik_termal             TEXT,
    data                    TEXT NOT NULL,
    status                  TEXT NOT NULL CHECK (status IN ('ok', 'blad')),
    blad                    TEXT,
    model_rejestracji       TEXT,
    macierz_T               TEXT,               -- JSON 3 x 3: piksel zdjecia -> piksel termowizji
    model_znamienia         TEXT,
    model_znacznika_termal  TEXT,
    folder_wynikow          TEXT,
    wersja_kodu             TEXT                -- commit gita
);
CREATE TABLE IF NOT EXISTS miara (
    analiza_id  INTEGER NOT NULL REFERENCES analiza(id) ON DELETE CASCADE,
    grupa       TEXT NOT NULL,                  -- np. zgodnosc_modalnosci.obrys, pomiary_rgb
    nazwa       TEXT NOT NULL,                  -- np. dice, hd95_mm, pole_mm2
    wartosc     REAL,
    jednostka   TEXT,
    PRIMARY KEY (analiza_id, grupa, nazwa)
);
CREATE TABLE IF NOT EXISTS piksel (
    analiza_id   INTEGER NOT NULL REFERENCES analiza(id) ON DELETE CASCADE,
    x            INTEGER NOT NULL,              -- kolumna piksela obrazu termowizyjnego (0 = lewa krawedz)
    y            INTEGER NOT NULL,              -- wiersz piksela (0 = gorna krawedz)
    ulamek       REAL NOT NULL CHECK (ulamek > 0 AND ulamek <= 1),   -- czesc pola piksela pokryta przez znamie
    w_masce      INTEGER NOT NULL CHECK (w_masce IN (0, 1)),         -- ulamek >= 0,5
    intensywnosc INTEGER NOT NULL,              -- surowa wartosc detektora z nagrania .SEQ
    PRIMARY KEY (analiza_id, x, y)
);
CREATE INDEX IF NOT EXISTS ix_para_znamie ON para(znamie_id);
CREATE INDEX IF NOT EXISTS ix_analiza_para ON analiza(para_id, status);
CREATE INDEX IF NOT EXISTS ix_miara_nazwa ON miara(grupa, nazwa);
CREATE VIEW IF NOT EXISTS ostatnia_analiza AS
    SELECT a.* FROM analiza a
    WHERE a.status = 'ok' AND a.para_id IS NOT NULL
      AND a.id = (SELECT MAX(b.id) FROM analiza b WHERE b.para_id = a.para_id AND b.status = 'ok');
CREATE VIEW IF NOT EXISTS wyniki_par AS
    SELECT p.id AS para, p.znamie_id AS znamie, z.fold AS fold, a.id AS analiza, a.data AS data,
           m.grupa, m.nazwa, m.wartosc, m.jednostka
    FROM ostatnia_analiza a
    JOIN para p ON p.id = a.para_id
    LEFT JOIN znamie z ON z.id = p.znamie_id
    JOIN miara m ON m.analiza_id = a.id;
"""

POMIJANE = {"info", "zrodla", "macierz_T", "tre_punkty", "folder", "model", "model_termal"}


def _wzgledna(p):
    """Sciezka wzgledem folderu Inzynierka (z ukosnikami /), a gdy plik lezy poza nim - bezwzgledna."""
    if p is None:
        return None
    p = Path(p).resolve()
    try:
        return p.relative_to(INZ.resolve()).as_posix()
    except ValueError:
        return str(p)


def _csv(nazwa):
    p = DANE / nazwa
    if not p.exists():
        return []
    with open(p, encoding="utf-8-sig") as f:
        return list(csv.DictReader(f, delimiter=";"))


def _jednostka(nazwa):
    if nazwa.endswith("_mm2"):
        return "mm²"
    if nazwa == "mm_na_px" or nazwa.startswith("mm_na_px"):
        return "mm/px"
    if nazwa.endswith("_mm"):
        return "mm"
    if nazwa.endswith("_px") or nazwa.startswith("piksele"):
        return "px"
    if nazwa.startswith("intensywnosc"):
        return "j. surowe"
    if nazwa.endswith("_s"):
        return "s"
    return ""


def splaszcz(d, grupa=()):
    """Liczby ze slownika wynikow (metryki.json) jako (grupa, nazwa, wartosc, jednostka)."""
    for k, v in d.items():
        if k in POMIJANE or str(k).startswith("_"):
            continue
        if isinstance(v, dict):
            yield from splaszcz(v, grupa + (str(k),))
        elif isinstance(v, (bool, np.bool_)):
            yield ".".join(grupa), str(k), float(v), ""
        elif isinstance(v, (int, float, np.integer, np.floating)):
            x = float(v)
            yield ".".join(grupa), str(k), (x if math.isfinite(x) else None), _jednostka(str(k))
        elif k == "lab_znamie" and isinstance(v, (list, tuple)) and len(v) == 3:
            for skl, x in zip(("L", "a", "b"), v):
                yield ".".join(grupa), f"lab_{skl}", float(x), ""


def wersja_kodu():
    """Skrot commita gita (z plikow .git, bez programu git) albo None."""
    g = INZ / ".git"
    try:
        head = (g / "HEAD").read_text().strip()
        if head.startswith("ref: "):
            ref = head[5:]
            p = g / ref
            if p.exists():
                return p.read_text().strip()[:7]
            for linia in (g / "packed-refs").read_text().splitlines():
                if linia.endswith(" " + ref):
                    return linia[:7]
            return None
        return head[:7]
    except OSError:
        return None


class Baza:
    """Polaczenie z baza (context manager: zatwierdza zmiany przy wyjsciu bez bledu)."""

    def __init__(self, sciezka=None, utworz=True):
        self.sciezka = Path(sciezka) if sciezka else PLIK_BAZY
        nowa = not self.sciezka.exists()
        if nowa and not utworz:
            raise FileNotFoundError(f"Nie ma bazy {self.sciezka} - utwórz ją: baza_danych.bat utworz")
        self.sciezka.parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(str(self.sciezka), timeout=30)
        self.db.row_factory = sqlite3.Row
        self.db.execute("PRAGMA foreign_keys = ON")
        if nowa:
            self.utworz()
            self.importuj_dane()
        elif self.db.execute("PRAGMA user_version").fetchone()[0] < WERSJA_SCHEMATU:
            self.utworz()                                # starsza baza: dopisuje nowe tabele (IF NOT EXISTS)

    def __enter__(self):
        return self

    def __exit__(self, typ, *_):
        if typ is None:
            self.db.commit()
        self.db.close()

    # ── schemat i dane wejsciowe ─────────────────────────────────────────────
    def utworz(self):
        self.db.executescript(SCHEMAT)
        self.db.execute(f"PRAGMA user_version = {WERSJA_SCHEMATU}")

    def importuj_dane(self):
        """Znamiona, pary i adnotacje z CVAT z plikow (ponowne wywolanie aktualizuje wpisy)."""
        teraz = datetime.now().isoformat(timespec="seconds")
        podzial = {int(r["para"]): (int(r["znamie"]), int(r["fold"])) for r in _csv("znamiona.csv")}
        for zn, fold in sorted(set(podzial.values())):
            self.db.execute("INSERT INTO znamie (id, fold) VALUES (?, ?) ON CONFLICT(id) DO UPDATE SET fold = excluded.fold",
                            (zn, fold))
        rgb = {r["plik"]: r for r in _csv("mapowanie_dane_RGB.csv")}
        ter = {r["plik"]: r for r in _csv("mapowanie_dane_termowizja.csv")}
        numery = sorted(int(k.name) for k in PARY.iterdir() if k.name.isdigit()) if PARY.is_dir() else []
        n_par = n_adn = 0
        for n in numery:
            k = PARY / str(n)
            if not ((k / "rgb.jpg").exists() and (k / "termal.jpg").exists()):
                continue
            r, t = rgb.get(f"{n}.jpg", {}), ter.get(f"{n}.jpg", {})
            liczba = lambda d, kl: int(d[kl]) if d.get(kl, "").isdigit() else None
            self.db.execute("""
                INSERT INTO para (id, znamie_id, plik_rgb, plik_termal, plik_termal_c, oryginal_rgb, oryginal_termal,
                                  data_zdjecia, szer_rgb, wys_rgb, szer_termal, wys_termal, zaktualizowano)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET znamie_id = excluded.znamie_id, plik_rgb = excluded.plik_rgb,
                    plik_termal = excluded.plik_termal, plik_termal_c = excluded.plik_termal_c,
                    oryginal_rgb = excluded.oryginal_rgb, oryginal_termal = excluded.oryginal_termal,
                    data_zdjecia = excluded.data_zdjecia, szer_rgb = excluded.szer_rgb, wys_rgb = excluded.wys_rgb,
                    szer_termal = excluded.szer_termal, wys_termal = excluded.wys_termal,
                    zaktualizowano = excluded.zaktualizowano""",
                (n, podzial.get(n, (None,))[0], _wzgledna(k / "rgb.jpg"), _wzgledna(k / "termal.jpg"),
                 _wzgledna(k / "termal_C.npy") if (k / "termal_C.npy").exists() else None,
                 r.get("oryginal"), t.get("nagranie"), r.get("data_wykonania"),
                 liczba(r, "szerokosc"), liczba(r, "wysokosc"), liczba(t, "szerokosc"), liczba(t, "wysokosc"), teraz))
            n_par += 1
            n_adn += self._importuj_adnotacje(n, k)
        return {"znamiona": len(set(podzial.values())), "pary": n_par, "adnotacje": n_adn}

    def _importuj_adnotacje(self, n, k):
        nar = json.loads((k / "narozniki.json").read_text(encoding="utf-8")) if (k / "narozniki.json").exists() else {}
        ile = 0
        for modalnosc, obiekt, plik, klucz in (("rgb", "znamie", "maska_znamie_rgb.png", None),
                                               ("rgb", "znacznik", "maska_znacznik_rgb.png", "rgb"),
                                               ("termal", "znacznik", "maska_znacznik_termal.png", "termowizja")):
            if not (k / plik).exists():
                continue
            z = nar.get(klucz, {}) if klucz else {}
            self.db.execute("""
                INSERT INTO adnotacja (para_id, modalnosc, obiekt, plik_maski, narozniki, homografia_mm, rms_mm)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(para_id, modalnosc, obiekt) DO UPDATE SET plik_maski = excluded.plik_maski,
                    narozniki = excluded.narozniki, homografia_mm = excluded.homografia_mm, rms_mm = excluded.rms_mm""",
                (n, modalnosc, obiekt, _wzgledna(k / plik),
                 json.dumps(z["punkty_px"]) if "punkty_px" in z else None,
                 json.dumps(z["homografia_px_na_mm"]) if "homografia_px_na_mm" in z else None, z.get("rms_mm")))
            ile += 1
        return ile

    def _para_istnieje(self, n):
        return n is not None and self.db.execute("SELECT 1 FROM para WHERE id = ?", (n,)).fetchone() is not None

    # ── analizy ──────────────────────────────────────────────────────────────
    def zapisz_analize(self, a, status="ok", blad=None, folder=None, data=None):
        """Wpis analizy system.Analiza (po etapie pomiarow albo z bledem) i jej miar; zwraca id analizy."""
        if a.para is not None and not self._para_istnieje(a.para):
            self.importuj_dane()                         # nowa para dopisana do dane/pary
        w = a.wyniki or {}
        zr = w.get("zrodla", {})
        cur = self.db.execute("""
            INSERT INTO analiza (para_id, plik_rgb, plik_termal, data, status, blad, model_rejestracji, macierz_T,
                                 model_znamienia, model_znacznika_termal, folder_wynikow, wersja_kodu)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (a.para if self._para_istnieje(a.para) else None, _wzgledna(a.rgb_path), _wzgledna(a.ter_path),
             data or datetime.now().isoformat(timespec="seconds"), status, blad,
             (a.rej or {}).get("model"), json.dumps(np.asarray(a.M).tolist()) if a.M is not None else None,
             zr.get("znamie") if a.maska_znamie is not None else None,
             a.model_termal, _wzgledna(folder or a.folder), wersja_kodu()))
        aid = cur.lastrowid
        if status == "ok" and w:
            self.db.executemany("INSERT OR REPLACE INTO miara VALUES (?, ?, ?, ?, ?)",
                                [(aid, g, n, v, j) for g, n, v, j in splaszcz(w)])
            if getattr(a, "piksele", None) is not None:
                self._zapisz_piksele(aid, a.piksele)
        return aid

    def _zapisz_piksele(self, aid, pk):
        self.db.executemany("INSERT OR REPLACE INTO piksel VALUES (?, ?, ?, ?, ?, ?)",
                            [(aid, int(x), int(y), float(u), int(m), int(i)) for x, y, u, m, i in
                             zip(pk["x"], pk["y"], pk["ulamek"], pk["w_masce"], pk["intensywnosc"])])

    def zapisz_blad(self, para, tekst, plik_rgb=None, plik_termal=None):
        """Nieudana analiza, gdy nie bylo nawet obiektu Analiza (np. brak pliku)."""
        if para is not None and not self._para_istnieje(para):
            self.importuj_dane()
        return self.db.execute(
            "INSERT INTO analiza (para_id, plik_rgb, plik_termal, data, status, blad, wersja_kodu) "
            "VALUES (?, ?, ?, ?, 'blad', ?, ?)",
            (para if self._para_istnieje(para) else None, _wzgledna(plik_rgb), _wzgledna(plik_termal),
             datetime.now().isoformat(timespec="seconds"), tekst, wersja_kodu())).lastrowid

    def importuj_wyniki(self, katalog=None):
        """Dotychczasowe wyniki potoku (wyniki/wyniki_obu/para_N/metryki.json, blad.txt) jako analizy.
        Pomija foldery, ktore juz sa w bazie z ta sama data."""
        kat = Path(katalog) if katalog else INZ / "wyniki" / "wyniki_obu"
        dodane = 0
        for f in sorted(kat.glob("para_*"), key=lambda p: int(p.name[5:]) if p.name[5:].isdigit() else 0):
            if not f.name[5:].isdigit():
                continue
            n = int(f.name[5:])
            met, bl = f / "metryki.json", f / "blad.txt"
            nowszy_blad = bl.exists() and (not met.exists() or bl.stat().st_mtime >= met.stat().st_mtime)
            zrodlo = bl if nowszy_blad else met
            if not zrodlo.exists():
                continue
            data = datetime.fromtimestamp(zrodlo.stat().st_mtime).isoformat(timespec="seconds")
            if self.db.execute("SELECT 1 FROM analiza WHERE folder_wynikow = ? AND data = ?",
                               (_wzgledna(f), data)).fetchone():
                continue
            if not self._para_istnieje(n):
                self.importuj_dane()
            para = n if self._para_istnieje(n) else None
            if nowszy_blad:
                self.db.execute("INSERT INTO analiza (para_id, data, status, blad, folder_wynikow) "
                                "VALUES (?, ?, 'blad', ?, ?)",
                                (para, data, bl.read_text(encoding="utf-8", errors="replace").strip(), _wzgledna(f)))
            else:
                w = json.loads(met.read_text(encoding="utf-8"))
                rej, zr = w.get("rejestracja", {}), w.get("zrodla", {})
                aid = self.db.execute("""
                    INSERT INTO analiza (para_id, plik_rgb, plik_termal, data, status, model_rejestracji, macierz_T,
                                         model_znamienia, model_znacznika_termal, folder_wynikow)
                    VALUES (?, ?, ?, ?, 'ok', ?, ?, ?, ?, ?)""",
                    (para, None, None, data, rej.get("model"), json.dumps(rej.get("macierz_T")),
                     zr.get("znamie"), zr.get("znacznik_termal"), _wzgledna(f))).lastrowid
                self.db.executemany("INSERT OR REPLACE INTO miara VALUES (?, ?, ?, ?, ?)",
                                    [(aid, g, n_, v, j) for g, n_, v, j in splaszcz(w)])
                if (f / "piksele_znamienia_termal.csv").exists():
                    self._zapisz_piksele(aid, wczytaj_piksele(f / "piksele_znamienia_termal.csv"))
            dodane += 1
        return dodane

    # ── odczyt ───────────────────────────────────────────────────────────────
    def info_pary(self, n):
        """Jak dane.info_pary: oryginalne nazwy plikow, data zdjecia, znamie i fold (albo None)."""
        r = self.db.execute("SELECT p.*, z.fold FROM para p LEFT JOIN znamie z ON z.id = p.znamie_id WHERE p.id = ?",
                            (n,)).fetchone()
        if r is None:
            return None
        info = {"rgb_oryginal": r["oryginal_rgb"], "rgb_data": r["data_zdjecia"], "termal_nagranie": r["oryginal_termal"]}
        if r["znamie_id"] is not None:
            info.update(znamie=int(r["znamie_id"]), fold=int(r["fold"]))
        return {k: v for k, v in info.items() if v is not None}

    def tabela_wynikow(self):
        """Ostatnie udane analizy par: (kolumny, wiersze) - jedna kolumna na miare 'grupa.nazwa'."""
        rows = self.db.execute("SELECT * FROM wyniki_par ORDER BY para").fetchall()
        kolumny = sorted({f"{r['grupa']}.{r['nazwa']}" if r["grupa"] else r["nazwa"] for r in rows})
        tab = {}
        for r in rows:
            t = tab.setdefault(r["para"], {"para": r["para"], "znamie": r["znamie"], "fold": r["fold"],
                                          "analiza": r["analiza"], "data": r["data"]})
            t[f"{r['grupa']}.{r['nazwa']}" if r["grupa"] else r["nazwa"]] = r["wartosc"]
        return ["para", "znamie", "fold", "analiza", "data"] + kolumny, [tab[k] for k in sorted(tab)]

    def piksele_par(self):
        """Piksele znamion na termowizji z ostatnich udanych analiz par: (kolumny, wiersze)."""
        cur = self.db.execute("""
            SELECT a.para_id AS para, p.znamie_id AS znamie, a.id AS analiza, k.x, k.y, k.ulamek, k.w_masce,
                   k.intensywnosc
            FROM ostatnia_analiza a JOIN para p ON p.id = a.para_id JOIN piksel k ON k.analiza_id = a.id
            ORDER BY a.para_id, k.y, k.x""")
        return [d[0] for d in cur.description], cur.fetchall()

    def podsumowanie(self):
        q = lambda s: self.db.execute(s).fetchone()[0]
        return {"plik": str(self.sciezka), "znamiona": q("SELECT COUNT(*) FROM znamie"),
                "pary": q("SELECT COUNT(*) FROM para"), "adnotacje": q("SELECT COUNT(*) FROM adnotacja"),
                "analizy": q("SELECT COUNT(*) FROM analiza"),
                "analizy_udane": q("SELECT COUNT(*) FROM analiza WHERE status = 'ok'"),
                "pary_z_wynikiem": q("SELECT COUNT(*) FROM ostatnia_analiza"),
                "miary": q("SELECT COUNT(*) FROM miara"), "piksele": q("SELECT COUNT(*) FROM piksel")}


def istnieje():
    return PLIK_BAZY.exists()


def main():
    ap = argparse.ArgumentParser(description="Baza danych systemu (SQLite)")
    ap.add_argument("polecenie", choices=["utworz", "importuj_wyniki", "pokaz", "eksport", "eksport_piksele", "sql"])
    ap.add_argument("argument", nargs="?", help="eksport: plik CSV; sql: zapytanie")
    ap.add_argument("--baza", default=None, help=f"plik bazy (domyslnie {PLIK_BAZY})")
    a = ap.parse_args()
    with Baza(a.baza) as b:
        if a.polecenie == "utworz":
            b.utworz()
            print("Zaimportowano:", b.importuj_dane())
        elif a.polecenie == "importuj_wyniki":
            print(f"Dodane analizy: {b.importuj_wyniki()}")
        elif a.polecenie == "eksport":
            kolumny, wiersze = b.tabela_wynikow()
            plik = Path(a.argument) if a.argument else INZ / "wyniki" / "baza_wyniki_par.csv"
            plik.parent.mkdir(parents=True, exist_ok=True)
            with open(plik, "w", newline="", encoding="utf-8-sig") as f:
                wr = csv.DictWriter(f, kolumny, delimiter=";")
                wr.writeheader()
                for w in wiersze:
                    wr.writerow({k: (f"{v:.6g}".replace(".", ",") if isinstance(v, float) else v) for k, v in w.items()})
            print(f"{len(wiersze)} par, {len(kolumny)} kolumn -> {plik}")
        elif a.polecenie == "eksport_piksele":
            kolumny, wiersze = b.piksele_par()
            plik = Path(a.argument) if a.argument else INZ / "wyniki" / "baza_piksele_znamion.csv"
            plik.parent.mkdir(parents=True, exist_ok=True)
            with open(plik, "w", newline="", encoding="utf-8") as f:
                wr = csv.writer(f, delimiter=";")
                wr.writerow(kolumny)
                wr.writerows(tuple(r) for r in wiersze)
            print(f"{len(wiersze)} pikseli z {len({r['para'] for r in wiersze})} par -> {plik}")
        elif a.polecenie == "sql":
            cur = b.db.execute(a.argument or "SELECT name FROM sqlite_master")
            print(";".join(d[0] for d in cur.description or []))
            for r in cur.fetchall():
                print(";".join("" if v is None else str(v) for v in r))
        if a.polecenie in ("utworz", "importuj_wyniki", "pokaz"):
            for k, v in b.podsumowanie().items():
                print(f"{k}: {v}")


if __name__ == "__main__":
    main()
