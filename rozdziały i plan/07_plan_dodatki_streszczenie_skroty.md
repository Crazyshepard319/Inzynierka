# Plan dodatków A i B, streszczenia, abstraktu i wykazu skrótów (pkt 5 i 7)

Stan: 28.10.2026. Gotowy wzór: `praca/wzor/dodatek_a_instrukcja.tex`, `dodatek_b_dokumentacja.tex`, `streszczenie_abstract.tex`, `wykaz_skrotow.tex`.

**Budżet:** Dodatek A ≈ 2 s. · Dodatek B ≈ 2 s. (dodatki liczą się do limitu 30–40 s.). Streszczenie i Abstract – po ok. 0,5 s. (każde na osobnej stronie, zgodnie z szablonem PG).

**Różnica między dodatkami (najczęstszy błąd – mieszanie ich):**
- **A – instrukcja użytkownika**: dla osoby, która *używa* aplikacji (lekarz, student). Krok po kroku, co kliknąć i co zobaczy. Bez nazw modułów i funkcji.
- **B – dokumentacja techniczna**: dla osoby, która *utrzymuje lub rozwija* system (programista). Instalacja środowisk, struktura kodu, interfejsy, formaty plików, baza, testy, rozszerzanie.

---

## Dodatek A „Instrukcja użytkownika” (≈ 2 s.)

| Punkt | Co zawrzeć | Element |
|---|---|---|
| A.1 Wymagania i uruchomienie | Windows 10/11; zainstalowane środowisko aplikacji (instalacja – Dodatek B); uruchomienie: `inzynierka\Scripts\python.exe projekt\aplikacja.py`; segmentacja znamienia wymaga środowiska modeli (instaluje administrator). | – |
| A.2 Przygotowanie zdjęć | znacznik Π naklejony tak, by znamię leżało między ramionami; znacznik **cały w kadrze** obu urządzeń; zdjęcie prostopadle, bez lampy błyskowej / odblasku; termowizja: zapis nagrania .SEQ, obraz JPG z nagrania o tej samej nazwie w tym samym folderze (piksele znamienia). | (opcja) zdjęcie stanowiska |
| A.3 Okno aplikacji | 4 obszary (pasek etapów, panel, podglądy, status i dziennik) – odsyłacz do rys. 4.4; obsługa podglądu (kółko – powiększenie, przeciąganie, dwuklik). | odsyłacz do rys. 4.4 |
| A.4 Analiza pary krok po kroku | Tabela: zakładka → czynność → wynik. 1 Dane (para ze zbioru: numer, ◀ ▶; własne pliki) → 2 Rejestracja (Wykonaj / Wczytaj zapisaną, suwak, zapis nałożenia) → 3 Segmentacja (narożniki, znamię PanDerm, znacznik U-Net) → 4 Przeniesienie ROI → 5 Pomiary (tabela, kliknięcie nazwy = objaśnienie, uwagi) → 6 Raport (zapis, otwórz raport / folder, podgląd obrazów, w tym „Piksele”). Skrót: „Wykonaj wszystkie etapy”. | **Tab. A.1** + 1–2 zrzuty (zakładka 5 i 6) |
| A.5 Wyniki | Folder `wyniki/wyniki_obu/<para>/`: `raport.html`, `metryki.json`, obrazy PNG, `piksele_znamienia_termal.csv` (kolumny x, y, ułamek, w_masce, intensywność); jak czytać raport (uwagi na górze, objaśnienia na dole). | **Tab. A.2** pliki wynikowe |
| A.6 Komunikaty i rozwiązywanie problemów | Tabela: komunikat → przyczyna → co zrobić: brak pliku; „Nie znaleziono znacznika” / niska zgodność z Π (znacznik ucięty, odblask); „Najpierw wykonaj …” (kolejność etapów); brak środowiska modeli; brak nagrania .SEQ; Dice E2 < 0,85; TRE > 1 mm (para z adnotacjami). | **Tab. A.3** |

**Zrzuty ekranu do zrobienia (✍ Ty, para 14, „Wykonaj wszystkie etapy”):**
1. `interfejs_rejestracja.png` – zakładka „2. Rejestracja”, nałożenie z suwakiem ok. 50% → rys. 4.4 (obszary 1–4 opisz w podpisie albo TikZ-em).
2. `interfejs_pomiary.png` – zakładka „5. Pomiary”, przewinięte do sekcji „Piksele znamienia na termowizji”, z klikniętym objaśnieniem → Dodatek A.
3. `interfejs_raport.png` – zakładka „6. Raport”, podgląd „Piksele” → Dodatek A (opcjonalnie, gdy jest miejsce).

Zrzut: `Win + Shift + S` → okno; zapisz do `praca/rysunki/`. Szerokość w pracy: `\textwidth`.

**Zwroty (A):**
- „Aby rozpocząć analizę, należy …” · „Po wybraniu polecenia … system …”
- „Wynik etapu jest widoczny w …” · „W przypadku wyświetlenia komunikatu … należy …”
- „Przycisk … jest aktywny dopiero po …”
- forma: tryb bezosobowy albo bezokolicznik („Wybrać numer pary i kliknąć …”); trzymaj jedną formę.

---

## Dodatek B „Dokumentacja techniczna” (≈ 2 s.)

| Punkt | Co zawrzeć | Element |
|---|---|---|
| B.1 Środowiska i instalacja | Dwa środowiska: aplikacji (Python 3.14, `inzynierka\`: customtkinter, OpenCV, NumPy, Pillow, flirpy, matplotlib; SimpleITK tylko do E4) i modeli (Python 3.12 + PyTorch z CUDA, `%USERPROFILE%\modele_dane\srodowisko\`, lista w `modele_segmentacja/wymagania_srodowiska.txt`); wagi w `modele_dane\wagi\` (PanDerm, `unet_termal\fold1..5.onnx`, `wszystkie.onnx`); zmienna `MODELE_DANE`. Polecenia instalacji. | **Tab. B.1** środowiska |
| B.2 Struktura folderów i kodu | `projekt/` (aplikacja, analiza/, modele_segmentacja/, skrypty), `dane/`, `wyniki/`, `praca/`; opis modułów `analiza/` (system, dane, geometria, miary, pomiary, obrazy, raport, baza). | **Tab. B.2** moduły |
| B.3 Interfejs programistyczny | klasa `Analiza`: metody = etapy (kolejność, wyjątek `BladEtapu`); funkcje `analizuj`, `analizuj_z_zapisanych`; przykład użycia w 8 liniach (jedyny listing w pracy). | **Listing B.1** |
| B.4 Formaty danych | `dane/pary/N/` (rgb.jpg, termal.jpg, termal_surowe.npy, termal_C.npy, maski, narozniki.json); macierz T (`dopasowanie_macierz.txt`); `metryki.json` (grupy); CSV pikseli; pliki ONNX. | **Tab. B.3** pliki |
| B.5 Baza danych | schemat (odsyłacz do rys. 4.2), wersja schematu 2, migracja, polecenia `baza_danych.bat`, przykładowe zapytania SQL (miary pary, piksele znamienia). | **Listing B.2** (SQL, 3–4 linie) |
| B.6 Skrypty wsadowe i trening | `potok_pary.bat` (+ `--z_zapisanych`), `raport_zbiorczy.bat`, `porownaj_rejestracje.py` (E4), `trenuj_panderm.bat`, `trenuj_unet_termal.bat`, `ocen_unet_termal.bat`, `temperatury_par.py --tylko_surowe`, `import_cvat.py`, `read_flirpy.py`, `heic_do_jpg.py`. | **Tab. B.4** skrypty |
| B.7 Testy i rozszerzanie | `projekt/testy/uruchom_testy.bat` (18 testów); dodanie modelu segmentacji (nowy folder w `modele/` z klasą `Model(ModelSegmentacji)` – wykrywany automatycznie); nowa miara → `metryki.json` → automatycznie w tabeli `miara` (bez zmiany schematu); parametry rejestracji (`MODEL`, `MIN_ZGODNOSC`, `RGB_DET_PX` w `dopasowanie3.py`). | – |

**Zwroty (B):**
- „Kod źródłowy podzielono na następujące moduły: …”
- „Środowisko instaluje się poleceniem …”
- „Klasa … udostępnia metody …, które należy wywoływać w kolejności …”
- „Plik … zawiera …; format opisano w tabeli B.3.”
- „Dodanie nowego modelu wymaga jedynie …”
- „Parametry metody zdefiniowano jako stałe w module …”

---

## Streszczenie i Abstract (pkt 7)

**Budowa (≈ 200–250 słów, jeden akapit albo dwa):**
1. Kontekst i problem (1–2 zdania): termografia uzupełnia zdjęcie, ale wymaga rejestracji; znamię niewidoczne na termogramie.
2. Cel (1 zdanie).
3. Metoda (3–4 zdania): znacznik Π, ECC na maskach, M1 (PanDerm + UperNet), M3 (U-Net), przeniesienie ROI, miary, piksele z .SEQ, aplikacja + baza SQLite.
4. Wyniki (2–3 zdania, liczby): 92/94 par, mediana TRE 0,61 mm (85% ≤ 1 mm), MI 3,36 mm; U-Net Dice 0,969; PanDerm Dice 0,870; E2 Dice folii 0,957, ρ = −0,72 z TRE.
5. Wniosek (1 zdanie).

**Słowa kluczowe (5–6):** rejestracja obrazów wielomodalnych; termowizja; segmentacja obrazów medycznych; znamię barwnikowe; znacznik referencyjny; uczenie głębokie.
**Keywords:** multimodal image registration; thermal imaging; medical image segmentation; melanocytic nevus; fiducial marker; deep learning.
**Dziedzina nauki i techniki (OECD)** – w szablonie PG: „Nauki inżynieryjne i techniczne, inżynieria biomedyczna” – **sprawdź** listę w szablonie.

**Zwroty (Streszczenie):** „W pracy przedstawiono …”, „Celem pracy było …”, „Zaprojektowano i zaimplementowano …”, „Weryfikację przeprowadzono na …”, „Uzyskano …”, „Wyniki wskazują, że …”.
**Phrases (Abstract):** “This thesis presents …”, “The aim of the work was …”, “The system was evaluated on …”, “The median target registration error was …”, “The results show that …”. W angielskim kropka dziesiętna (0.61 mm), nie przecinek.

---

## Wykaz ważniejszych oznaczeń i skrótów

Gotowy: `praca/wzor/wykaz_skrotow.tex` (oznaczenia + skróty, alfabetycznie, rozwinięcie PL i EN). Zasady:
- tylko skróty i symbole, które **występują w tekście** pracy (sprawdzone w rozdz. 1–7 i dodatkach wzoru);
- przy pierwszym użyciu w tekście skrót i tak trzeba rozwinąć;
- nazwy własne (PanDerm, OpenCV, SQLite) nie są skrótami – nie wpisuj ich;
- stary wykaz (SIFT, SURF, ORB) – usuń, tych metod już nie opisujesz.
