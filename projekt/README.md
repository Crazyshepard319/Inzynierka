# Praca inżynierska — dopasowanie i wielomodalna analiza regionów w obrazach dermatologicznych

## Struktura folderu `Inzynierka`

```
Inzynierka/
├── projekt/                      kod (w gicie)
│   ├── aplikacja.py              GUI: rejestracja RGB ↔ termal
│   ├── dopasowanie3.py           metoda rejestracji (ECC na maskach znacznika)
│   ├── read_flirpy.py            nagranie .seq (FLIR) → klatki PNG
│   ├── modele_segmentacja/       segmentacja znamienia: PanDerm, tester, znacznik Π (własny README)
│   └── README.md                 ten plik
├── dane/                         nowe dane (poza gitem)
│   ├── dane_RGB/                 zdjęcia z telefonu:  znamie_01/, znamie_02/, …
│   └── dane_termowizja/          nagrania i klatki:   znamie_01/, znamie_02/, …
├── wyniki/                       (poza gitem)
│   ├── wyniki_dopasowania/       aplikacja.py, dopasowanie3.py
│   ├── wyniki_segmentacji/       tester, trening PanDerm, sprawdz_znaczniki.bat
│   └── wyniki_obu/               maska znamienia przeniesiona na termal (do zrobienia)
├── praca/
│   ├── literatura/               PDF-y (poza gitem)
│   └── rysunki/                  rysunki do tekstu
├── archiwum/                     (poza gitem)
│   ├── dane/
│   │   ├── pary_rgb_termal/      nowe1 … nowe16: pary RGB–termal z wynikami starszych wersji
│   │   ├── nagrania_termowizja/  19 nagrań .seq (luty, maj 2026)
│   │   ├── znamiona/             10 zdjęć z 17.10 (5 ze znacznikiem Π)
│   │   └── termografia_test/     pierwsze testy (marzec 2026)
│   ├── proba1 … proba10/         eksperymenty marzec–czerwiec (SimpleITK, krawędzie, ORB)
│   ├── output_frames*/           klatki z pierwszych nagrań
│   └── dopasowanie2.py, downloaddata.py
└── inzynierka/                   venv aplikacji (Python 3.14, poza gitem)
```

Ciężkie pliki modeli (środowisko z PyTorch, wagi, ISIC 2018) leżą poza OneDrive:
`C:\Users\groch\modele_dane\` — szczegóły w `modele_segmentacja/README.md`.

## Uruchomienie

| Co | Jak | Wynik |
|---|---|---|
| Rejestracja RGB ↔ termal | `inzynierka\Scripts\python.exe projekt\aplikacja.py` | `wyniki/wyniki_dopasowania/` (domyślnie) |
| Segmentacja znamienia | `projekt\modele_segmentacja\uruchom_tester.bat` | `wyniki/wyniki_segmentacji/` |
| Kontrola znacznika na nowych zdjęciach | przeciągnij `dane\dane_RGB` na `projekt\modele_segmentacja\sprawdz_znaczniki.bat` | `wyniki/wyniki_segmentacji/znaczniki/` |
| Klatki z nagrania .seq | ustaw `filepath` w `projekt/read_flirpy.py` i uruchom | obok nagrania z `dane/` (albo `dane/dane_termowizja/<nagranie>/`) |
| Trening PanDerm | `projekt\modele_segmentacja\trenuj_panderm.bat` | wagi w `modele_dane\wagi\`, wykres w `wyniki/wyniki_segmentacji/` |

W aplikacji okna wyboru plików otwierają się w `dane/dane_RGB` i `dane/dane_termowizja`.
`dopasowanie3.py` zapisuje pliki diagnostyczne (`<wynik>_maska_*.png`, `<wynik>_debug_*.png`)
obok pliku wyniku — dane wejściowe nie są modyfikowane.

## Konwencja nowych danych

Jedno znamię = jeden podfolder, o tej samej nazwie w `dane_RGB` i `dane_termowizja`:

```
dane/dane_RGB/znamie_01/IMG_1234.jpg, IMG_1235.jpg, …
dane/dane_termowizja/znamie_01/Rec-000050.seq  →  read_flirpy.py  →  znamie_01/Rec-000050/frame_000.png, …
```

Dzięki temu wiadomo, które zdjęcie pasuje do którego nagrania, a podział train/test w segmentacji
idzie po znamionach (`sprawdz_znaczniki.bat` liczy zdjęcia na znamię).

## Git

W repozytorium jest tylko kod i opisy (`projekt/`, `praca/rysunki/`, `.gitignore`).
`dane/`, `wyniki/`, `archiwum/`, nagrania `.seq`, venvy i literatura są w `.gitignore`.
