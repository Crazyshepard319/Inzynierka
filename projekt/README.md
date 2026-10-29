# Praca inżynierska — dopasowanie i wielomodalna analiza regionów w obrazach dermatologicznych

## Struktura folderu `Inzynierka`

```
Inzynierka/
├── projekt/                      kod (w gicie)
│   ├── aplikacja.py              GUI: cały system krok po kroku (dane → rejestracja → segmentacja → przeniesienie ROI → pomiary → raport)
│   ├── dopasowanie3.py           metoda rejestracji (ECC na maskach znacznika)
│   ├── read_flirpy.py            nagrania .seq (FLIR) → obrazy (plik albo cały folder)
│   ├── heic_do_jpg.py            zdjęcia HEIC → JPG numerowane wg czasu wykonania
│   ├── import_cvat.py            adnotacje z CVAT → maski i narożniki znacznika w dane/pary/N/
│   ├── temperatury_par.py        nagrania SEQ → mapy °C (termal_C.npy) i surowa intensywność (termal_surowe.npy)
│   ├── potok_pary.py             analiza pary: rejestracja → przeniesienie ROI → pomiary → zgodność → raport
│   ├── analiza/                  etapy systemu (system.py, wspólne dla aplikacji i potoku) + dane, geometria, miary, pomiary, obrazy, raport,
│   │                             baza.py (baza SQLite)
│   ├── baza_danych.bat           obsługa bazy SQLite (utworz, importuj_wyniki, pokaz, eksport, eksport_piksele, sql)
│   ├── modele_segmentacja/       segmentacja: znamię – PanDerm (M1), znacznik na termowizji – U-Net (M3, unet_termal/),
│   │                             tester, znacznik Π (własny README)
│   └── README.md                 ten plik
├── dane/                         nowe dane (poza gitem)
│   ├── dane_RGB/                 zdjęcia z telefonu: 1.jpg, 2.jpg, …
│   ├── dane_termowizja/          obrazy termowizyjne: 1.jpg, 2.jpg, …
│   ├── pary/                     pary RGB–termal: rgb.jpg, termal.jpg, termal_C.npy, termal_surowe.npy, maski z CVAT, narozniki.json
│   ├── baza.sqlite               baza danych systemu: znamiona, pary, adnotacje, analizy, miary (analiza/baza.py)
│   ├── znamiona.csv              para → numer znamienia i fold (podział trening/test po znamionach)
│   ├── temperatury.csv           temperatura skóry w każdej parze (kontrola map °C)
│   ├── adnotacje/                eksporty CVAT (rgb.zip, termowizja.zip) + podsumowanie.csv
│   └── mapowanie_*.csv           numer → oryginalny plik (IMG_xxxx.heic, thermalNNNN.SEQ)
├── wyniki/                       (poza gitem)
│   ├── wyniki_dopasowania/       aplikacja.py, dopasowanie3.py
│   ├── wyniki_segmentacji/       tester, trening PanDerm, sprawdz_znaczniki.bat; unet_termal/ (trening i ocena U-Netu)
│   └── wyniki_obu/               raporty par: raport.html, metryki.json, obrazy PNG, piksele_znamienia_termal.csv
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
| Aplikacja (wszystkie etapy) | `inzynierka\Scripts\python.exe projekt\aplikacja.py` | rejestracja w `wyniki/wyniki_dopasowania/<para>/`, raport w `wyniki/wyniki_obu/<para>/` |
| Segmentacja znamienia | `projekt\modele_segmentacja\uruchom_tester.bat` | `wyniki/wyniki_segmentacji/` |
| Kontrola znacznika na nowych zdjęciach | przeciągnij `dane\dane_RGB` na `projekt\modele_segmentacja\sprawdz_znaczniki.bat` | `wyniki/wyniki_segmentacji/znaczniki/` |
| Nagrania .seq → JPG | `python projekt\read_flirpy.py <folder z .seq> --numeruj` | `dane/dane_termowizja/N.jpg` + `dane/mapowanie_dane_termowizja.csv` |
| Zdjęcia HEIC → JPG | `python projekt\heic_do_jpg.py` (wymaga `pip install pillow-heif`) | `dane/dane_RGB/N.jpg` + `dane/mapowanie_dane_RGB.csv`; HEIC do `archiwum/dane/oryginaly_heic/` |
| Import adnotacji z CVAT | eksporty „CVAT for images 1.1” do `dane\adnotacje\`, potem `python projekt\import_cvat.py` | maski i `narozniki.json` w `dane/pary/N/`, `dane/adnotacje/podsumowanie.csv`, podglądy w `wyniki/kontrola_adnotacji/` |
| Mapy temperatur °C i surowa intensywność | `python projekt\temperatury_par.py` (emisyjność skóry 0,98); same surowe wartości: `--tylko_surowe` | `dane/pary/N/termal_C.npy`, `dane/pary/N/termal_surowe.npy`, `dane/temperatury.csv` |
| Analiza par (te same etapy co aplikacja, PanDerm) | `projekt\potok_pary.bat 1` albo `projekt\potok_pary.bat 1 3 10-20` (Python środowiska modeli) | `wyniki/wyniki_obu/para_1/raport.html` + `metryki.json`, rejestracja w `wyniki/wyniki_dopasowania/para_1/` |
| Przeliczenie pomiarów i raportów bez GPU (np. po zmianach w kodzie) | `projekt\potok_pary.bat 1-94 --z_zapisanych` | jak wyżej; rejestracja z `wyniki_dopasowania/para_N/`, znamię z zapisanej maski PanDerm |
| Porównanie metod rejestracji (E4) | `"%USERPROFILE%\modele_dane\srodowisko\Scripts\python.exe" projekt\porownaj_rejestracje.py 1-94` | `wyniki/wyniki_dopasowania/porownanie_rejestracji.csv` (dopasowanie3 vs SimpleITK z `dopasowanie2_pi.py`) |
| Klatki jednego nagrania | ustaw `FILEPATH` w `projekt/read_flirpy.py` i uruchom bez argumentów | `frame_NNN.png` obok nagrania z `dane/` (albo `dane/dane_termowizja/<nagranie>/`) |
| Trening PanDerm | `projekt\modele_segmentacja\trenuj_panderm.bat` | wagi w `modele_dane\wagi\`, wykres w `wyniki/wyniki_segmentacji/` |
| Trening U-Netu (znacznik na termowizji, M3) | `projekt\modele_segmentacja\trenuj_unet_termal.bat` (GPU: kilka minut) | `modele_dane\wagi\unet_termal\fold1..5.onnx`, `wszystkie.onnx`; logi w `wyniki/wyniki_segmentacji/unet_termal/trening_<data>/` |
| Ocena U-Netu i detektora klasycznego względem CVAT | `projekt\modele_segmentacja\ocen_unet_termal.bat` | `wyniki/wyniki_segmentacji/unet_termal/ocena_<data>/` (CSV, podsumowanie, tabela LaTeX) |
| Baza danych | `projekt\baza_danych.bat utworz`, `importuj_wyniki`, `pokaz`, `eksport`, `eksport_piksele`, `sql "SELECT ..."` | `dane/baza.sqlite`; eksport: `wyniki/baza_wyniki_par.csv`, `wyniki/baza_piksele_znamion.csv` |

Aplikacja ma sześć zakładek – etapy z projektu systemu (kod etapów: `analiza/system.py`):
1. **Dane** – para z `dane/pary/N` (z adnotacjami z CVAT) albo dowolne dwa pliki,
2. **Rejestracja** – `dopasowanie3.py`, macierz T, nałożenie z suwakiem przezroczystości,
3. **Segmentacja** – narożniki znacznika automatycznie (wzorzec Π dopasowany do maski znacznika z rejestracji)
   → skala w mm; znamię modelem PanDerm (osobne środowisko modeli z PyTorch); znacznik na termowizji
   modelem U-Net (M3, plik ONNX przez OpenCV – bez PyTorch), niezależnie od rejestracji,
4. **Przeniesienie ROI** – znamię i znacznik zdjęcie → termowizja (T),
5. **Pomiary** – wymiary i kolor znamienia, kontrola skali, zgodność masek znacznika między modalnościami
   (badanie E2: maska ze zdjęcia przeniesiona przez T a maska z U-Netu; folia i otwór = ROI), ocena względem
   CVAT (gdy para ma adnotacje); piksele termowizji objęte przeniesionym znamieniem: współrzędne x, y
   i surowa intensywność z nagrania .SEQ; kliknięcie nazwy pokazuje objaśnienie,
6. **Raport** – `raport.html` (z objaśnieniem wszystkich wielkości), `metryki.json`, obrazy PNG,
   `piksele_znamienia_termal.csv` (`x;y;ulamek;w_masce;intensywnosc`); wpis analizy, jej miar i pikseli
   w bazie `dane/baza.sqlite`.

Intensywność pikseli to surowa wartość detektora z pierwszej klatki nagrania .SEQ (przed przeliczeniem na
temperaturę, bez palety i normalizacji `termal.jpg`). Para z bazy: `dane/pary/N/termal_surowe.npy`
(`temperatury_par.py`); własne pliki: nagranie `.SEQ` o tej samej nazwie co obraz termowizyjny, w tym samym
folderze (odczyt przez flirpy). Bez nagrania analiza działa, ale pikseli nie zapisuje (uwaga w raporcie).

Wszystko jest wyznaczane automatycznie; adnotacje z CVAT służą tylko do oceny wyników. Model przekształcenia
rejestracji ustawia `MODEL` w `dopasowanie3.py`. Podglądy: kółko myszy = powiększenie, przeciąganie = przesuwanie,
dwuklik = widok początkowy. Okna wyboru plików otwierają się w `dane/dane_RGB` i `dane/dane_termowizja`.
`dopasowanie3.py` zapisuje pliki diagnostyczne (`<wynik>_maska_*.png`, `<wynik>_debug_*.png`)
obok pliku wyniku — dane wejściowe nie są modyfikowane.

## Baza danych (SQLite)

`dane/baza.sqlite` (kod: `analiza/baza.py`). Obrazy i maski zostają w folderach, baza trzyma ścieżki
(względem folderu `Inzynierka`) i wszystkie wyniki liczbowe:

| Tabela | Zawartość | Źródło |
|---|---|---|
| `znamie` | numer znamienia, fold walidacji krzyżowej | `dane/znamiona.csv` |
| `para` | ścieżki zdjęcia, termowizji i mapy °C, oryginalne pliki (HEIC, SEQ), data, rozdzielczości | `dane/pary/N`, `dane/mapowanie_*.csv` |
| `adnotacja` | maski z CVAT (zdjęcie: znamię, znacznik; termowizja: znacznik), narożniki, homografia px → mm | `dane/pary/N/*.png`, `narozniki.json` |
| `analiza` | każde uruchomienie analizy pary: data, status (`ok`/`blad`), modele, macierz T, folder wyników, commit gita | aplikacja, `potok_pary.py` |
| `miara` | wszystkie liczby z `metryki.json` (grupa, nazwa, wartość, jednostka) | jw. |
| `piksel` | piksele termowizji objęte znamieniem: x, y, ułamek pokrycia, w masce (≥ 0,5), surowa intensywność | jw., `piksele_znamienia_termal.csv` |

Widoki: `ostatnia_analiza` (najnowsza udana analiza każdej pary), `wyniki_par` (jej miary z numerem znamienia
i foldem). Baza tworzy się sama przy pierwszym zapisie raportu; dotychczasowe wyniki dopisuje
`baza_danych.bat importuj_wyniki`. `analiza/dane.py` bierze informacje o parze (znamię, fold, oryginalne pliki)
z bazy, a gdy pary w niej nie ma – z plików CSV. Przykład:

```
baza_danych.bat sql "SELECT para, wartosc FROM wyniki_par WHERE grupa = 'zgodnosc_modalnosci.otwor' AND nazwa = 'dice'"
```

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
