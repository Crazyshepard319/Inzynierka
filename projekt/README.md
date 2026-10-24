# Praca inżynierska — dopasowanie i wielomodalna analiza regionów w obrazach dermatologicznych

## Struktura folderu `Inzynierka`

```
Inzynierka/
├── projekt/                      kod (w gicie)
│   ├── aplikacja.py              GUI: rejestracja RGB ↔ termal
│   ├── dopasowanie3.py           metoda rejestracji (ECC na maskach znacznika)
│   ├── read_flirpy.py            nagrania .seq (FLIR) → obrazy (plik albo cały folder)
│   ├── heic_do_jpg.py            zdjęcia HEIC → JPG numerowane wg czasu wykonania
│   ├── modele_segmentacja/       segmentacja znamienia: PanDerm, tester, znacznik Π (własny README)
│   └── README.md                 ten plik
├── dane/                         nowe dane (poza gitem)
│   ├── dane_RGB/                 zdjęcia z telefonu: 1.jpg, 2.jpg, …
│   ├── dane_termowizja/          obrazy termowizyjne: 1.jpg, 2.jpg, …
│   ├── pary/                     pary RGB–termal do dopasowania
│   └── mapowanie_*.csv           numer → oryginalny plik (IMG_xxxx.heic, thermalNNNN.SEQ)
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
│   │   ├── termografia_test/     pierwsze testy (marzec 2026)
│   │   └── oryginaly_heic/       oryginały zdjęć z dane_RGB (HEIC)
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
| Nagrania .seq → JPG | `python projekt\read_flirpy.py <folder z .seq> --numeruj` | `dane/dane_termowizja/N.jpg` + `dane/mapowanie_dane_termowizja.csv` |
| Zdjęcia HEIC → JPG | `python projekt\heic_do_jpg.py` (wymaga `pip install pillow-heif`) | `dane/dane_RGB/N.jpg` + `dane/mapowanie_dane_RGB.csv`; HEIC do `archiwum/dane/oryginaly_heic/` |
| Klatki jednego nagrania | ustaw `FILEPATH` w `projekt/read_flirpy.py` i uruchom bez argumentów | `frame_NNN.png` obok nagrania z `dane/` (albo `dane/dane_termowizja/<nagranie>/`) |
| Trening PanDerm | `projekt\modele_segmentacja\trenuj_panderm.bat` | wagi w `modele_dane\wagi\`, wykres w `wyniki/wyniki_segmentacji/` |

W aplikacji okna wyboru plików otwierają się w `dane/dane_RGB` i `dane/dane_termowizja`.
`dopasowanie3.py` zapisuje pliki diagnostyczne (`<wynik>_maska_*.png`, `<wynik>_debug_*.png`)
obok pliku wyniku — dane wejściowe nie są modyfikowane.

## Nowe dane

Numeracja 1…N: zdjęcia wg czasu wykonania (EXIF), obrazy termowizyjne wg numeru nagrania.
Oba skrypty numerują od pierwszego wolnego numeru, więc kolejne serie dopisują się na końcu,
a pliki `dane/mapowanie_*.csv` trzymają powiązanie z oryginałami.

Seria z 23.10.2026: 96 zdjęć RGB (`IMG_9844`–`IMG_9939`, 12:07–12:58) i 97 nagrań
(`thermal0001`–`thermal0101`, 12:58–13:49). Numery RGB i termowizji nie odpowiadają sobie 1:1
(jedno nagranie więcej) — pary trzeba ustalić przed dopasowaniem (`dane/pary/`).

Kamera termowizyjna z tej serii ma klatkę 320×240 (+6 wierszy telemetrii, które `read_flirpy.py`
obcina); przesunięcie kolumn 66 px dotyczy tylko FLIR A655sc (640×480) ze starszych nagrań.

## Git

W repozytorium jest tylko kod i opisy (`projekt/`, `praca/rysunki/`, `.gitignore`).
`dane/`, `wyniki/`, `archiwum/`, nagrania `.seq`, venvy i literatura są w `.gitignore`.
