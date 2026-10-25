"""
Aplikacja desktopowa: system dopasowania i wielomodalnej analizy regionow (zdjecie RGB <-> termowizja).

Zakladki odpowiadaja etapom z projektu systemu (kod etapow: analiza/system.py, wspolny z potok_pary.py).
Wszystko jest wyznaczane automatycznie; adnotacje z CVAT (gdy para je ma) sluza tylko do oceny.
  1. Dane           para z bazy (dane/pary/N) albo dowolne dwa pliki
  2. Rejestracja    dopasowanie3 -> macierz T (model z dopasowanie3.MODEL); nalozenie z suwakiem
  3. Segmentacja    narozniki znacznika (wzorzec Π dopasowany do maski znacznika) -> skala w mm;
                    znamie modelem PanDerm we wnetrzu znacznika
  4. Przeniesienie  znamie i znacznik: zdjecie -> termowizja (T)
  5. Pomiary        wymiary i kolor znamienia, kontrola skali, ocena wzgledem CVAT, objasnienia wielkosci
  6. Raport         raport.html + metryki.json + obrazy PNG w wyniki/wyniki_obu/...

Podglady: kolko myszy = powiekszenie, przeciaganie myszka = przesuwanie, dwuklik = widok poczatkowy.

Wymaga: customtkinter, Pillow, opencv-python, numpy (srodowisko "inzynierka").
PanDerm uruchamia sie w osobnym srodowisku modeli (modele_segmentacja/konfiguracja.py).
"""
import os
import queue
import sys
import threading
import tkinter as tk
import traceback
import webbrowser
from pathlib import Path
from tkinter import filedialog, messagebox

import cv2
import customtkinter as ctk
import numpy as np
from PIL import Image, ImageTk

PROJEKT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJEKT))
import dopasowanie3 as dopasowanie                               # noqa: E402
from analiza import geometria as geo, raport                     # noqa: E402
from analiza.dane import INZ, dostepne_pary, imread              # noqa: E402
from analiza.obrazy import ramka                                 # noqa: E402
from analiza.system import OPIS_ZNAMIENIA, Analiza, BladEtapu, analizuj   # noqa: E402

KATALOG_RGB = INZ / "dane" / "dane_RGB"
KATALOG_TERMAL = INZ / "dane" / "dane_termowizja"

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

KOLOR_TLO_PANEL = ("#e8e8e8", "#2b2b2b")
KOLOR_LOG_TLO = "#161616"
KOLOR_LOG_TEKST = "#c8c8c8"
OK, PRACA, BLAD, SZARY = "#2cc97a", "#e8a020", "#e84040", "gray"
# kolory obrysow (jak w raporcie)
ZIELONY, CZERWONY, FIOLET, NIEBIESKI = "#00d000", "#ff3030", "#ff40ff", "#20a8ff"

ZAKLADKI = ("1. Dane", "2. Rejestracja", "3. Segmentacja", "4. Przeniesienie ROI", "5. Pomiary", "6. Raport")
ETAPY = ("wejscie", "rejestracja", "segmentacja", "przeniesienie", "pomiary", "raport")


class QueueWriter:
    """Strumien tekstu -> kolejka (log w oknie)."""

    def __init__(self, q):
        self._q = q

    def write(self, t):
        if t:
            self._q.put(t)
        return len(t)

    def flush(self):
        pass


def otworz(sciezka):
    """Plik albo folder w domyslnym programie systemu."""
    p = str(sciezka)
    if hasattr(os, "startfile"):
        os.startfile(p)
    else:
        webbrowser.open(Path(p).resolve().as_uri())


def _f(v, cyfry=2):
    return raport._f(v, cyfry)


# ── podglad obrazu z powiekszaniem, nakladkami i zaznaczaniem wielokata ─────────

class Podglad(ctk.CTkFrame):
    """Obraz BGR (opcjonalnie z warstwa BGRA nalozona z przezroczystoscia) na plotnie tk,
    z powiekszaniem i przesuwaniem.
    Nakladki: lista slownikow {pkt: (N, 2) px obrazu, kolor, grubosc, zamkniety, punkty, etykiety}.
    Wspolrzedne punktow jak w OpenCV: srodek piksela (i, j) = (j, i)."""

    def __init__(self, master, tytul="", piksele=False):
        super().__init__(master, fg_color=KOLOR_TLO_PANEL, corner_radius=10)
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)
        self._tytul = ctk.CTkLabel(self, text=tytul, anchor="w", font=ctk.CTkFont(size=12, weight="bold"))
        self._tytul.grid(row=0, column=0, sticky="ew", padx=10, pady=(6, 0))
        self.c = tk.Canvas(self, bg="#1b1b1b", highlightthickness=0, width=200, height=150)
        self.c.grid(row=1, column=0, sticky="nsew", padx=6, pady=4)
        self.piksele = piksele                      # powiekszenie bez wygladzania (termowizja)
        self.obraz = self.warstwa = None
        self.alfa = 0.5                              # 0 = sama warstwa, 1 = sam obraz
        self.nakladki = []
        self.s, self.ox, self.oy = 1.0, 0.0, 0.0     # px plotna na px obrazu, lewy gorny rog widoku
        self._widok = None
        self._pokazany = False
        self._foto = None
        self._ciagniecie = None
        c = self.c
        c.bind("<Configure>", self._zmiana_rozmiaru)
        c.bind("<MouseWheel>", lambda e: self._powieksz(e, 1 if e.delta > 0 else -1))
        c.bind("<Button-4>", lambda e: self._powieksz(e, 1))
        c.bind("<Button-5>", lambda e: self._powieksz(e, -1))
        c.bind("<ButtonPress-1>", self._start_ciagniecia)
        c.bind("<B1-Motion>", self._ciagnij)
        c.bind("<ButtonRelease-1>", lambda e: setattr(self, "_ciagniecie", None))
        c.bind("<Double-Button-1>", lambda e: self.pokaz())

    # ── dane ────────────────────────────────────────────────────────────────
    def ustaw_tytul(self, tekst):
        self._tytul.configure(text=tekst)

    def ustaw(self, obraz, warstwa=None, widok=None):
        """Nowy obraz; widok = (x0, y0, x1, y1) poczatkowy kadr (domyslnie caly obraz)."""
        nowy = obraz is None or self.obraz is None or obraz.shape != self.obraz.shape
        self.obraz, self.warstwa = obraz, warstwa
        if obraz is not None and (widok is not None or nowy or self._widok is None):
            self._widok = widok or (0, 0, obraz.shape[1], obraz.shape[0])
            self.pokaz()
        else:
            self.odswiez()

    def ustaw_nakladki(self, nakladki):
        self.nakladki = nakladki or []
        self.odswiez()

    def przybliz_jesli_calosc(self, widok):
        """Ustaw kadr, jesli dotad pokazywany byl caly obraz (nie zmienia widoku ustawionego przez uzytkownika)."""
        if self.obraz is not None and self._widok == (0, 0, self.obraz.shape[1], self.obraz.shape[0]):
            self.pokaz(widok)

    def ustaw_alfa(self, alfa):
        self.alfa = alfa
        self.odswiez()

    def wyczysc(self):
        self.obraz = self.warstwa = None
        self.nakladki, self._widok = [], None
        self.odswiez()

    # ── widok ───────────────────────────────────────────────────────────────
    def _rozmiar(self):
        return max(2, self.c.winfo_width()), max(2, self.c.winfo_height())

    def pokaz(self, widok=None):
        """Dopasuj widok do kadru (x0, y0, x1, y1) w px obrazu."""
        if widok is not None:
            self._widok = widok
        if self._widok is None:
            return self.odswiez()
        cw, ch = self._rozmiar()
        x0, y0, x1, y1 = self._widok
        self.s = min(cw / max(1, x1 - x0), ch / max(1, y1 - y0))
        self.ox = (x0 + x1) / 2 - cw / (2 * self.s)
        self.oy = (y0 + y1) / 2 - ch / (2 * self.s)
        self._pokazany = self.c.winfo_width() > 2
        self.odswiez()

    def _zmiana_rozmiaru(self, _):
        if not self._pokazany and self._widok is not None:
            self.pokaz()
        else:
            self.odswiez()

    def _na_plotno(self, pkt):
        p = np.asarray(pkt, np.float64).reshape(-1, 2)
        return (p + 0.5 - [self.ox, self.oy]) * self.s

    def _powieksz(self, e, kierunek):
        if self.obraz is None:
            return
        X, Y = e.x / self.s + self.ox, e.y / self.s + self.oy
        s = float(np.clip(self.s * (1.25 if kierunek > 0 else 0.8), 0.02, 60))
        self.s, self.ox, self.oy = s, X - e.x / s, Y - e.y / s
        self.odswiez()

    def _start_ciagniecia(self, e):
        self._ciagniecie = (e.x, e.y, self.ox, self.oy)

    def _ciagnij(self, e):
        if self._ciagniecie is None:
            return
        x0, y0, ox, oy = self._ciagniecie
        self.ox, self.oy = ox - (e.x - x0) / self.s, oy - (e.y - y0) / self.s
        self.odswiez()

    # ── rysowanie ───────────────────────────────────────────────────────────
    def odswiez(self):
        c = self.c
        c.delete("all")
        cw, ch = self._rozmiar()
        if self.obraz is None:
            c.create_text(cw / 2, ch / 2, text="brak obrazu", fill="#777")
            return
        H, W = self.obraz.shape[:2]
        s = self.s
        xa, ya = max(0, int(np.floor(self.ox))), max(0, int(np.floor(self.oy)))
        xb, yb = min(W, int(np.ceil(self.ox + cw / s))), min(H, int(np.ceil(self.oy + ch / s)))
        if xb > xa and yb > ya:
            wh = (max(1, int(round((xb - xa) * s))), max(1, int(round((yb - ya) * s))))
            interp = cv2.INTER_AREA if s < 1 else (cv2.INTER_NEAREST if self.piksele else cv2.INTER_LINEAR)
            wyc = cv2.resize(self.obraz[ya:yb, xa:xb], wh, interpolation=interp)
            if self.warstwa is not None and self.alfa < 1:
                war = cv2.resize(self.warstwa[ya:yb, xa:xb], wh, interpolation=interp)
                a = (1 - self.alfa) * war[..., 3:4].astype(np.float32) / 255 if war.shape[2] == 4 \
                    else np.full(war.shape[:2] + (1,), 1 - self.alfa, np.float32)
                wyc = (wyc * (1 - a) + war[..., :3] * a + 0.5).astype(np.uint8)
            self._foto = ImageTk.PhotoImage(Image.fromarray(cv2.cvtColor(wyc, cv2.COLOR_BGR2RGB)))
            c.create_image((xa - self.ox) * s, (ya - self.oy) * s, image=self._foto, anchor="nw")
        for n in self.nakladki:
            q = self._na_plotno(n["pkt"])
            if len(q) < 2:
                continue
            if n.get("zamkniety", True):
                q = np.vstack([q, q[:1]])
            c.create_line(*q.ravel().tolist(), fill=n.get("kolor", ZIELONY), width=n.get("grubosc", 2))
            if n.get("punkty"):
                for x, y in q[:-1] if n.get("zamkniety", True) else q:
                    c.create_oval(x - 3, y - 3, x + 3, y + 3, fill=n["kolor"], outline="")
            if n.get("etykiety"):
                for i, (x, y) in enumerate(q[:len(n["pkt"])]):
                    c.create_text(x + 9, y - 9, text=str(i), fill="white", font=("Segoe UI", 9, "bold"))



# ── aplikacja ──────────────────────────────────────────────────────────────

class Aplikacja(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("System dopasowania i analizy  RGB ↔ termowizja")
        self.geometry("1360x940")
        self.minsize(1100, 760)
        self.a = None                    # analiza.system.Analiza biezacej pary
        self._wyrownany = None           # termowizja w geometrii zdjecia (BGRA) z rejestracji
        self._raport = None              # sciezka ostatnio zapisanego raportu
        self._obrazy_raportu = {}
        self._q = queue.Queue()
        self._zajete = False
        self._przyciski = []             # przyciski blokowane w czasie obliczen
        self._buduj()
        self._odswiez_stan()
        self._odpytuj()

    # ── budowa okna ─────────────────────────────────────────────────────────
    def _buduj(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)

        pasek = ctk.CTkFrame(self, corner_radius=0, fg_color=("gray80", "gray15"))
        pasek.grid(row=0, column=0, sticky="ew")
        pasek.columnconfigure(1, weight=1)
        ctk.CTkLabel(pasek, text="System dopasowania i analizy  RGB ↔ termowizja",
                     font=ctk.CTkFont(size=19, weight="bold")).grid(row=0, column=0, padx=16, pady=10, sticky="w")
        self._lbl_para = ctk.CTkLabel(pasek, text="", text_color=SZARY, font=ctk.CTkFont(size=12))
        self._lbl_para.grid(row=0, column=1, padx=10, sticky="e")

        etapy = ctk.CTkFrame(self, fg_color="transparent")
        etapy.grid(row=1, column=0, sticky="ew", padx=14, pady=(8, 0))
        self._chipy = []
        for i, nazwa in enumerate(ZAKLADKI):
            etapy.columnconfigure(i, weight=1)
            b = ctk.CTkButton(etapy, text=nazwa, height=30, corner_radius=15, fg_color=("gray75", "gray25"),
                              text_color=("gray20", "gray80"), hover_color=("gray65", "gray35"),
                              command=lambda n=nazwa: self.tabs.set(n))
            b.grid(row=0, column=i, padx=3, sticky="ew")
            self._chipy.append(b)

        self.tabs = ctk.CTkTabview(self, corner_radius=10)
        self.tabs.grid(row=2, column=0, sticky="nsew", padx=12, pady=(2, 4))
        for nazwa in ZAKLADKI:
            t = self.tabs.add(nazwa)
            t.columnconfigure(1, weight=1)
            t.rowconfigure(0, weight=1)
        try:
            self.tabs._segmented_button.grid_remove()    # zakladki przelacza pasek etapow wyzej
        except AttributeError:
            pass
        self._zakladka_dane(self.tabs.tab(ZAKLADKI[0]))
        self._zakladka_rejestracja(self.tabs.tab(ZAKLADKI[1]))
        self._zakladka_segmentacja(self.tabs.tab(ZAKLADKI[2]))
        self._zakladka_przeniesienie(self.tabs.tab(ZAKLADKI[3]))
        self._zakladka_pomiary(self.tabs.tab(ZAKLADKI[4]))
        self._zakladka_raport(self.tabs.tab(ZAKLADKI[5]))

        dol = ctk.CTkFrame(self, fg_color="transparent")
        dol.grid(row=3, column=0, sticky="ew", padx=14, pady=(0, 10))
        dol.columnconfigure(0, weight=1)
        stat = ctk.CTkFrame(dol, fg_color="transparent")
        stat.grid(row=0, column=0, sticky="ew")
        stat.columnconfigure(0, weight=1)
        self._lbl_status = ctk.CTkLabel(stat, text="Wybierz parę albo pliki w zakładce 1.", anchor="w",
                                        text_color=SZARY, font=ctk.CTkFont(size=12))
        self._lbl_status.grid(row=0, column=0, sticky="ew")
        self._bar = ctk.CTkProgressBar(stat, width=220, height=8, mode="determinate")
        self._bar.grid(row=0, column=1, padx=(8, 0))
        self._bar.set(0)
        self._log = ctk.CTkTextbox(dol, height=110, font=ctk.CTkFont(family="Consolas", size=11),
                                   fg_color=KOLOR_LOG_TLO, text_color=KOLOR_LOG_TEKST, state="disabled")
        self._log.grid(row=1, column=0, sticky="ew", pady=(4, 0))

    def _panel(self, t, szer=330):
        """Lewa kolumna zakladki (sterowanie)."""
        p = ctk.CTkScrollableFrame(t, width=szer, fg_color=KOLOR_TLO_PANEL, corner_radius=10)
        p.grid(row=0, column=0, sticky="nsw", padx=(4, 8), pady=4)
        p.columnconfigure(0, weight=1)
        return p

    def _naglowek(self, p, tekst, r):
        ctk.CTkLabel(p, text=tekst, anchor="w", font=ctk.CTkFont(size=14, weight="bold")).grid(
            row=r, column=0, sticky="ew", padx=10, pady=(12, 2))

    def _opis(self, p, tekst, r, kolor=SZARY):
        lbl = ctk.CTkLabel(p, text=tekst, anchor="w", justify="left", wraplength=300, text_color=kolor,
                           font=ctk.CTkFont(size=12))
        lbl.grid(row=r, column=0, sticky="ew", padx=10, pady=2)
        return lbl

    def _przycisk(self, p, tekst, cmd, r, glowny=False, blokowany=True):
        b = ctk.CTkButton(p, text=tekst, command=cmd, height=34 if glowny else 30,
                          font=ctk.CTkFont(size=13, weight="bold" if glowny else "normal"))
        b.grid(row=r, column=0, sticky="ew", padx=10, pady=3)
        if blokowany:
            self._przyciski.append(b)
        return b

    def _dalej(self, p, r, nr):
        ctk.CTkButton(p, text=f"Dalej: {ZAKLADKI[nr]}  →", fg_color="transparent", border_width=1,
                      command=lambda: self.tabs.set(ZAKLADKI[nr])).grid(row=r, column=0, sticky="ew", padx=10, pady=(16, 8))

    # ── 1. dane ─────────────────────────────────────────────────────────────
    def _zakladka_dane(self, t):
        p = self._panel(t)
        self._naglowek(p, "Skąd obrazy", 0)
        self._tryb = ctk.CTkSegmentedButton(p, values=["Para z bazy", "Własne pliki"], command=self._zmien_tryb)
        self._tryb.grid(row=1, column=0, sticky="ew", padx=10, pady=4)
        self._tryb.set("Para z bazy")

        self._ramka_para = ctk.CTkFrame(p, fg_color="transparent")
        self._ramka_para.grid(row=2, column=0, sticky="ew")
        self._ramka_para.columnconfigure(1, weight=1)
        pary = [str(n) for n in dostepne_pary()]
        ctk.CTkLabel(self._ramka_para, text="Para nr").grid(row=0, column=0, padx=(10, 6), pady=6)
        self._cmb_para = ctk.CTkComboBox(self._ramka_para, values=pary or ["–"], width=90)
        self._cmb_para.grid(row=0, column=1, sticky="w", pady=6)
        self._cmb_para.set(pary[0] if pary else "–")
        ctk.CTkButton(self._ramka_para, text="◀", width=34, command=lambda: self._kolejna_para(-1)).grid(row=0, column=2, padx=2)
        ctk.CTkButton(self._ramka_para, text="▶", width=34, command=lambda: self._kolejna_para(1)).grid(row=0, column=3, padx=(2, 10))
        b = ctk.CTkButton(self._ramka_para, text="Wczytaj parę", height=34, font=ctk.CTkFont(size=13, weight="bold"),
                          command=self._wczytaj_pare)
        b.grid(row=1, column=0, columnspan=4, sticky="ew", padx=10, pady=4)
        self._przyciski.append(b)

        self._ramka_pliki = ctk.CTkFrame(p, fg_color="transparent")
        self._ramka_pliki.columnconfigure(0, weight=1)
        self._sciezka_rgb, self._sciezka_ter = ctk.StringVar(), ctk.StringVar()
        for i, (opis, zm, kat) in enumerate((("Zdjęcie RGB", self._sciezka_rgb, KATALOG_RGB),
                                             ("Obraz termowizyjny", self._sciezka_ter, KATALOG_TERMAL))):
            ctk.CTkLabel(self._ramka_pliki, text=opis, anchor="w").grid(row=3 * i, column=0, sticky="ew", padx=10, pady=(6, 0))
            ctk.CTkEntry(self._ramka_pliki, textvariable=zm, font=ctk.CTkFont(size=11)).grid(row=3 * i + 1, column=0, sticky="ew", padx=10)
            ctk.CTkButton(self._ramka_pliki, text="Wybierz plik...", height=28,
                          command=lambda z=zm, k=kat, o=opis: self._wybierz_plik(z, k, o)).grid(row=3 * i + 2, column=0, sticky="ew", padx=10, pady=3)
        b = ctk.CTkButton(self._ramka_pliki, text="Wczytaj pliki", height=34, font=ctk.CTkFont(size=13, weight="bold"),
                          command=self._wczytaj_pliki)
        b.grid(row=6, column=0, sticky="ew", padx=10, pady=(8, 4))
        self._przyciski.append(b)

        self._naglowek(p, "Informacje", 3)
        self._lbl_info = self._opis(p, "Nic nie wczytano.", 4, kolor=("gray20", "gray80"))
        self._naglowek(p, "Cały potok naraz", 5)
        self._opis(p, "Rejestracja, narożniki znacznika, znamię (PanDerm), przeniesienie, pomiary i raport "
                      "– jak potok_pary.py.", 6)
        self._btn_wszystko = self._przycisk(p, "Wykonaj wszystkie etapy", self._wszystkie_etapy, 7)
        self._dalej(p, 8, 1)

        prawa = ctk.CTkFrame(t, fg_color="transparent")
        prawa.grid(row=0, column=1, sticky="nsew")
        prawa.columnconfigure((0, 1), weight=1, uniform="p")
        prawa.rowconfigure(0, weight=1)
        self._pg_dane_rgb = Podglad(prawa, "Zdjęcie RGB")
        self._pg_dane_rgb.grid(row=0, column=0, sticky="nsew", padx=(0, 4), pady=4)
        self._pg_dane_ter = Podglad(prawa, "Termowizja", piksele=True)
        self._pg_dane_ter.grid(row=0, column=1, sticky="nsew", padx=(4, 0), pady=4)

    def _zmien_tryb(self, wartosc):
        if wartosc == "Para z bazy":
            self._ramka_pliki.grid_forget()
            self._ramka_para.grid(row=2, column=0, sticky="ew")
        else:
            self._ramka_para.grid_forget()
            self._ramka_pliki.grid(row=2, column=0, sticky="ew")

    def _kolejna_para(self, krok):
        pary = self._cmb_para.cget("values")
        if self._cmb_para.get() in pary:
            i = (pary.index(self._cmb_para.get()) + krok) % len(pary)
            self._cmb_para.set(pary[i])
            self._wczytaj_pare()

    def _wybierz_plik(self, zmienna, katalog, opis):
        p = filedialog.askopenfilename(title=f"Wybierz: {opis}", initialdir=str(katalog),
                                       filetypes=[("Obrazy", "*.jpg *.jpeg *.png *.bmp *.tif"), ("Wszystkie", "*.*")])
        if p:
            zmienna.set(p)

    def _wczytaj_pare(self):
        n = self._cmb_para.get().strip()
        if not n.isdigit():
            messagebox.showerror("Błąd", "Podaj numer pary.")
            return
        self._ustaw_analize(lambda: Analiza.z_pary(int(n)))

    def _wczytaj_pliki(self):
        r, t = self._sciezka_rgb.get().strip(), self._sciezka_ter.get().strip()
        if not (r and Path(r).exists() and t and Path(t).exists()):
            messagebox.showerror("Błąd", "Wybierz istniejące zdjęcie i obraz termowizyjny.")
            return
        self._ustaw_analize(lambda: Analiza(r, t))

    def _ustaw_analize(self, utworz):
        if self._zajete:
            return
        try:
            a = utworz()
        except (BladEtapu, OSError) as e:
            messagebox.showerror("Błąd wczytania", str(e))
            return
        self.a, self._wyrownany, self._raport, self._obrazy_raportu = a, None, None, {}
        self._pg_dane_rgb.ustaw(a.rgb)
        self._pg_dane_ter.ustaw(a.termal)
        for pg in (self._pg_rej, self._pg_seg, self._pg_prz_rgb, self._pg_prz_ter, self._pg_raport):
            pg.wyczysc()
        self._pg_seg.ustaw(a.rgb)
        self._pg_prz_ter.ustaw(a.termal)
        self._lbl_rej.configure(text="")
        self._lbl_nar.configure(text="")
        self._lbl_zn.configure(text="")
        self._lbl_prz.configure(text="")
        self._pokaz_pomiary()
        i = a.info
        linie = [f"Para {a.para}" if a.para is not None else "Własne pliki",
                 f"Zdjęcie: {i.get('rgb_oryginal', a.rgb_path.name)}  ({a.rgb.shape[1]}×{a.rgb.shape[0]} px)",
                 f"Termowizja: {i.get('termal_nagranie', a.ter_path.name)}  ({a.termal.shape[1]}×{a.termal.shape[0]} px)"]
        if "znamie" in i:
            linie.append(f"Znamię nr {i['znamie']}, fold {i['fold']}")
        linie.append("Adnotacje z CVAT: " + ("są (tylko do oceny wyników)" if a.wzorzec is not None else "brak"))
        if (a.folder_rejestracji / "dopasowanie_macierz.txt").exists():
            linie.append("Jest zapisana rejestracja (można ją wczytać w kroku 2).")
        self._lbl_info.configure(text="\n".join(linie))
        self._lbl_para.configure(text=linie[0] + (" · CVAT" if a.wzorzec is not None else ""))
        self._lbl_folder.configure(text=self._wzgledna(a.folder))
        self._log_wyczysc()
        self._status(f"Wczytano: {linie[0]}. Następny krok: rejestracja.", OK)
        self._odswiez_stan()

    # ── 2. rejestracja ──────────────────────────────────────────────────────
    def _zakladka_rejestracja(self, t):
        p = self._panel(t)
        self._naglowek(p, "Rejestracja (dopasowanie3.py)", 0)
        self._opis(p, "Znacznik Π jest wykrywany automatycznie na obu obrazach (bez adnotacji), a jego kształty są "
                      "dopasowywane – wynik to macierz T: piksel zdjęcia → piksel termowizji.", 1)
        self._opis(p, f"Model przekształcenia: {dopasowanie.MODEL} (ustawienie MODEL w dopasowanie3.py).", 2,
                   kolor=("gray20", "gray80"))
        self._btn_rej = self._przycisk(p, "Uruchom rejestrację", self._rejestruj, 4, glowny=True)
        self._btn_rej_wczytaj = self._przycisk(p, "Wczytaj zapisaną rejestrację", self._wczytaj_rejestracje, 5)
        self._lbl_rej = self._opis(p, "", 6, kolor=("gray20", "gray80"))
        self._naglowek(p, "Nałożenie", 7)
        self._lbl_przezr = ctk.CTkLabel(p, text="Przezroczystość termowizji: 50 %", anchor="w")
        self._lbl_przezr.grid(row=8, column=0, sticky="ew", padx=10)
        self._suwak = ctk.CTkSlider(p, from_=0, to=100, number_of_steps=100, command=self._zmien_przezroczystosc)
        self._suwak.set(50)
        self._suwak.grid(row=9, column=0, sticky="ew", padx=10, pady=4)
        self._opis(p, "0 % = sama termowizja, 100 % = samo zdjęcie. Zielony: znacznik wykryty na zdjęciu, "
                      "fioletowy: znacznik z termowizji przeniesiony przez T⁻¹.", 10)
        self._btn_zapisz_nal = self._przycisk(p, "Zapisz nałożenie...", self._zapisz_nalozenie, 11)
        self._przycisk(p, "Otwórz folder rejestracji", lambda: self._otworz_folder(self.a and self.a.folder_rejestracji), 12, blokowany=False)
        self._dalej(p, 13, 2)
        self._pg_rej = Podglad(t, "Zdjęcie z nałożoną termowizją")
        self._pg_rej.grid(row=0, column=1, sticky="nsew", pady=4)

    def _rejestruj(self):
        self._log_wyczysc()
        self._w_tle("Rejestracja", lambda: self.a.rejestruj(log=QueueWriter(self._q)), self._po_rejestracji)

    def _wczytaj_rejestracje(self):
        self._w_tle("Wczytanie rejestracji", self.a.wczytaj_rejestracje, self._po_rejestracji)

    def _po_rejestracji(self, rej):
        a = self.a
        self._wyrownany = imread(a.plik_wyrownany, cv2.IMREAD_UNCHANGED)
        widok = None
        if a.maska_znacznika_rgb is not None and a.maska_znacznika_rgb.any():
            x, y, w, h = cv2.boundingRect(a.maska_znacznika_rgb)
            widok = ramka(np.array([[x, y], [x + w, y + h]]), a.rgb.shape, 0.3)
        self._pg_rej.ustaw(a.rgb, self._wyrownany, widok)
        nak = []
        if a.maska_znacznika_rgb is not None:
            nak += [dict(pkt=k, kolor=ZIELONY) for k in geo.kontury(a.maska_znacznika_rgb)]
        if a.maska_znacznika_termal is not None:
            Mi = np.linalg.inv(a.M)
            nak += [dict(pkt=geo.przenies_punkty(k, Mi), kolor=FIOLET) for k in geo.kontury(a.maska_znacznika_termal)]
        self._pg_rej.ustaw_nakladki(nak)
        self._lbl_rej.configure(text=f"Wybrany model: {rej.get('model', '–')}\n"
                                     f"Kontrola wewnętrzna: Dice {_f(rej.get('dice_wewnetrzny'), 4)}, "
                                     f"błąd krawędzi {_f(rej.get('blad_krawedzi_px'))} px termowizji\n"
                                     f"Folder: {rej.get('folder', '')}")
        self._odswiez_widoki()

    def _zmien_przezroczystosc(self, v):
        self._lbl_przezr.configure(text=f"Przezroczystość termowizji: {int(round(float(v)))} %")
        self._pg_rej.ustaw_alfa(float(v) / 100)
        self._pg_prz_rgb.ustaw_alfa(float(v) / 100)

    def _zapisz_nalozenie(self):
        if self._wyrownany is None:
            return
        proc = int(round(self._suwak.get()))
        p = filedialog.asksaveasfilename(title="Zapisz nałożenie jako", initialdir=str(self.a.folder_rejestracji),
                                         initialfile=f"nalozenie_{proc}.png", defaultextension=".png",
                                         filetypes=[("PNG", "*.png"), ("JPEG", "*.jpg")])
        if p and dopasowanie.imwrite(p, dopasowanie.nalozenie(self.a.rgb, self._wyrownany, proc / 100)):
            self._status(f"Zapisano: {Path(p).name}", OK)

    # ── 3. segmentacja ──────────────────────────────────────────────────────
    def _zakladka_segmentacja(self, t):
        p = self._panel(t)
        self._naglowek(p, "Znacznik i znamię", 0)
        self._opis(p, "Narożniki znacznika: wzorzec Π (35 × 26 mm, pasek 9 mm) dopasowany do maski znacznika "
                      "z rejestracji → skala w mm. Znamię: model PanDerm we wnętrzu znacznika (osobne środowisko "
                      "modeli z PyTorch; pierwsze uruchomienie wczytuje wagi).", 1)
        self._btn_seg = self._przycisk(p, "Wyznacz narożniki i znamię", self._segmentuj, 2, glowny=True)
        self._naglowek(p, "Narożniki", 3)
        self._lbl_nar = self._opis(p, "", 4, kolor=("gray20", "gray80"))
        self._naglowek(p, "Znamię", 5)
        self._lbl_zn = self._opis(p, "", 6, kolor=("gray20", "gray80"))
        self._opis(p, "Kolory: zielony – znacznik i narożniki 0–7, czerwony – znamię z PanDerm, niebieski – znamię "
                      "z CVAT (tylko do porównania, gdy para ma adnotacje).", 7)
        self._dalej(p, 8, 3)
        self._pg_seg = Podglad(t, "Zdjęcie: narożniki znacznika i znamię")
        self._pg_seg.grid(row=0, column=1, sticky="nsew", pady=4)

    def _segmentuj(self):
        a, log = self.a, QueueWriter(self._q)

        def zadanie():
            a.ustaw_narozniki()
            return a.segmentuj_znamie(log)
        self._w_tle("Narożniki i znamię (PanDerm)", zadanie, lambda _: self._odswiez_widoki())

    # ── 4. przeniesienie ROI ────────────────────────────────────────────────
    def _zakladka_przeniesienie(self, t):
        p = self._panel(t)
        self._naglowek(p, "Zdjęcie → termowizja (T)", 0)
        self._opis(p, "Obrys znamienia, obrys i otwór znacznika oraz 8 narożników przechodzą przez macierz T "
                      "na obraz termowizyjny.", 1)
        self._btn_prz = self._przycisk(p, "Przenieś na termowizję", self._przenies, 2, glowny=True)
        self._lbl_prz = self._opis(p, "", 3, kolor=("gray20", "gray80"))
        self._naglowek(p, "Widok zdjęcia", 10)
        self._widok_prz = ctk.CTkSegmentedButton(p, values=["Zdjęcie", "Nałożenie"], command=lambda _: self._odswiez_widoki())
        self._widok_prz.set("Zdjęcie")
        self._widok_prz.grid(row=11, column=0, sticky="ew", padx=10, pady=4)
        self._opis(p, "Kolory: zielony – znacznik ze zdjęcia, fioletowy – znacznik na termowizji (z CVAT, gdy para "
                      "ma adnotacje), czerwony – znamię. Przezroczystość nałożenia: suwak w kroku 2.", 12)
        self._dalej(p, 13, 4)
        prawa = ctk.CTkFrame(t, fg_color="transparent")
        prawa.grid(row=0, column=1, sticky="nsew")
        prawa.columnconfigure((0, 1), weight=1, uniform="p")
        prawa.rowconfigure(0, weight=1)
        self._pg_prz_rgb = Podglad(prawa, "Zdjęcie")
        self._pg_prz_rgb.grid(row=0, column=0, sticky="nsew", padx=(0, 4), pady=4)
        self._pg_prz_ter = Podglad(prawa, "Termowizja", piksele=True)
        self._pg_prz_ter.grid(row=0, column=1, sticky="nsew", padx=(4, 0), pady=4)

    def _przenies(self):
        self._w_tle("Przeniesienie ROI", self.a.przenies, lambda _: self._odswiez_widoki())

    # ── 5. pomiary ──────────────────────────────────────────────────────────
    def _zakladka_pomiary(self, t):
        p = self._panel(t)
        self._naglowek(p, "Pomiary i zgodność", 0)
        self._opis(p, "Wymiary i kolor znamienia w mm (skala z narożników znacznika), kontrola skali obu "
                      "modalności i – gdy są adnotacje z CVAT – ocena rejestracji (badanie E1) i maski PanDerm.", 1)
        self._btn_pom = self._przycisk(p, "Oblicz pomiary i zgodność", self._zmierz, 2, glowny=True)
        self._lbl_uwagi = self._opis(p, "", 3, kolor=PRACA)
        self._opis(p, "Kliknij nazwę wielkości w tabeli, żeby zobaczyć jej dokładne objaśnienie.", 4)
        self._dalej(p, 5, 5)
        prawa = ctk.CTkFrame(t, fg_color="transparent")
        prawa.grid(row=0, column=1, sticky="nsew")
        prawa.columnconfigure(0, weight=1)
        prawa.rowconfigure(0, weight=1)
        self._tabela = ctk.CTkScrollableFrame(prawa, fg_color=KOLOR_TLO_PANEL, corner_radius=10)
        self._tabela.grid(row=0, column=0, sticky="nsew", pady=4)
        self._tabela.columnconfigure(2, weight=1)
        self._objasnienie = ctk.CTkTextbox(prawa, height=130, wrap="word", font=ctk.CTkFont(size=13))
        self._objasnienie.grid(row=1, column=0, sticky="ew", pady=(4, 4))
        self._ustaw_objasnienie("Objaśnienie", "Kliknij nazwę wielkości w tabeli.")

    def _zmierz(self):
        self._w_tle("Pomiary", self.a.zmierz, lambda _: (self._pokaz_pomiary(), self._odswiez_widoki()))

    def _ustaw_objasnienie(self, tytul, tekst):
        o = self._objasnienie
        o.configure(state="normal")
        o.delete("1.0", "end")
        o.insert("end", tytul + "\n", "tytul")
        o.insert("end", tekst)
        o.tag_config("tytul", foreground="#5aa9ff")
        o.configure(state="disabled")

    def _pokaz_pomiary(self):
        for w in self._tabela.winfo_children():
            w.destroy()
        a = self.a
        if a is None or a.wyniki is None:
            ctk.CTkLabel(self._tabela, text="Brak wyników – wykonaj kroki 2–4 i kliknij „Oblicz pomiary i zgodność”.",
                         text_color=SZARY).grid(row=0, column=0, columnspan=3, padx=10, pady=10, sticky="w")
            self._lbl_uwagi.configure(text="")
            return
        w = a.wyniki
        u = raport.uwagi(w)
        self._lbl_uwagi.configure(text=("Uwagi:\n• " + "\n• ".join(u)) if u else "Brak uwag.", text_color=PRACA if u else OK)
        r = 0
        for tytul, wstep, wiersze in raport.sekcje(w):
            ctk.CTkLabel(self._tabela, text=tytul, anchor="w", font=ctk.CTkFont(size=14, weight="bold")).grid(
                row=r, column=0, columnspan=3, sticky="ew", padx=10, pady=(12, 2))
            r += 1
            if wstep:
                ctk.CTkLabel(self._tabela, text=wstep, anchor="w", justify="left", wraplength=760, text_color=SZARY).grid(
                    row=r, column=0, columnspan=3, sticky="ew", padx=10)
                r += 1
            for klucz, nazwa, wartosc, skrot in wiersze:
                b = ctk.CTkButton(self._tabela, text=nazwa, anchor="w", fg_color="transparent", text_color="#5aa9ff",
                                  hover_color=("gray80", "gray30"), height=24,
                                  command=lambda k=klucz: self._ustaw_objasnienie(*raport.objasnienie(k)[1:]))
                b.grid(row=r, column=0, sticky="ew", padx=(6, 4))
                ctk.CTkLabel(self._tabela, text=wartosc, anchor="w", font=ctk.CTkFont(size=13, weight="bold")).grid(
                    row=r, column=1, sticky="w", padx=8)
                ctk.CTkLabel(self._tabela, text=skrot, anchor="w", justify="left", wraplength=430, text_color=SZARY).grid(
                    row=r, column=2, sticky="ew", padx=8)
                r += 1

    # ── 6. raport ───────────────────────────────────────────────────────────
    def _zakladka_raport(self, t):
        p = self._panel(t)
        self._naglowek(p, "Raport pary", 0)
        self._opis(p, "Zapisuje raport.html (z obrazami i objaśnieniem wszystkich wielkości), metryki.json "
                      "i obrazy PNG. Pomiary są liczone, jeśli jeszcze ich nie ma.", 1)
        ctk.CTkLabel(p, text="Folder wyników", anchor="w").grid(row=2, column=0, sticky="ew", padx=10, pady=(8, 0))
        self._lbl_folder = self._opis(p, "–", 3, kolor=("gray20", "gray80"))
        self._przycisk(p, "Zmień folder...", self._zmien_folder, 4)
        self._btn_raport = self._przycisk(p, "Zapisz raport", self._zapisz_raport, 5, glowny=True)
        self._btn_otworz_raport = self._przycisk(p, "Otwórz raport", lambda: self._raport and otworz(self._raport), 6)
        self._przycisk(p, "Otwórz folder wyników", lambda: self._otworz_folder(self.a and self.a.folder), 7, blokowany=False)
        self._lbl_raport = self._opis(p, "", 8, kolor=("gray20", "gray80"))
        self._naglowek(p, "Podgląd obrazów raportu", 9)
        self._wybor_obrazu = ctk.CTkSegmentedButton(p, values=["Zdjęcie", "Termowizja", "Nałożenie", "Zbliżenie"],
                                                    command=self._pokaz_obraz_raportu)
        self._wybor_obrazu.set("Nałożenie")
        self._wybor_obrazu.grid(row=10, column=0, sticky="ew", padx=10, pady=4)
        self._pg_raport = Podglad(t, "Obraz z raportu")
        self._pg_raport.grid(row=0, column=1, sticky="nsew", pady=4)

    def _zmien_folder(self):
        if self.a is None:
            return
        p = filedialog.askdirectory(title="Folder wyników", initialdir=str(self.a.folder.parent))
        if p:
            self.a.folder = Path(p)
            self._lbl_folder.configure(text=self._wzgledna(self.a.folder))

    def _zapisz_raport(self):
        self._w_tle("Raport", lambda: (self.a.zapisz_raport(), self.a.ostatnie_obrazy), self._po_raporcie)

    def _po_raporcie(self, wynik):
        self._raport, self._obrazy_raportu = wynik
        self._lbl_raport.configure(text=f"Zapisano:\n{self._wzgledna(self._raport)}\n+ metryki.json, "
                                        f"{', '.join(n + '.png' for n in self._obrazy_raportu)}")
        self._pokaz_pomiary()
        self._pokaz_obraz_raportu(self._wybor_obrazu.get())

    def _pokaz_obraz_raportu(self, nazwa):
        klucz = {"Zdjęcie": "rgb", "Termowizja": "termal", "Nałożenie": "nakladka", "Zbliżenie": "nakladka_zblizenie"}[nazwa]
        img = self._obrazy_raportu.get(klucz)
        if img is not None:
            self._pg_raport.ustaw(img, widok=(0, 0, img.shape[1], img.shape[0]))

    # ── wszystkie etapy naraz ───────────────────────────────────────────────
    def _wszystkie_etapy(self):
        a, log = self.a, QueueWriter(self._q)

        def zadanie():
            analizuj(a, log)
            return a.zapisz_raport(), a.ostatnie_obrazy

        def po(wynik):
            self._po_rejestracji(a.rej)
            self._po_raporcie(wynik)
            self.tabs.set(ZAKLADKI[5])

        self._log_wyczysc()
        self._w_tle("Wszystkie etapy", zadanie, po)

    # ── widoki z nakladkami ─────────────────────────────────────────────────
    def _odswiez_widoki(self):
        a = self.a
        if a is None:
            return
        Mi = np.linalg.inv(a.M) if a.M is not None else None
        nar_t_ref = a.wzorzec["narozniki_termal"] if a.wzorzec is not None else a.narozniki_termal
        # krok 3: zdjecie
        nak = []
        if a.narozniki_rgb is not None:
            nak.append(dict(pkt=a.narozniki_rgb, kolor=ZIELONY, punkty=True, etykiety=True))
        if a.maska_znamie is not None:
            nak += [dict(pkt=k, kolor=CZERWONY) for k in geo.kontury(a.maska_znamie)]
        seg_nak = list(nak)
        if a.maska_znamie is not None and a.wzorzec is not None:
            seg_nak += [dict(pkt=k, kolor=NIEBIESKI, grubosc=1) for k in geo.kontury(a.wzorzec["maska_znamie_rgb"])]
        self._pg_seg.ustaw_nakladki(seg_nak)
        kadr_rgb = ramka(a.narozniki_rgb, a.rgb.shape, 0.25) if a.narozniki_rgb is not None else None
        if kadr_rgb:
            self._pg_seg.przybliz_jesli_calosc(kadr_rgb)
        # krok 4: zdjecie (albo nalozenie) i termowizja
        rgb_nak = list(nak)
        if Mi is not None and nar_t_ref is not None:
            rgb_nak.append(dict(pkt=geo.przenies_punkty(nar_t_ref, Mi), kolor=FIOLET))
        warstwa = self._wyrownany if self._widok_prz.get() == "Nałożenie" else None
        self._pg_prz_rgb.alfa = self._suwak.get() / 100
        self._pg_prz_rgb.ustaw(a.rgb, warstwa)
        self._pg_prz_rgb.ustaw_nakladki(rgb_nak)
        if kadr_rgb:
            self._pg_prz_rgb.przybliz_jesli_calosc(kadr_rgb)
        ter_nak = []
        if nar_t_ref is not None:
            ter_nak.append(dict(pkt=nar_t_ref, kolor=FIOLET, punkty=True))
        pr = a.przeniesione
        if pr is not None:
            ter_nak.append(dict(pkt=pr["narozniki"], kolor=ZIELONY))
            ter_nak += [dict(pkt=k, kolor=CZERWONY) for k in pr["kontury_znamienia"]]
        self._pg_prz_ter.ustaw_nakladki(ter_nak)
        if nar_t_ref is not None:
            self._pg_prz_ter.przybliz_jesli_calosc(ramka(nar_t_ref, a.termal.shape, 0.3))
        # opisy
        if a.H_rgb is not None:
            d = a.dopasowanie_naroznikow
            s = geo.mm_na_px(a.H_rgb, a.narozniki_rgb.mean(0))
            tekst = (f"IoU wzorca z maską znacznika: {_f(d.get('rgb_iou_wzorca'), 3)} (zdjęcie), "
                     f"{_f(d.get('termal_iou_wzorca'), 3)} (termowizja)\nSkala zdjęcia: {_f(s, 4)} mm/px")
            if a.wzorzec is not None:
                from analiza import miary
                b = miary.tre(a.narozniki_rgb, a.wzorzec["narozniki_rgb"], a.wzorzec["H_rgb"])["tre_srednie"]
                tekst += f"\nOdległość od narożników z CVAT: średnio {_f(b)} mm"
            self._lbl_nar.configure(text=tekst)
        else:
            self._lbl_nar.configure(text="")
        if a.maska_znamie is not None:
            px = int((a.maska_znamie > 0).sum())
            tekst = f"{OPIS_ZNAMIENIA}: {px} px"
            if a.H_rgb is not None:
                c = np.argwhere(a.maska_znamie > 0).mean(0)[::-1]
                pole = px * geo.mm_na_px(a.H_rgb, c) ** 2
                tekst += f" ≈ {_f(pole)} mm², średnica równoważna {_f(2 * np.sqrt(pole / np.pi))} mm"
                if a.wzorzec is not None:
                    pc = int((a.wzorzec["maska_znamie_rgb"] > 0).sum()) * geo.mm_na_px(a.H_rgb, c) ** 2
                    tekst += f"\nZnamię z CVAT (do porównania): ≈ {_f(pc)} mm²"
            self._lbl_zn.configure(text=tekst)
        else:
            self._lbl_zn.configure(text="")
        if pr is not None:
            ul = pr["ulamek"]
            s_t = geo.mm_na_px(a.H_termal, a.narozniki_termal.mean(0))
            self._lbl_prz.configure(text=f"Znamię na termowizji: {_f(float(ul.sum()), 1)} px "
                                         f"(≈ {_f(float(ul.sum()) * s_t ** 2)} mm²)\nPiksel termowizji: {_f(s_t, 3)} mm")
        else:
            self._lbl_prz.configure(text="")
        self._odswiez_stan()

    # ── zadania w tle, stan przyciskow ──────────────────────────────────────
    def _w_tle(self, opis, zadanie, po_sukcesie=None):
        if self._zajete or self.a is None:
            return
        self._zajete = True
        self._ustaw_przyciski(False)
        self._bar.configure(mode="indeterminate")
        self._bar.start()
        self._status(f"{opis}...", PRACA)

        def watek():
            try:
                self._q.put(("ok", opis, zadanie(), po_sukcesie))
            except BladEtapu as e:
                self._q.put(("blad", opis, str(e)))
            except Exception as e:                       # noqa: BLE001 - pokazujemy kazdy blad w oknie
                self._q.put(traceback.format_exc())
                self._q.put(("blad", opis, f"{type(e).__name__}: {e}"))

        threading.Thread(target=watek, daemon=True).start()

    def _odpytuj(self):
        try:
            while True:
                msg = self._q.get_nowait()
                if isinstance(msg, str):
                    self._log_dopisz(msg)
                    continue
                self._zajete = False
                self._bar.stop()
                self._bar.configure(mode="determinate")
                self._bar.set(0)
                if msg[0] == "ok":
                    _, opis, wynik, po = msg
                    self._status(f"{opis} – gotowe ✔", OK)
                    if po:
                        try:
                            po(wynik)
                        except Exception as e:           # noqa: BLE001
                            self._log_dopisz(traceback.format_exc())
                            messagebox.showerror(opis, f"{type(e).__name__}: {e}")
                else:
                    _, opis, tekst = msg
                    self._status(f"{opis} – błąd", BLAD)
                    self._log_dopisz(f"BŁĄD ({opis}): {tekst}\n")
                    messagebox.showerror(opis, tekst)
                self._odswiez_stan()
        except queue.Empty:
            pass
        self.after(80, self._odpytuj)

    def _ustaw_przyciski(self, wlaczone):
        for b in self._przyciski:
            b.configure(state="normal" if wlaczone else "disabled")

    def _odswiez_stan(self):
        a = self.a
        wolne = not self._zajete
        self._ustaw_przyciski(wolne)
        if a is not None and a.wyniki is None:
            self._raport = None                          # wyniki policzone od nowa -> raport nieaktualny
        st = a.stan() if a is not None else {}
        st["raport"] = self._raport is not None
        if wolne:
            def wl(b, warunek):
                b.configure(state="normal" if warunek else "disabled")
            jest = a is not None
            wl(self._btn_rej, jest)
            wl(self._btn_rej_wczytaj, jest and (a.folder_rejestracji / "dopasowanie_macierz.txt").exists())
            wl(self._btn_zapisz_nal, self._wyrownany is not None)
            wl(self._btn_wszystko, jest)
            wl(self._btn_seg, jest and a.M is not None)
            wl(self._btn_prz, jest and a.M is not None and a.H_rgb is not None and a.maska_znamie is not None)
            wl(self._btn_pom, jest and a.przeniesione is not None)
            wl(self._btn_raport, jest and a.przeniesione is not None)
            wl(self._btn_otworz_raport, self._raport is not None)
        nastepny = next((i for i, e in enumerate(ETAPY) if not st.get(e)), None)
        for i, (b, e) in enumerate(zip(self._chipy, ETAPY)):
            if st.get(e):
                b.configure(fg_color=("#9be3bd", "#1f6b45"), text=f"✔ {ZAKLADKI[i]}")
            elif i == nastepny:
                b.configure(fg_color=("#f3d39a", "#7a5a12"), text=ZAKLADKI[i])
            else:
                b.configure(fg_color=("gray75", "gray25"), text=ZAKLADKI[i])

    def _status(self, tekst, kolor=SZARY):
        self._lbl_status.configure(text=tekst, text_color=kolor)

    def _log_dopisz(self, tekst):
        self._log.configure(state="normal")
        self._log.insert("end", tekst)
        self._log.see("end")
        self._log.configure(state="disabled")

    def _log_wyczysc(self):
        self._log.configure(state="normal")
        self._log.delete("1.0", "end")
        self._log.configure(state="disabled")

    @staticmethod
    def _wzgledna(p):
        try:
            return Path(p).resolve().relative_to(INZ.resolve()).as_posix()
        except ValueError:
            return str(p)

    def _otworz_folder(self, folder):
        if folder and Path(folder).exists():
            otworz(folder)
        else:
            messagebox.showinfo("Folder", "Folder jeszcze nie istnieje – najpierw wykonaj ten krok.")


if __name__ == "__main__":
    Aplikacja().mainloop()
