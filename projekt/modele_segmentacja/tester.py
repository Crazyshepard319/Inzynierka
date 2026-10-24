"""
Aplikacja do testowania modeli segmentacji znamion.

Uruchomienie: uruchom_tester.bat  (albo z folderu Inzynierka/projekt:
    <modele_dane>\\srodowisko\\Scripts\\python.exe -m modele_segmentacja.tester)

Obsluga podgladu:
  kolko myszy          - przyblizanie / oddalanie
  przeciaganie LPM     - przesuwanie (gdy nie zaznaczasz obszaru ani nie rysujesz)
  tryb "Zaznacz obszar"- przeciagnij prostokat wokol znamienia
  "Ze znacznika Π"     - obszar = wnetrze znacznika (szukany tez automatycznie po wczytaniu);
                         maska znamienia jest ograniczana do wnetrza
  tryb "Rysuj wzorzec" - klikaj punkty wokol znamienia, PPM / Enter zamyka obrys,
                         Backspace cofa punkt, Esc anuluje
"""
import csv
import queue
import sys
import threading
import time
from datetime import datetime
from pathlib import Path
from tkinter import filedialog, messagebox
import tkinter as tk

import cv2
import customtkinter as ctk
import numpy as np
from PIL import Image, ImageTk

if __package__ in (None, ""):          # uruchomienie jako skrypt: python tester.py
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    __package__ = "modele_segmentacja"

from modele_segmentacja import dostepne_modele, metryki
from modele_segmentacja.interfejs import wczytaj_obraz, zapisz_obraz
from modele_segmentacja.konfiguracja import WYNIKI

try:
    from modele_segmentacja.znacznik import BrakZnacznika, wykryj_znacznik
    _BLAD_ZNACZNIKA = ""
except Exception as _e:          # np. brak dopasowanie3.py obok folderu modele_segmentacja
    BrakZnacznika, wykryj_znacznik, _BLAD_ZNACZNIKA = RuntimeError, None, str(_e)

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

KOLORY = [(0, 200, 255), (255, 220, 0), (255, 90, 255), (80, 160, 255), (0, 120, 255)]   # BGR
KOLOR_WZORCA = (60, 230, 60)
KOLOR_PANEL = ("#e8e8e8", "#2b2b2b")


def hex_bgr(c):
    return "#%02x%02x%02x" % (c[2], c[1], c[0])


class Tester(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Segmentacja znamion - tester modeli")
        self.geometry("1440x900")
        self.minsize(1100, 700)

        self.obraz = None          # BGR, pelna rozdzielczosc
        self.sciezka = None
        self.roi = None            # (x, y, w, h)
        self.znacznik = None       # znacznik.Znacznik, gdy obszar = wnetrze znacznika
        self._kz = None            # cache konturow znacznika
        self.wzorzec = None        # uint8 0/255
        self.wyniki = {}           # klucz -> WynikSegmentacji
        self.modele = {m.klucz: m for m in dostepne_modele()}
        self.kolor = {k: KOLORY[i % len(KOLORY)] for i, k in enumerate(self.modele)}
        self._kontury = {}         # cache konturow: klucz -> lista konturow
        self._q = queue.Queue()
        self._zajety = False
        self._ostrzezenia = []

        # widok: skala (px ekranu / px obrazu) i lewy gorny rog w ukladzie obrazu
        self.skala, self.ox, self.oy = 1.0, 0.0, 0.0
        self.tryb = None           # None | "roi" | "rysuj"
        self._punkty = []          # rysowany obrys (wsp. obrazu)
        self._start = None

        self._buduj()
        self.after(100, self._odpytuj)

    # ── interfejs ────────────────────────────────────────────────────────────

    def _buduj(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.plotno = tk.Canvas(self, bg="#161616", highlightthickness=0, cursor="crosshair")
        self.plotno.grid(row=0, column=0, sticky="nsew", padx=(12, 6), pady=12)
        self.plotno.bind("<Configure>", lambda e: self._rysuj())
        self.plotno.bind("<MouseWheel>", self._kolko)
        self.plotno.bind("<ButtonPress-1>", self._lpm_wcisniety)
        self.plotno.bind("<B1-Motion>", self._lpm_ruch)
        self.plotno.bind("<ButtonRelease-1>", self._lpm_puszczony)
        self.plotno.bind("<ButtonPress-2>", self._pan_start)
        self.plotno.bind("<B2-Motion>", self._pan_ruch)
        self.plotno.bind("<Button-3>", lambda e: self._zamknij_obrys())
        self.plotno.bind("<Motion>", self._ruch)
        self.bind("<Return>", lambda e: self._zamknij_obrys())
        self.bind("<BackSpace>", lambda e: self._cofnij_punkt())
        self.bind("<Escape>", lambda e: self._anuluj())

        p = ctk.CTkScrollableFrame(self, width=370, fg_color="transparent")
        p.grid(row=0, column=1, sticky="ns", padx=(6, 12), pady=12)
        B = dict(height=32)

        def sekcja(tytul):
            f = ctk.CTkFrame(p, fg_color=KOLOR_PANEL, corner_radius=10)
            f.pack(fill="x", pady=(0, 10))
            ctk.CTkLabel(f, text=tytul, font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", padx=12, pady=(8, 4))
            return f

        f = sekcja("Zdjecie")
        ctk.CTkButton(f, text="Wczytaj zdjecie...", command=self._wczytaj_obraz, **B).pack(fill="x", padx=12)
        self.lbl_obraz = ctk.CTkLabel(f, text="(brak)", text_color="gray", font=ctk.CTkFont(size=11),
                                      wraplength=330, justify="left")
        self.lbl_obraz.pack(anchor="w", padx=12, pady=(4, 10))

        f = sekcja("Obszar analizy")
        r = ctk.CTkFrame(f, fg_color="transparent"); r.pack(fill="x", padx=12)
        self.btn_roi = ctk.CTkButton(r, text="Zaznacz obszar", command=lambda: self._ustaw_tryb("roi"), **B)
        self.btn_roi.pack(side="left", expand=True, fill="x", padx=(0, 4))
        ctk.CTkButton(r, text="Caly obraz", command=self._caly_obraz, **B).pack(side="left", expand=True, fill="x")
        r = ctk.CTkFrame(f, fg_color="transparent"); r.pack(fill="x", padx=12, pady=(6, 0))
        ctk.CTkButton(r, text="Ze znacznika \u03a0", command=self._szukaj_znacznika, **B).pack(
            side="left", expand=True, fill="x", padx=(0, 4))
        self.auto_znacznik = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(r, text="szukaj po wczytaniu", variable=self.auto_znacznik,
                        font=ctk.CTkFont(size=11)).pack(side="left", expand=True, fill="x")
        r = ctk.CTkFrame(f, fg_color="transparent"); r.pack(fill="x", padx=12, pady=(6, 0))
        ctk.CTkButton(r, text="Przybliz do obszaru", command=self._przybliz_roi, **B).pack(side="left", expand=True, fill="x", padx=(0, 4))
        ctk.CTkButton(r, text="Dopasuj widok", command=self._dopasuj, **B).pack(side="left", expand=True, fill="x")
        self.lbl_roi = ctk.CTkLabel(f, text="Zaznacz prostokat wokol znamienia (model widzi tylko ten obszar).",
                                    text_color="gray", font=ctk.CTkFont(size=11), wraplength=330, justify="left")
        self.lbl_roi.pack(anchor="w", padx=12, pady=(4, 10))

        f = sekcja("Modele")
        self.wybor = {}
        for k, m in self.modele.items():
            ok, powod = m.dostepnosc()
            v = ctk.BooleanVar(value=ok)
            cb = ctk.CTkCheckBox(f, text=m.nazwa, variable=v, state="normal" if ok else "disabled",
                                 text_color=hex_bgr(self.kolor[k]) if ok else "gray",
                                 font=ctk.CTkFont(size=12, weight="bold"))
            cb.pack(anchor="w", padx=12, pady=(2, 0))
            ctk.CTkLabel(f, text=m.opis if ok else f"Niedostepny: {powod}", text_color="gray",
                         font=ctk.CTkFont(size=10), wraplength=280, justify="left").pack(anchor="w", padx=(40, 12))
            self.wybor[k] = v
        self.przyblizaj = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(f, text="Automatyczne przyblizenie do znamienia", variable=self.przyblizaj,
                        font=ctk.CTkFont(size=11)).pack(anchor="w", padx=12, pady=(8, 0))
        ctk.CTkLabel(f, text="Kadr jak w danych uczacych (ISIC): znamie ~1/2 kadru, 2-3 przebiegi. "
                             "Przerywana ramka = kadr, na ktorym liczyl model.",
                     text_color="gray", font=ctk.CTkFont(size=10), wraplength=280,
                     justify="left").pack(anchor="w", padx=(40, 12))
        self.btn_seg = ctk.CTkButton(f, text="Segmentuj", command=self._segmentuj, height=38,
                                     font=ctk.CTkFont(size=14, weight="bold"))
        self.btn_seg.pack(fill="x", padx=12, pady=(10, 4))
        self.lbl_status = ctk.CTkLabel(f, text="", text_color="gray", font=ctk.CTkFont(size=11),
                                       wraplength=330, justify="left")
        self.lbl_status.pack(anchor="w", padx=12, pady=(0, 10))

        f = sekcja("Wyniki")
        self.tabela = ctk.CTkTextbox(f, height=150, font=ctk.CTkFont(family="Courier New", size=11),
                                     fg_color="#161616", wrap="word")
        self.tabela.pack(fill="x", padx=12)
        self.tabela.configure(state="disabled")
        ctk.CTkButton(f, text="Zapisz wyniki", command=self._zapisz_wyniki, **B).pack(fill="x", padx=12, pady=10)

        f = sekcja("Maska wzorcowa (do metryk)")
        r = ctk.CTkFrame(f, fg_color="transparent"); r.pack(fill="x", padx=12)
        ctk.CTkButton(r, text="Wczytaj...", command=self._wczytaj_wzorzec, **B).pack(side="left", expand=True, fill="x", padx=(0, 4))
        self.btn_rysuj = ctk.CTkButton(r, text="Rysuj", command=lambda: self._ustaw_tryb("rysuj"), **B)
        self.btn_rysuj.pack(side="left", expand=True, fill="x")
        r = ctk.CTkFrame(f, fg_color="transparent"); r.pack(fill="x", padx=12, pady=(6, 0))
        ctk.CTkButton(r, text="Zapisz...", command=self._zapisz_wzorzec, **B).pack(side="left", expand=True, fill="x", padx=(0, 4))
        ctk.CTkButton(r, text="Usun", command=self._usun_wzorzec, fg_color="#7a2a2a", hover_color="#9a3a3a",
                      **B).pack(side="left", expand=True, fill="x")
        self.lbl_wzorzec = ctk.CTkLabel(f, text="Brak - narysuj obrys znamienia albo wczytaj maske PNG.",
                                        text_color="gray", font=ctk.CTkFont(size=11), wraplength=330, justify="left")
        self.lbl_wzorzec.pack(anchor="w", padx=12, pady=(4, 10))

        f = sekcja("Widok")
        self.krycie = ctk.DoubleVar(value=35)
        r = ctk.CTkFrame(f, fg_color="transparent"); r.pack(fill="x", padx=12)
        ctk.CTkLabel(r, text="Krycie masek", font=ctk.CTkFont(size=11)).pack(side="left")
        ctk.CTkSlider(r, from_=0, to=100, variable=self.krycie, command=lambda v: self._rysuj(),
                      width=180).pack(side="right")
        self.pokaz_kontury = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(f, text="Kontury", variable=self.pokaz_kontury, command=self._rysuj,
                        font=ctk.CTkFont(size=11)).pack(anchor="w", padx=12, pady=(6, 10))

    # ── wczytywanie ──────────────────────────────────────────────────────────

    def _wczytaj_obraz(self):
        p = filedialog.askopenfilename(title="Wybierz zdjecie",
                                       filetypes=[("Obrazy", "*.jpg *.jpeg *.png *.bmp *.tif"), ("Wszystkie", "*.*")])
        if p:
            self.otworz(p)

    def otworz(self, p):
        img = wczytaj_obraz(p)
        if img is None:
            messagebox.showerror("Blad", f"Nie mozna wczytac:\n{p}")
            return
        self.obraz, self.sciezka = img, Path(p)
        self.roi, self.wzorzec, self.wyniki, self._kontury = None, None, {}, {}
        self.znacznik = None
        self.lbl_obraz.configure(text=f"{self.sciezka.name}\n{img.shape[1]} x {img.shape[0]} px")
        auto = self.sciezka.with_name(self.sciezka.stem + "_wzorzec.png")
        if auto.exists():
            self._ustaw_wzorzec(wczytaj_obraz(auto, cv2.IMREAD_GRAYSCALE), f"wczytano automatycznie: {auto.name}")
        else:
            self._ustaw_wzorzec(None)
        self._info_roi()
        self._tabela()
        self._dopasuj()
        if self.auto_znacznik.get():
            self._szukaj_znacznika()

    def _wczytaj_wzorzec(self):
        if self.obraz is None:
            return
        p = filedialog.askopenfilename(title="Maska wzorcowa (PNG, bialy = znamie)",
                                       filetypes=[("Obrazy", "*.png *.bmp *.jpg"), ("Wszystkie", "*.*")])
        if p:
            self._ustaw_wzorzec(wczytaj_obraz(p, cv2.IMREAD_GRAYSCALE), Path(p).name)

    def _ustaw_wzorzec(self, m, opis=""):
        self._kontury.pop("_wzorzec", None)
        if m is None:
            self.wzorzec = None
            self.lbl_wzorzec.configure(text="Brak - narysuj obrys znamienia albo wczytaj maske PNG.")
        else:
            H, W = self.obraz.shape[:2]
            if m.shape[:2] != (H, W):
                if abs(m.shape[1] / m.shape[0] - W / H) > 0.01:
                    messagebox.showerror("Blad", "Maska ma inne proporcje niz zdjecie.")
                    return
                m = cv2.resize(m, (W, H), interpolation=cv2.INTER_NEAREST)
            self.wzorzec = (m > 127).astype(np.uint8) * 255
            pole = np.count_nonzero(self.wzorzec)
            self.lbl_wzorzec.configure(text=f"{opis + chr(10) if opis else ''}pole: {pole} px")
        self._tabela()
        self._rysuj()

    # ── obszar ───────────────────────────────────────────────────────────────

    def _caly_obraz(self):
        if self.obraz is not None:
            self.roi, self.znacznik = None, None
            self._info_roi()
            self._rysuj()

    def _info_roi(self):
        if self.roi is None:
            self.lbl_roi.configure(text="Caly obraz. Zaznacz luzny prostokat wokol wybranego znamienia - "
                                        "inaczej model wybierze najwieksza plamke/zmiane na zdjeciu. "
                                        "Dokladny kadr ustawi automatyczne przyblizenie.")
        elif self.znacznik is not None:
            x, y, w, h = self.roi
            self.lbl_roi.configure(text=f"Wnetrze znacznika \u03a0 (zgodnosc ksztaltu {self.znacznik.zgodnosc:.2f}): "
                                        f"x={x}, y={y}, {w} x {h} px. Maska znamienia ograniczona do wnetrza "
                                        f"(bialy kontur), folia zastapiona kolorem skory na wejsciu modelu.")
        else:
            x, y, w, h = self.roi
            self.lbl_roi.configure(text=f"x={x}, y={y}, {w} x {h} px")

    def _ustaw_tryb(self, tryb):
        if self.obraz is None:
            return
        self.tryb = None if self.tryb == tryb else tryb
        self._punkty = []
        aktywny, zwykly = ("#c47a10", "#e8a020"), ctk.ThemeManager.theme["CTkButton"]["fg_color"]
        self.btn_roi.configure(fg_color=aktywny if self.tryb == "roi" else zwykly)
        self.btn_rysuj.configure(fg_color=aktywny if self.tryb == "rysuj" else zwykly)
        podp = {"roi": "Przeciagnij prostokat wokol znamienia.",
                "rysuj": "Klikaj punkty obrysu; PPM lub Enter zamyka, Backspace cofa, Esc anuluje."}
        self.lbl_status.configure(text=podp.get(self.tryb, ""), text_color="#e8a020")
        self._rysuj()

    # ── znacznik (w watku) ───────────────────────────────────────────────────

    def _szukaj_znacznika(self):
        if self.obraz is None or self._zajety:
            return
        if wykryj_znacznik is None:
            messagebox.showerror("Blad", f"Detekcja znacznika niedostepna:\n{_BLAD_ZNACZNIKA}")
            return
        self._zajety = True
        self.btn_seg.configure(state="disabled")
        self.lbl_status.configure(text="Szukam znacznika \u03a0...", text_color="#e8a020")
        obraz, sciezka = self.obraz, self.sciezka

        def watek():
            try:
                self._q.put(("znacznik", sciezka, wykryj_znacznik(obraz)))
            except BrakZnacznika as e:
                self._q.put(("brak_znacznika", sciezka, str(e)))
            except Exception as e:
                self._q.put(("brak_znacznika", sciezka, f"blad detekcji: {e}"))
            self._q.put(("koniec_znacznika",))

        threading.Thread(target=watek, daemon=True).start()

    def _ustaw_znacznik(self, z):
        self.znacznik, self.roi, self._kz = z, z.roi, None
        self._info_roi()
        self.lbl_status.configure(text=f"Znaleziono znacznik \u03a0 ({z.czas_s:.1f} s). Obszar analizy = wnetrze "
                                       f"znacznika.", text_color="#2cc97a")
        self._rysuj()

    def _kontury_znacznika(self):
        """Kontury folii (szary) i wnetrza (bialy) we wspolrzednych obrazu."""
        if self._kz is None or self._kz[0] is not self.znacznik:
            out = []
            for m, kol in ((self.znacznik.maska, "#9e9e9e"), (self.znacznik.wnetrze, "#ffffff")):
                ks, _ = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                out += [(cv2.approxPolyDP(k, 1.5, True).reshape(-1, 2).astype(np.float64), kol) for k in ks]
            self._kz = (self.znacznik, out)
        return self._kz[1]

    # ── segmentacja (w watku) ────────────────────────────────────────────────

    def _segmentuj(self):
        if self.obraz is None or self._zajety:
            return
        wybrane = [k for k, v in self.wybor.items() if v.get() and self.modele[k].dostepnosc()[0]]
        if not wybrane:
            messagebox.showinfo("Info", "Zaznacz co najmniej jeden dostepny model.")
            return
        if self.roi is None and any(self.modele[k].kadr_docelowy for k in wybrane):
            if messagebox.askyesno(
                    "Brak zaznaczonego obszaru",
                    "Nie zaznaczono obszaru wokol znamienia.\n\n"
                    "Model uczony na zdjeciach dermatoskopowych (jedna zmiana w kadrze) na calym "
                    "zdjeciu z telefonu moze zaznaczyc inna plame, cien albo faldu skory.\n\n"
                    "Zaznaczyc teraz luzny prostokat wokol znamienia?"):
                self._ustaw_tryb("roi")
                return
        self._ostrzezenia = []
        self._zajety = True
        self.btn_seg.configure(state="disabled")
        obszar = self.znacznik.obszar if self.znacznik is not None else None
        threading.Thread(target=self._watek, args=(wybrane, self.obraz, self.roi, self.przyblizaj.get(), obszar),
                         daemon=True).start()

    def _watek(self, klucze, obraz, roi, przyblizaj, obszar=None):
        for k in klucze:
            m = self.modele[k]
            try:
                if not m._wczytany or m.nieaktualny():
                    self._q.put(("status", f"Wczytywanie modelu {m.nazwa}..."))
                    t0 = time.time()
                    m.wczytaj()
                    dop = ", ".join(x for x in (getattr(m, "wersja_wag", ""), getattr(m, "urzadzenie", "")) if x)
                    self._q.put(("status", f"{m.nazwa}: wczytano w {time.time() - t0:.1f} s"
                                           + (f" ({dop})" if dop else "")))
                self._q.put(("status", f"Segmentacja: {m.nazwa}..."))
                self._q.put(("wynik", k, m.segmentuj(obraz, roi, przyblizaj=przyblizaj, obszar=obszar)))
            except Exception as e:
                self._q.put(("blad", k, str(e)))
        self._q.put(("koniec",))

    def _odpytuj(self):
        try:
            while True:
                msg = self._q.get_nowait()
                if msg[0] == "status":
                    self.lbl_status.configure(text=msg[1], text_color="#e8a020")
                elif msg[0] == "wynik":
                    self.wyniki[msg[1]] = msg[2]
                    self._kontury.pop(msg[1], None)
                    self._tabela()
                    self._rysuj()
                    self._ostrzez_duza_maske(msg[1], msg[2])
                elif msg[0] == "znacznik":
                    if msg[1] == self.sciezka:
                        self._ustaw_znacznik(msg[2])
                elif msg[0] == "brak_znacznika":
                    if msg[1] == self.sciezka:
                        self.lbl_status.configure(text=f"Nie znaleziono znacznika: {msg[2]}\n"
                                                       f"Zaznacz obszar recznie.", text_color="#ff6b4a")
                elif msg[0] == "koniec_znacznika":
                    self._zajety = False
                    self.btn_seg.configure(state="normal")
                elif msg[0] == "blad":
                    messagebox.showerror("Blad modelu", f"{self.modele[msg[1]].nazwa}:\n{msg[2]}")
                elif msg[0] == "koniec":
                    self._zajety = False
                    self.btn_seg.configure(state="normal")
                    if self._ostrzezenia:
                        self.lbl_status.configure(text="\n".join(self._ostrzezenia), text_color="#ff6b4a")
                    else:
                        self.lbl_status.configure(text="Gotowe.", text_color="#2cc97a")
        except queue.Empty:
            pass
        self.after(80, self._odpytuj)

    def _ostrzez_duza_maske(self, klucz, wynik):
        """Znamie zajmuje zwykle ulamek zdjecia - duza maska to najczesciej inna plama lub cien."""
        _, _, w, h = wynik.info.get("kadry", [wynik.roi])[0]
        udzial = np.count_nonzero(wynik.maska) / max(1, w * h)
        if self.znacznik is not None:
            u = np.count_nonzero(wynik.maska) / max(1, np.count_nonzero(self.znacznik.obszar))
            if u > 0.2:
                self._ostrzezenia.append(f"UWAGA: {self.modele[klucz].nazwa} zaznaczyl {100 * u:.0f}% wnetrza "
                                         f"znacznika - to raczej nie znamie (cien, wlosy, odblask?).")
        if self.roi is None and udzial > 0.02:
            self._ostrzezenia.append(f"UWAGA: {self.modele[klucz].nazwa} zaznaczyl {100 * udzial:.0f}% calego "
                                     f"zdjecia - to raczej nie znamie. Zaznacz obszar wokol znamienia.")

    # ── tabela i zapis ───────────────────────────────────────────────────────

    def _wiersze(self):
        out = []
        for k, w in self.wyniki.items():
            m = metryki(w.maska, self.wzorzec) if self.wzorzec is not None else None
            out.append((k, self.modele[k].nazwa, w, int(np.count_nonzero(w.maska)), m))
        return out

    def _tabela(self):
        t = f"{'Model':<16}{'czas':>6}{'Dice':>6}{'IoU':>6}{'Prec':>5}{'Czul':>5}\n"
        for _, nazwa, w, pole, m in self._wiersze():
            t += f"{nazwa[:15]:<16}{w.czas_s:>5.2f}s"
            t += (f"{m['dice']:>6.3f}{m['iou']:>6.3f}{m['precyzja']:>5.2f}{m['czulosc']:>5.2f}\n" if m
                  else f"{'-':>6}{'-':>6}{'-':>5}{'-':>5}\n")
        if self.wzorzec is None and self.wyniki:
            t += "\n(metryki po dodaniu maski wzorcowej)"
        self.tabela.configure(state="normal")
        self.tabela.delete("1.0", "end")
        self.tabela.insert("1.0", t)
        self.tabela.configure(state="disabled")

    def _zapisz_wyniki(self):
        if not self.wyniki:
            messagebox.showinfo("Info", "Brak wynikow do zapisania.")
            return
        znacznik = datetime.now().strftime("%Y%m%d_%H%M%S")
        kat = WYNIKI / f"{self.sciezka.stem}_{znacznik}"
        kat.mkdir(parents=True, exist_ok=True)
        for k, w in self.wyniki.items():
            zapisz_obraz(kat / f"maska_{k}.png", w.maska)
        if self.wzorzec is not None:
            zapisz_obraz(kat / "wzorzec.png", self.wzorzec)
        if self.znacznik is not None:
            zapisz_obraz(kat / "znacznik.png", self.znacznik.maska)
            zapisz_obraz(kat / "znacznik_wnetrze.png", self.znacznik.wnetrze)
        zapisz_obraz(kat / "podglad.png", self._podglad_pelny())
        plik = WYNIKI / "wyniki.csv"
        nowy = not plik.exists()
        with open(plik, "a", newline="", encoding="utf-8") as f:
            wr = csv.writer(f, delimiter=";")
            if nowy:
                wr.writerow(["data", "zdjecie", "roi_x", "roi_y", "roi_w", "roi_h", "model", "czas_s",
                             "pole_px", "dice", "iou", "precyzja", "czulosc", "folder"])
            roi = self.roi or (0, 0, self.obraz.shape[1], self.obraz.shape[0])   # obszar zaznaczony przez uzytkownika
            for k, _, w, pole, m in self._wiersze():
                wr.writerow([znacznik, str(self.sciezka), *roi, k, f"{w.czas_s:.3f}", pole,
                             *([f"{m[x]:.4f}" for x in ("dice", "iou", "precyzja", "czulosc")] if m else [""] * 4),
                             kat.name])
        self.lbl_status.configure(text=f"Zapisano: {kat}", text_color="#2cc97a")

    def _podglad_pelny(self):
        """Wycinek wokol obszaru w pelnej rozdzielczosci z konturami wszystkich masek."""
        H, W = self.obraz.shape[:2]
        x, y, w, h = self.roi or (0, 0, W, H)
        p = max(w, h) // 5
        x0, y0, x1, y1 = max(0, x - p), max(0, y - p), min(W, x + w + p), min(H, y + h + p)
        img = self.obraz[y0:y1, x0:x1].copy()
        gr = max(2, max(x1 - x0, y1 - y0) // 400)
        maski = [(self.znacznik.wnetrze, (255, 255, 255))] if self.znacznik is not None else []
        maski += [(self.wzorzec, KOLOR_WZORCA)] if self.wzorzec is not None else []
        maski += [(r.maska, self.kolor[k]) for k, r in self.wyniki.items()]
        for m, kol in maski:
            ks, _ = cv2.findContours(m[y0:y1, x0:x1], cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
            cv2.drawContours(img, ks, -1, kol, gr, cv2.LINE_AA)
        return img

    def _zapisz_wzorzec(self):
        if self.wzorzec is None:
            return
        p = filedialog.asksaveasfilename(title="Zapisz maske wzorcowa", defaultextension=".png",
                                         initialdir=str(self.sciezka.parent),
                                         initialfile=self.sciezka.stem + "_wzorzec.png",
                                         filetypes=[("PNG", "*.png")])
        if p and zapisz_obraz(p, self.wzorzec):
            self.lbl_status.configure(text=f"Zapisano wzorzec: {Path(p).name} (wczyta sie automatycznie "
                                           f"przy kolejnym otwarciu zdjecia)", text_color="#2cc97a")

    def _usun_wzorzec(self):
        if self.obraz is not None:
            self._ustaw_wzorzec(None)

    # ── mysz i widok ─────────────────────────────────────────────────────────

    def _do_obrazu(self, ex, ey):
        return self.ox + ex / self.skala, self.oy + ey / self.skala

    def _na_ekran(self, x, y):
        return (x - self.ox) * self.skala, (y - self.oy) * self.skala

    def _dopasuj(self):
        if self.obraz is not None:
            self._pokaz_obszar(0, 0, self.obraz.shape[1], self.obraz.shape[0])

    def _przybliz_roi(self):
        if self.obraz is not None and self.roi is not None:
            x, y, w, h = self.roi
            self._pokaz_obszar(x - w * 0.15, y - h * 0.15, w * 1.3, h * 1.3)

    def _pokaz_obszar(self, x, y, w, h):
        cw, ch = max(10, self.plotno.winfo_width()), max(10, self.plotno.winfo_height())
        self.skala = min(cw / w, ch / h)
        self.ox = x + w / 2 - cw / 2 / self.skala
        self.oy = y + h / 2 - ch / 2 / self.skala
        self._rysuj()

    def _kolko(self, e):
        if self.obraz is None:
            return
        x, y = self._do_obrazu(e.x, e.y)
        self.skala = float(np.clip(self.skala * (1.25 if e.delta > 0 else 0.8), 0.02, 40))
        self.ox, self.oy = x - e.x / self.skala, y - e.y / self.skala
        self._rysuj()

    def _pan_start(self, e):
        self._start = (e.x, e.y, self.ox, self.oy)

    def _pan_ruch(self, e):
        if self._start:
            sx, sy, ox, oy = self._start
            self.ox, self.oy = ox - (e.x - sx) / self.skala, oy - (e.y - sy) / self.skala
            self._rysuj()

    def _lpm_wcisniety(self, e):
        if self.obraz is None:
            return
        if self.tryb == "roi":
            self._start = (e.x, e.y)
        elif self.tryb == "rysuj":
            self._punkty.append(self._do_obrazu(e.x, e.y))
            self._rysuj_nakladki()
        else:
            self._pan_start(e)

    def _lpm_ruch(self, e):
        if self.tryb == "roi" and self._start:
            self.plotno.delete("ramka")
            self.plotno.create_rectangle(*self._start, e.x, e.y, outline="#ffd400", width=2, dash=(6, 4), tags="ramka")
        elif self.tryb is None:
            self._pan_ruch(e)

    def _lpm_puszczony(self, e):
        if self.tryb == "roi" and self._start:
            (x0, y0), (x1, y1) = self._do_obrazu(*self._start), self._do_obrazu(e.x, e.y)
            H, W = self.obraz.shape[:2]
            x0, x1 = sorted((int(np.clip(x0, 0, W)), int(np.clip(x1, 0, W))))
            y0, y1 = sorted((int(np.clip(y0, 0, H)), int(np.clip(y1, 0, H))))
            if x1 - x0 >= 8 and y1 - y0 >= 8:
                self.roi, self.znacznik = (x0, y0, x1 - x0, y1 - y0), None
                self._info_roi()
            self._ustaw_tryb("roi")       # wyjscie z trybu
        self._start = None

    def _ruch(self, e):
        if self.tryb == "rysuj" and self._punkty:
            self.plotno.delete("gumka")
            self.plotno.create_line(*self._na_ekran(*self._punkty[-1]), e.x, e.y, fill=hex_bgr(KOLOR_WZORCA),
                                    dash=(4, 3), tags="gumka")

    def _zamknij_obrys(self):
        if self.tryb != "rysuj" or len(self._punkty) < 3:
            return
        H, W = self.obraz.shape[:2]
        m = self.wzorzec.copy() if self.wzorzec is not None else np.zeros((H, W), np.uint8)
        cv2.fillPoly(m, [np.round(self._punkty).astype(np.int32)], 255)
        self._punkty = []
        self._ustaw_tryb("rysuj")         # wyjscie z trybu
        self._ustaw_wzorzec(m, "narysowany recznie (zapisz, aby uzyc ponownie)")

    def _cofnij_punkt(self):
        if self.tryb == "rysuj" and self._punkty:
            self._punkty.pop()
            self._rysuj_nakladki()

    def _anuluj(self):
        if self.tryb:
            self._ustaw_tryb(self.tryb)

    # ── rysowanie ────────────────────────────────────────────────────────────

    def _kontury_maski(self, klucz, maska):
        if klucz not in self._kontury:
            ks, _ = cv2.findContours(maska, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            self._kontury[klucz] = [k.reshape(-1, 2).astype(np.float64) for k in ks]
        return self._kontury[klucz]

    def _rysuj(self):
        self.plotno.delete("all")
        if self.obraz is None:
            self.plotno.create_text(self.plotno.winfo_width() // 2, self.plotno.winfo_height() // 2,
                                    text="Wczytaj zdjecie (panel po prawej)", fill="gray", font=("Segoe UI", 14))
            return
        cw, ch = self.plotno.winfo_width(), self.plotno.winfo_height()
        H, W = self.obraz.shape[:2]
        # widoczny fragment obrazu
        x0, y0 = max(0, int(self.ox)), max(0, int(self.oy))
        x1 = min(W, int(np.ceil(self.ox + cw / self.skala)) + 1)
        y1 = min(H, int(np.ceil(self.oy + ch / self.skala)) + 1)
        if x1 <= x0 or y1 <= y0:
            return
        # najpierw skalowanie do rozmiaru ekranu, potem maski (szybko takze dla 12 Mpx)
        dw, dh = max(1, int(round((x1 - x0) * self.skala))), max(1, int(round((y1 - y0) * self.skala)))
        inter = cv2.INTER_AREA if self.skala < 1 else cv2.INTER_NEAREST
        disp = cv2.resize(self.obraz[y0:y1, x0:x1], (dw, dh), interpolation=inter)
        a = self.krycie.get() / 100
        maski = [(r.maska, self.kolor[k]) for k, r in self.wyniki.items()]
        if self.wzorzec is not None:
            maski.append((self.wzorzec, KOLOR_WZORCA))
        if maski and a > 0:
            disp = disp.astype(np.float32)
            for m, kol in maski:
                mm = cv2.resize(m[y0:y1, x0:x1], (dw, dh), interpolation=cv2.INTER_NEAREST) > 0
                disp[mm] = disp[mm] * (1 - a) + np.array(kol, np.float32) * a
            disp = disp.astype(np.uint8)
        if self.pokaz_kontury.get():
            klucze = list(self.wyniki) + (["_wzorzec"] if self.wzorzec is not None else [])
            for k in klucze:
                m = self.wzorzec if k == "_wzorzec" else self.wyniki[k].maska
                kol = KOLOR_WZORCA if k == "_wzorzec" else self.kolor[k]
                for kontur in self._kontury_maski(k, m):
                    pts = np.round((kontur - [x0, y0]) * self.skala).astype(np.int32)
                    cv2.polylines(disp, [pts], True, kol, 2, cv2.LINE_AA)
        self._foto = ImageTk.PhotoImage(Image.fromarray(cv2.cvtColor(disp, cv2.COLOR_BGR2RGB)))
        ex, ey = self._na_ekran(x0, y0)
        self.plotno.create_image(int(round(ex)), int(round(ey)), image=self._foto, anchor="nw")
        self._rysuj_nakladki()

    def _rysuj_nakladki(self):
        self.plotno.delete("nakladka", "gumka")
        if self.znacznik is not None:
            for kontur, kol in self._kontury_znacznika():
                pts = [c for p in kontur for c in self._na_ekran(*p)]
                if len(pts) >= 6:
                    self.plotno.create_line(*pts, pts[0], pts[1], fill=kol, width=1, tags="nakladka")
        if self.roi is not None:
            x, y, w, h = self.roi
            self.plotno.create_rectangle(*self._na_ekran(x, y), *self._na_ekran(x + w, y + h),
                                         outline="#ffd400", width=2, dash=(6, 4), tags="nakladka")
        for k, wyn in self.wyniki.items():          # ostateczny kadr po automatycznym przyblizeniu
            kadry = wyn.info.get("kadry", [])
            if len(kadry) > 1:
                x, y, w, h = kadry[-1]
                self.plotno.create_rectangle(*self._na_ekran(x, y), *self._na_ekran(x + w, y + h),
                                             outline=hex_bgr(self.kolor[k]), width=1, dash=(3, 3), tags="nakladka")
        if self._punkty:
            pts = [c for p in self._punkty for c in self._na_ekran(*p)]
            if len(self._punkty) > 1:
                self.plotno.create_line(*pts, fill=hex_bgr(KOLOR_WZORCA), width=2, tags="nakladka")
            for i in range(0, len(pts), 2):
                self.plotno.create_oval(pts[i] - 3, pts[i + 1] - 3, pts[i] + 3, pts[i + 1] + 3,
                                        fill=hex_bgr(KOLOR_WZORCA), outline="", tags="nakladka")


def _uruchom_w_srodowisku_modeli():
    """Gdy tester odpalono Pythonem bez PyTorch (np. "Run" w VS Code z interpreterem
    aplikacji), uruchamia go ponownie w srodowisku modeli i konczy biezacy proces."""
    import importlib.util
    import subprocess
    from modele_segmentacja.konfiguracja import KATALOG_MODULU, PYTHON_MODELI
    if importlib.util.find_spec("torch") is not None or not PYTHON_MODELI.exists():
        return
    if Path(sys.executable).resolve() == PYTHON_MODELI.resolve():
        return
    print(f"Brak PyTorch w {sys.executable}\n-> uruchamiam tester w srodowisku modeli: {PYTHON_MODELI}")
    subprocess.Popen([str(PYTHON_MODELI), "-m", "modele_segmentacja.tester", *sys.argv[1:]],
                     cwd=str(KATALOG_MODULU.parent))
    sys.exit(0)


def main():
    _uruchom_w_srodowisku_modeli()
    app = Tester()
    if len(sys.argv) > 1:
        app.after(200, lambda: app.otworz(sys.argv[1]))
    app.mainloop()


if __name__ == "__main__":
    main()
