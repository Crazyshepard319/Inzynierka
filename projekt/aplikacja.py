"""
Aplikacja desktopowa — rejestracja multimodalna RGB <-> Termal
Wymaga: pip install customtkinter Pillow
"""

import os
import queue
import sys
import threading
from pathlib import Path
from tkinter import filedialog, messagebox

import cv2
import customtkinter as ctk
from PIL import Image

import dopasowanie3 as dopasowanie   # poprzednia wersja: dopasowanie2 (archiwum/)

INZ = Path(__file__).resolve().parent.parent          # folder Inzynierka
KATALOG_RGB = INZ / "dane" / "dane_RGB"
KATALOG_TERMAL = INZ / "dane" / "dane_termowizja"
KATALOG_WYNIKOW = INZ / "wyniki" / "wyniki_dopasowania"


# ── Motyw ─────────────────────────────────────────────────────────────────────
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

THUMB = (220, 220)
PREVIEW = (400, 260)

KOLOR_TLO_PANEL  = ("#e8e8e8", "#2b2b2b")
KOLOR_TLO_OBRAZ  = ("#d0d0d0", "#1e1e1e")
KOLOR_LOG_TLO    = "#161616"
KOLOR_LOG_TEKST  = "#c8c8c8"


# ── Pomocnicze ────────────────────────────────────────────────────────────────

class QueueWriter:
    def __init__(self, q):
        self._q = q

    def write(self, t):
        if t:
            self._q.put(t)

    def flush(self):
        pass


def bgr_do_ctk(img_bgr, rozmiar: tuple) -> ctk.CTkImage | None:
    """Konwertuje obraz OpenCV do CTkImage o podanym rozmiarze."""
    if img_bgr is None:
        return None
    h, w = img_bgr.shape[:2]
    sc = min(rozmiar[0] / w, rozmiar[1] / h, 1.0)
    nw, nh = max(1, int(w * sc)), max(1, int(h * sc))
    img_s = cv2.resize(img_bgr, (nw, nh), interpolation=cv2.INTER_AREA)
    pil = Image.fromarray(cv2.cvtColor(img_s, cv2.COLOR_BGR2RGB))
    return ctk.CTkImage(light_image=pil, dark_image=pil, size=(nw, nh))


# ── Glowna klasa ─────────────────────────────────────────────────────────────

class Aplikacja(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Rejestracja multimodalna  RGB ↔ Termal")
        self.geometry("1100x960")
        self.minsize(800, 640)

        self._rgb_path = ctk.StringVar()
        self._ter_path = ctk.StringVar()
        self._out_path = ctk.StringVar(
            value=str(KATALOG_WYNIKOW / "wynik_rejestracji.png"))

        self._log_q   = queue.Queue()
        self._running = False
        self._images  = {}   # zapobiega GC obrazow

        self._przezr   = ctk.DoubleVar(value=50)   # przezroczystosc termalu [%]
        self._podglad  = None   # (rgb, termal BGRA) pomniejszone - do szybkiego mieszania
        self._biezacy  = None   # (rgb, out) rejestracji w toku
        self._ostatni  = None   # (rgb, out) ostatniej udanej rejestracji

        self._build()
        self._poll()

    # ── Budowanie UI ──────────────────────────────────────────────────────────

    def _build(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(4, weight=1)   # log rozciagalny

        # ── 1. Pasek tytulowy ─────────────────────────────────────────────────
        pasek = ctk.CTkFrame(self, height=64, corner_radius=0,
                              fg_color=("gray80", "gray15"))
        pasek.grid(row=0, column=0, sticky="ew")
        pasek.grid_propagate(False)
        pasek.columnconfigure(0, weight=1)

        ctk.CTkLabel(pasek,
                     text="Rejestracja multimodalna  RGB ↔ Termal",
                     font=ctk.CTkFont(size=20, weight="bold")).grid(
            row=0, column=0, pady=16)

        # ── 2. Sekcja obrazow wejsciowych ─────────────────────────────────────
        sekcja_in = ctk.CTkFrame(self, fg_color=KOLOR_TLO_PANEL, corner_radius=12)
        sekcja_in.grid(row=1, column=0, padx=16, pady=(12, 6), sticky="ew")
        sekcja_in.columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(sekcja_in, text="Obrazy wejsciowe",
                     font=ctk.CTkFont(size=13, weight="bold")).grid(
            row=0, column=0, columnspan=2, padx=16, pady=(12, 4), sticky="w")

        self._panel_obrazu(sekcja_in, "Obraz RGB",
                           self._rgb_path, self._pick_rgb, "rgb", col=0)
        self._panel_obrazu(sekcja_in, "Obraz termalny",
                           self._ter_path, self._pick_ter, "ter", col=1)

        # ── 3. Plik wyjsciowy ─────────────────────────────────────────────────
        sekcja_out = ctk.CTkFrame(self, fg_color=KOLOR_TLO_PANEL, corner_radius=12)
        sekcja_out.grid(row=2, column=0, padx=16, pady=6, sticky="ew")
        sekcja_out.columnconfigure(1, weight=1)

        ctk.CTkLabel(sekcja_out, text="Plik wyjsciowy:",
                     font=ctk.CTkFont(size=12)).grid(
            row=0, column=0, padx=(16, 8), pady=14)
        ctk.CTkEntry(sekcja_out, textvariable=self._out_path,
                     font=ctk.CTkFont(size=11), height=36).grid(
            row=0, column=1, sticky="ew", pady=14)
        ctk.CTkButton(sekcja_out, text="Zmien...", width=100, height=36,
                      command=self._pick_out).grid(
            row=0, column=2, padx=(8, 16), pady=14)

        # ── 4. Przycisk + status + pasek postepu ──────────────────────────────
        sekcja_btn = ctk.CTkFrame(self, fg_color="transparent")
        sekcja_btn.grid(row=3, column=0, pady=8)

        self._btn = ctk.CTkButton(
            sekcja_btn,
            text="  Uruchom rejestracje",
            font=ctk.CTkFont(size=15, weight="bold"),
            height=48, width=260,
            corner_radius=24,
            command=self._run)
        self._btn.pack(side="left", padx=12)

        self._lbl_status = ctk.CTkLabel(
            sekcja_btn, text="Gotowy",
            text_color="gray",
            font=ctk.CTkFont(size=11))
        self._lbl_status.pack(side="left", padx=4)

        self._bar = ctk.CTkProgressBar(self, height=8, corner_radius=4,
                                        mode="indeterminate")
        self._bar.grid(row=3, column=0, padx=16, pady=(0, 4),
                       sticky="sew")
        self._bar.set(0)

        # ── 5. Log i wynik obok siebie (pod soba nie mieszcza sie w oknie) ────
        dolna = ctk.CTkFrame(self, fg_color="transparent")
        dolna.grid(row=4, column=0, padx=16, pady=(6, 14), sticky="nsew")
        dolna.columnconfigure(0, weight=1)
        dolna.rowconfigure(0, weight=1)

        sekcja_log = ctk.CTkFrame(dolna, fg_color=KOLOR_TLO_PANEL, corner_radius=12)
        sekcja_log.grid(row=0, column=0, padx=(0, 6), sticky="nsew")
        sekcja_log.columnconfigure(0, weight=1)
        sekcja_log.rowconfigure(1, weight=1)

        ctk.CTkLabel(sekcja_log, text="Log",
                     font=ctk.CTkFont(size=13, weight="bold")).grid(
            row=0, column=0, padx=16, pady=(10, 4), sticky="w")

        self._log = ctk.CTkTextbox(
            sekcja_log,
            font=ctk.CTkFont(family="Courier New", size=10),
            fg_color=KOLOR_LOG_TLO,
            text_color=KOLOR_LOG_TEKST,
            corner_radius=8,
            state="disabled")
        self._log.grid(row=1, column=0, padx=12, pady=(0, 12), sticky="nsew")

        # ── 6. Sekcja wyniku ──────────────────────────────────────────────────
        sekcja_wynik = ctk.CTkFrame(dolna, fg_color=KOLOR_TLO_PANEL, corner_radius=12)
        sekcja_wynik.grid(row=0, column=1, padx=(6, 0), sticky="nsew")
        sekcja_wynik.columnconfigure(0, weight=1)

        ctk.CTkLabel(sekcja_wynik, text="Wynik",
                     font=ctk.CTkFont(size=13, weight="bold")).grid(
            row=0, column=0, columnspan=2, padx=16, pady=(12, 4), sticky="w")

        self._lbl_wynik = ctk.CTkLabel(
            sekcja_wynik,
            text="(brak — uruchom rejestracje)",
            text_color="gray",
            font=ctk.CTkFont(size=11))
        self._lbl_wynik.grid(row=1, column=0, padx=16, pady=(0, 14), sticky="w")

        sterowanie = ctk.CTkFrame(sekcja_wynik, fg_color="transparent")
        sterowanie.grid(row=1, column=1, padx=16, pady=(0, 14), sticky="n")

        ctk.CTkLabel(sterowanie, text="Przezroczystosc termalu",
                     font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w")
        self._suwak = ctk.CTkSlider(sterowanie, from_=0, to=100, number_of_steps=100,
                                    width=200, variable=self._przezr,
                                    command=self._zmien_przezroczystosc,
                                    state="disabled")
        self._suwak.pack(pady=(8, 2))
        self._lbl_przezr = ctk.CTkLabel(sterowanie, text="50 %",
                                        font=ctk.CTkFont(size=12))
        self._lbl_przezr.pack()
        ctk.CTkLabel(sterowanie, text="0 % = sam termal,  100 % = samo RGB",
                     text_color="gray", font=ctk.CTkFont(size=10)).pack()

        self._btn_zapisz = ctk.CTkButton(sterowanie, text="Zapisz nalozenie...",
                                         width=200, height=36, state="disabled",
                                         command=self._zapisz_nalozenie)
        self._btn_zapisz.pack(pady=(12, 6))
        ctk.CTkButton(sterowanie, text="Otworz w eksploratorze",
                      width=200, height=36,
                      command=self._open_result).pack()

    def _panel_obrazu(self, parent, tytul, zmienna, komenda, klucz, col):
        """Panel z miniatura, przyciskiem i sciezka pliku."""
        fr = ctk.CTkFrame(parent, fg_color="transparent")
        fr.grid(row=1, column=col, padx=16, pady=(4, 16), sticky="n")

        ctk.CTkLabel(fr, text=tytul,
                     font=ctk.CTkFont(size=12, weight="bold")).pack(pady=(0, 6))

        # Ramka miniatury
        ramka = ctk.CTkFrame(fr,
                              width=THUMB[0], height=THUMB[1],
                              fg_color=KOLOR_TLO_OBRAZ,
                              corner_radius=10,
                              border_width=1,
                              border_color=("gray70", "gray35"))
        ramka.pack_propagate(False)
        ramka.pack()

        lbl_img = ctk.CTkLabel(ramka, text="Brak obrazu",
                                text_color=("gray50", "gray60"),
                                font=ctk.CTkFont(size=12))
        lbl_img.place(relx=0.5, rely=0.5, anchor="center")
        self._images[klucz + "_lbl"] = lbl_img

        ctk.CTkButton(fr, text="Wybierz plik...",
                      width=180, height=36, corner_radius=8,
                      command=komenda).pack(pady=10)

        ctk.CTkLabel(fr, textvariable=zmienna,
                     font=ctk.CTkFont(size=9),
                     text_color=("gray50", "gray55"),
                     wraplength=240).pack()

    # ── Wybor plikow ──────────────────────────────────────────────────────────

    def _pick_rgb(self):
        p = filedialog.askopenfilename(
            title="Wybierz obraz RGB",
            initialdir=str(KATALOG_RGB),
            filetypes=[("Obrazy", "*.jpg *.jpeg *.png *.bmp"), ("Wszystkie", "*.*")])
        if p:
            self._rgb_path.set(p)
            self._pokaz_miniature(p, "rgb")

    def _pick_ter(self):
        p = filedialog.askopenfilename(
            title="Wybierz obraz termalny",
            initialdir=str(KATALOG_TERMAL),
            filetypes=[("Obrazy", "*.jpg *.jpeg *.png *.bmp"), ("Wszystkie", "*.*")])
        if p:
            self._ter_path.set(p)
            self._pokaz_miniature(p, "ter")

    def _pick_out(self):
        p = filedialog.asksaveasfilename(
            title="Zapisz wynik jako",
            initialdir=str(KATALOG_WYNIKOW),
            defaultextension=".png",
            filetypes=[("PNG", "*.png"), ("Wszystkie", "*.*")])
        if p:
            self._out_path.set(p)

    def _pokaz_miniature(self, sciezka, klucz):
        lbl = self._images.get(klucz + "_lbl")
        if lbl is None:
            return
        img = dopasowanie.imread(sciezka)
        ctk_img = bgr_do_ctk(img, THUMB)
        if ctk_img:
            self._images[klucz] = ctk_img
            lbl.configure(image=ctk_img, text="")
        else:
            lbl.configure(text=Path(sciezka).name)

    # ── Uruchomienie rejestracji ───────────────────────────────────────────────

    def _run(self):
        if self._running:
            return

        rgb = self._rgb_path.get().strip()
        ter = self._ter_path.get().strip()
        out = self._out_path.get().strip()

        if not rgb or not Path(rgb).exists():
            messagebox.showerror("Blad", "Wybierz istniejacy obraz RGB.")
            return
        if not ter or not Path(ter).exists():
            messagebox.showerror("Blad", "Wybierz istniejacy obraz termalny.")
            return
        if not out:
            messagebox.showerror("Blad", "Podaj sciezke do pliku wyjsciowego.")
            return

        self._running = True
        self._biezacy = (rgb, out)
        self._btn.configure(state="disabled")
        self._suwak.configure(state="disabled")
        self._btn_zapisz.configure(state="disabled")
        self._bar.start()
        self._ustaw_status("Rejestracja w toku...", "#e8a020")

        self._log.configure(state="normal")
        self._log.delete("1.0", "end")
        self._log.configure(state="disabled")

        threading.Thread(target=self._worker,
                         args=(rgb, ter, out), daemon=True).start()

    def _worker(self, rgb, ter, out):
        stary_out, stary_err = sys.stdout, sys.stderr
        sys.stdout = sys.stderr = QueueWriter(self._log_q)
        try:
            dopasowanie.run_registration(rgb, ter, out)
            self._log_q.put(("OK", out))
        except Exception as exc:
            self._log_q.put(("ERR", str(exc)))
        finally:
            sys.stdout, sys.stderr = stary_out, stary_err

    # ── Polling logu ──────────────────────────────────────────────────────────

    def _poll(self):
        while True:
            try:
                msg = self._log_q.get_nowait()
            except queue.Empty:
                break

            if isinstance(msg, tuple):
                rodzaj, dane = msg
                self._bar.stop()
                self._bar.set(0)
                self._btn.configure(state="normal")
                self._running = False

                if rodzaj == "OK":
                    self._ustaw_status("Zakonczone pomyslnie  ✔", "#2cc97a")
                    self._ostatni = self._biezacy
                    self._pokaz_wynik(dane)
                else:
                    self._ustaw_status("Blad — sprawdz log", "#e84040")
                    if self._podglad is not None:      # poprzedni wynik nadal jest
                        self._suwak.configure(state="normal")
                        self._btn_zapisz.configure(state="normal")
                    messagebox.showerror("Blad rejestracji", dane)
            else:
                self._log.configure(state="normal")
                self._log.insert("end", msg)
                self._log.see("end")
                self._log.configure(state="disabled")

        self.after(80, self._poll)

    # ── Pomocnicze ────────────────────────────────────────────────────────────

    def _ustaw_status(self, tekst, kolor="gray"):
        self._lbl_status.configure(text=tekst, text_color=kolor)

    def _wczytaj_do_nalozenia(self):
        """Pelne RGB i termal wyrownany (BGRA) ostatniej rejestracji albo (None, None)."""
        if self._ostatni is None:
            return None, None
        rgb_path, out = self._ostatni
        stem = Path(out).with_suffix("")
        rgb = dopasowanie.imread(rgb_path)
        ter = dopasowanie.imread(f"{stem}_termal_wyrownany.png", cv2.IMREAD_UNCHANGED)
        if rgb is None or ter is None or ter.ndim != 3 or ter.shape[:2] != rgb.shape[:2]:
            return None, None
        return rgb, ter

    def _pokaz_wynik(self, sciezka):
        rgb, ter = self._wczytaj_do_nalozenia()
        if rgb is None:
            # brak wyrownanego termalu - pokaz sam plik wynikowy, bez suwaka
            self._podglad = None
            ctk_img = bgr_do_ctk(dopasowanie.imread(sciezka), PREVIEW)
            if ctk_img:
                self._images["wynik"] = ctk_img
                self._lbl_wynik.configure(image=ctk_img, text="")
            else:
                self._lbl_wynik.configure(text=f"Zapisano: {sciezka}")
            return

        h, w = rgb.shape[:2]
        sc = min(PREVIEW[0] / w, PREVIEW[1] / h, 1.0)
        rozm = (max(1, int(w * sc)), max(1, int(h * sc)))
        self._podglad = (cv2.resize(rgb, rozm, interpolation=cv2.INTER_AREA),
                         cv2.resize(ter, rozm, interpolation=cv2.INTER_AREA))
        self._suwak.configure(state="normal")
        self._btn_zapisz.configure(state="normal")
        self._odswiez_podglad()

    def _odswiez_podglad(self):
        if self._podglad is None:
            return
        rgb, ter = self._podglad
        img = dopasowanie.nalozenie(rgb, ter, self._przezr.get() / 100)
        ctk_img = bgr_do_ctk(img, PREVIEW)
        self._images["wynik"] = ctk_img
        self._lbl_wynik.configure(image=ctk_img, text="")

    def _zmien_przezroczystosc(self, wartosc):
        self._lbl_przezr.configure(text=f"{int(round(float(wartosc)))} %")
        self._odswiez_podglad()

    def _zapisz_nalozenie(self):
        if self._ostatni is None:
            return
        stem = Path(self._ostatni[1]).with_suffix("")
        proc = int(round(self._przezr.get()))
        p = filedialog.asksaveasfilename(
            title="Zapisz nalozenie jako",
            initialdir=str(stem.parent),
            initialfile=f"{stem.name}_nalozenie_{proc}.png",
            defaultextension=".png",
            filetypes=[("PNG", "*.png"), ("JPEG", "*.jpg"), ("Wszystkie", "*.*")])
        if not p:
            return
        rgb, ter = self._wczytaj_do_nalozenia()
        if rgb is None:
            messagebox.showerror("Blad", "Nie mozna wczytac obrazow do nalozenia.\n"
                                          "Uruchom rejestracje ponownie.")
            return
        if dopasowanie.imwrite(p, dopasowanie.nalozenie(rgb, ter, proc / 100)):
            self._ustaw_status(f"Zapisano: {Path(p).name}", "#2cc97a")
        else:
            messagebox.showerror("Blad", f"Nie udalo sie zapisac pliku:\n{p}")

    def _open_result(self):
        out = self._out_path.get()
        if Path(out).exists():
            os.startfile(out)
        else:
            messagebox.showinfo("Info",
                                "Plik wyjsciowy jeszcze nie istnieje.\n"
                                "Najpierw uruchom rejestracje.")


# ── Start ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app = Aplikacja()
    app.mainloop()
