# Materiały do rozdziałów 1, 3 i 4 – co napisać i jakimi zwrotami (pkt 1)

Stan: 26.10.2026. To są **materiały**: lista treści, fakty o systemie z liczbami i zwroty. Gotowy wzór tekstu będzie w pkt 6. Pliki z wcześniejszych punktów: `03_streszczenia_artykulow.md` (literatura), `plan_pracy.md` (spis treści, budżet stron).

Budżet stron (decyzja z 26.10): Wstęp ≈ 2 s. · Analiza projektowa ≈ 4 s. · Projekt systemu ≈ 4,5 s.

---

## 0. Zasady ogólne (wszystkie rozdziały)

**Styl bezosobowy.** Piszemy „zaprojektowano”, „przyjęto”, „w pracy przedstawiono”, „system wyznacza”. Nie piszemy „zaprojektowałem”, „zrobiliśmy”, „nasz system”.

| Sytuacja | Forma | Przykład |
|---|---|---|
| Wykonana praca autora | czas przeszły, forma na -no/-to | „Zaprojektowano znacznik…”, „Przyjęto model afiniczny…” |
| Opis działania systemu | czas teraźniejszy, system jako podmiot | „System wyznacza macierz T…”, „Moduł zapisuje wyniki…” |
| Zawartość pracy | strona bierna / „w pracy” | „W rozdziale 3 przedstawiono…”, „Opisano…” |
| Uzasadnienie decyzji | „ze względu na”, „ponieważ” | „Wybrano SQLite, ponieważ baza nie wymaga serwera.” |

**Zapis liczb i jednostek:**
- przecinek dziesiętny (0,97, a nie 0.97);
- spacja przed jednostką (17 mm, 289 mm²);
- znak × w wymiarach (320 × 240 px).

**Terminy:** polski termin + angielski w nawiasie przy pierwszym użyciu: rejestracja obrazów (ang. *image registration*), obszar zainteresowania (ang. *region of interest*, ROI). Skrót wpisz też do „Wykazu ważniejszych oznaczeń i skrótów” (dziś są tam tylko SIF, SURF, ORB – do wymiany).

**Spójne nazwy w całej pracy.** Raz ustalona nazwa obowiązuje wszędzie:
- znacznik Π (nie zamiennie „marker”, „taśma”, „ㄇ”);
- macierz T;
- model M1 (PanDerm + UperNet), model M3 (U-Net);
- badania E1, E2, E4.

**Odsyłacze.** Rysunki i tabele są zapowiadane w tekście przed ich pojawieniem się („…przedstawiono na rysunku 3.1”). Każdy musi mieć podpis i odwołanie w tekście.

### Wymagania promotorki → gdzie w pracy

| Wymaganie (7 punktów) | Rozdział |
|---|---|
| 1. Baza danych | 4.3 (projekt), 5.6 (implementacja) |
| 2. Projekt systemu | 3 (analiza), 4 (projekt) |
| 3. Implementacja | 5 |
| 4. Modele segmentacji dla każdej modalności (dane, architektura, ocena jakości) | 5.3 (dane, architektura), 6.3 (ocena) |
| 5. Miary zgodności ROI | 2.4 (literatura), 5.5 (implementacja), 6.4 (wyniki) |
| 6. Weryfikacja systemu i wnioski | 6, 7 |
| 7. Dokumentacja techniczna i instrukcja | Dodatek A (instrukcja), Dodatek B (dokumentacja) |

W 1.2 (zakres pracy) warto wymienić te same punkty – recenzent łatwo sprawdzi, że wszystkie zrealizowano.

---

## 1. Rozdział 1 „Wstęp” (≈ 2 strony)

**Rola rozdziału:** odpowiada na pytania: dlaczego temat jest ważny, co jest celem, co dokładnie zrobiono (zakres) i jak zbudowana jest praca. Czytelnik po Wstępie wie, czego się spodziewać, ale nie zna jeszcze szczegółów metod ani wyników.

**Czego NIE pisać we Wstępie:**
- przeglądu literatury (to rozdział 2) – wystarczą 3–5 cytowań do motywacji;
- szczegółów algorytmów (ECC, U-Net) – tylko ich nazwy;
- wyników liczbowych (to rozdział 6 i Streszczenie) – najwyżej jedno zdanie w zakresie;
- historii prób i błędów („najpierw próbowano SimpleITK…”) – jeśli w ogóle, to w rozdz. 6 (badanie E4).

### 1.1 Motywacja (≈ 0,75 s.)

**Co powinno się znaleźć (kolejność „od ogółu do szczegółu”):**
1. Problem kliniczny: ocena zmian skórnych (znamion), znaczenie wczesnego wykrywania czerniaka. Krótko, 1–2 zdania z cytatem (`dermoscopy`, `visualization-detection-cancer`).
2. Dwie komplementarne modalności: zdjęcie RGB (morfologia: barwa, brzeg, kształt) i termografia (rozkład temperatury, informacja funkcjonalna). Źródła: `infared-thermal-imaging`, `magalhaes2019`, `deep-learning`.
3. Trudność 1 – rejestracja: dwa niezależne urządzenia, inne pole widzenia, rozdzielczość (320 × 240 px vs zdjęcie z telefonu o dłuższym boku 1104–3274 px w Twoim zbiorze), inny mechanizm powstawania obrazu (`visible-and-infared`, `deep-learning`).
4. Trudność 2 – znamię bez schładzania skóry jest **niewidoczne na termogramie** (`visualization-detection-cancer`), więc nie może być punktem odniesienia → potrzebny znacznik widoczny w obu modalnościach.
5. Trudność 3 – jak sprawdzić, że ten sam obszar wyznaczono poprawnie w obu obrazach, bez ręcznych adnotacji? → modele segmentacji dedykowane każdej modalności i porównanie masek.
6. Zdanie przejściowe do celu: „Powyższe problemy stanowią motywację do opracowania systemu…”.

**Przydatne zwroty:**
- „Obrazowanie termowizyjne jest nieinwazyjną metodą pomiaru…”
- „W ostatnich latach rośnie zainteresowanie…”
- „Istotnym ograniczeniem … jest…”
- „Obie modalności mają charakter komplementarny: …, natomiast …”
- „Warunkiem wspólnej analizy obu obrazów jest…”
- „Zagadnienie to jest nietrywialne, ponieważ…”
- „Dodatkową trudność stanowi fakt, że…”
- „W praktyce klinicznej oznacza to, że…”
- „Brakuje rozwiązania, które…” / „Dotychczasowe rozwiązania wymagają…”
- „Powyższe obserwacje stanowią motywację do podjęcia niniejszej pracy.”

### 1.2 Cel i zakres pracy (≈ 0,75 s.)

**Cel** – jedno–dwa zdania, zgodne z kartą tematu. Ustalone sformułowanie celu:
> System rejestruje zdjęcie RGB i obraz termowizyjny zmiany skórnej we wspólnej przestrzeni odniesienia i przenosi zaznaczony obszar zainteresowania między modalnościami. Wyznacza parametry ilościowe ROI. Zgodność wyznaczenia ROI weryfikuje przez porównanie masek z modeli segmentacji dedykowanych każdej modalności. Wynikiem jest raport z miarami zgodności.

Sprawdź brzmienie w karcie tematu (moja PG) – cel w pracy powinien się z nią pokrywać.

**Zakres** – lista zadań wykonanych w pracy (najlepiej wypunktowanie, bo recenzent je odhacza):
1. Przegląd literatury: rejestracja wielomodalna, segmentacja, miary oceny.
2. Analiza wymagań i projekt systemu: przypadki użycia, architektura, diagram klas, baza danych SQLite, interfejs.
3. Projekt znacznika referencyjnego Π (35 × 26 mm, pasek 9 mm, otwór 17 × 17 mm) widocznego w obu modalnościach.
4. Zebranie własnego zbioru: 94 pary RGB–termowizja, 34 znamiona (2–3 pary na znamię), seria z 23.10.2026. Ręczne adnotacje w CVAT (maska znamienia, maski znacznika, narożniki).
5. Implementacja modułu rejestracji: automatyczna detekcja znacznika, wstępne dopasowanie, doprecyzowanie metodą ECC (przekształcenie afiniczne / homografia).
6. Modele segmentacji dla obu modalności:
   - zdjęcie – PanDerm + UperNet (M1), douczony na ISIC 2018;
   - termowizja – U-Net (M3), uczony na własnych danych z 5-krotną walidacją krzyżową po znamionach.
7. Przeniesienie ROI, pomiary w mm (skala z narożników znacznika) i miary zgodności (Dice, IoU, HD95, ASSD, TRE).
8. Aplikacja z interfejsem graficznym (6 etapów), potok wsadowy, raport HTML/JSON i zapis w bazie.
9. Weryfikacja systemu:
   - E1 – dokładność rejestracji względem CVAT;
   - E2 – zgodność masek między modalnościami bez adnotacji;
   - E4 – porównanie z rejestracją przez informację wzajemną;
   - ocena segmentacji względem CVAT.
10. Dokumentacja techniczna i instrukcja użytkownika.

**Ograniczenia zakresu** (ważne – chronią przed zarzutami recenzenta):
- system nie stawia diagnozy i nie klasyfikuje zmian (nie jest wyrobem medycznym);
- temperatury nie są częścią raportu – termografia dynamiczna to tylko kontekst (zdanie warunkowe: „do decyzji promotorki”);
- znamię nie jest widoczne na termowizji, więc obszarem porównywanym między modalnościami jest otwór znacznika Π (ROI), a nie znamię;
- jeden zestaw kamer, jedna seria pomiarowa, zdjęcia wykonane przez autora.

**Wkład własny** (opcjonalny akapit; na PG często oczekiwany): wskaż, co jest Twoje, a co gotowe:
- gotowe: koder PanDerm (wagi autorów), OpenCV, CVAT;
- Twoje: znacznik, zbiór danych i adnotacje, metoda rejestracji na maskach znacznika, trening M1 i M3, badania E1/E2/E4, aplikacja, baza.

**Przydatne zwroty:**
- „Celem pracy jest opracowanie, implementacja oraz ocena systemu…”
- „Aby osiągnąć ten cel, zrealizowano następujące zadania: …”
- „Zakres pracy obejmuje…” / „Zakres pracy nie obejmuje…”
- „Przyjęto następujące ograniczenia: …”
- „Praca ma charakter projektowo-badawczy.”
- „Wkład własny autora obejmuje…”
- „W pracy wykorzystano gotowy model…, który douczono na…”

### 1.3 Struktura pracy (≈ 0,3 s.)

Jedno zdanie na rozdział (i na dodatki), w kolejności spisu treści. Bez powtarzania tytułów słowo w słowo.

**Zwroty:**
- „Praca składa się z siedmiu rozdziałów oraz dwóch dodatków.”
- „Rozdział 2 zawiera przegląd literatury dotyczącej…”
- „W rozdziale 3 przedstawiono analizę wymagań…”
- „Rozdział 4 opisuje projekt systemu, w tym…”
- „Implementację poszczególnych modułów omówiono w rozdziale 5.”
- „Rozdział 6 przedstawia wyniki badań…”
- „Pracę zamyka podsumowanie wraz z kierunkami dalszych prac.”
- „Dodatek A zawiera instrukcję użytkownika, a Dodatek B – dokumentację techniczną.”

**Typowe błędy we Wstępie:** cel sformułowany jako czynność („Celem jest zbadanie…” bez produktu); brak zakresu; zakres niezgodny z tym, co jest w rozdz. 5–6; wyniki liczbowe; zbyt długa motywacja (> 1 strony).

---

## 3. Rozdział 3 „Analiza projektowa” (≈ 4 strony)

**Rola rozdziału:** opisuje, **CO** system ma robić i w jakich warunkach – bez szczegółów technicznych (to rozdział 4) i bez kodu (rozdział 5). Rozdział łączy cel z Wstępu z projektem: każde wymaganie powinno mieć uzasadnienie w celu lub w ograniczeniach.

Stara wersja (rozdz. 2 w PDF) opisywała system z SimpleITK (czas 20–30 s, metryka Mattesa). Wszystko poniżej dotyczy **obecnego** systemu.

### 3.1 Założenia i ograniczenia (≈ 0,5 s.)

**Co opisać:**
- **Użytkownicy:** studenci i lekarze współpracujący z Uniwersyteckim Centrum Klinicznym w Gdańsku (tak było w starej wersji – potwierdź z promotorką).
- **Dane wejściowe:**
  - zdjęcie RGB z telefonu (JPG; oryginały HEIC konwertowane `heic_do_jpg.py`);
  - obraz termowizyjny 320 × 240 px z nagrania .seq (klatka wyodrębniona `read_flirpy.py`);
  - model kamery termowizyjnej z serii 23.10 – **uzupełnij** (stary tekst podawał FLIR A655sc 640 × 480, to nieaktualne).
- **Dwa niezależne urządzenia:**
  - kamery nie są zintegrowane ani skalibrowane względem siebie;
  - zdjęcia wykonywane z ręki, z różnych odległości i pod różnymi kątami;
  - stąd potrzeba rejestracji dla każdej pary osobno.
- **Znacznik Π** naklejany na skórę, znamię leży między ramionami (w otworze). Założenie: skóra w obrębie znacznika jest w przybliżeniu płaska → przekształcenie afiniczne / homografia wystarcza.
- **Znamię niewidoczne w termowizji** (bez schładzania) → w termowizji segmentuje się znacznik, a nie znamię.
- **Adnotacje z CVAT** służą wyłącznie do oceny; system działa w pełni automatycznie.
- **Środowisko:** komputer z Windows. PanDerm wymaga osobnego środowiska z PyTorch (GPU opcjonalne; Twoje: ≤ 8 GB VRAM). U-Net działa bez PyTorch (ONNX przez OpenCV).
- **Poza zakresem:** diagnoza, temperatury w raporcie, praca w czasie rzeczywistym, obsługa wielu użytkowników / sieci.

**Zwroty:**
- „Przy projektowaniu systemu przyjęto następujące założenia: …”
- „Zakłada się, że…” / „Przyjęto, że skóra w obrębie znacznika jest w przybliżeniu płaska.”
- „System jest przeznaczony dla…”
- „Ze względu na … nie jest możliwe…, dlatego…”
- „Ograniczeniem wynikającym z … jest…”
- „System nie stanowi narzędzia diagnostycznego; jego zadaniem jest…”

### 3.2 Wymagania funkcjonalne (≈ 1 s.)

**Forma:** tabela z identyfikatorami (WF1…WFn), krótkim opisem i priorytetem. Identyfikatory przydają się później: diagram przypadków użycia i testy funkcjonalne (6.6) mogą się do nich odwoływać („WF5 – spełnione”).

Propozycja listy (zgodna z tym, co system robi dziś):

| ID | Wymaganie (system umożliwia / system…) | Gdzie w kodzie |
|---|---|---|
| WF1 | wczytanie pary obrazów: z bazy (numer pary) albo dwóch dowolnych plików | zakładka 1, `Analiza.z_pary`, `Analiza(...)` |
| WF2 | automatyczną rejestrację: detekcja znacznika w obu modalnościach i wyznaczenie macierzy T | zakładka 2, `dopasowanie3.run_registration` |
| WF3 | podgląd nałożenia obrazów z regulowaną przezroczystością i zapis nałożenia | zakładka 2 |
| WF4 | wyznaczenie 8 narożników znacznika i skali px → mm w obu modalnościach | zakładka 3, `ustaw_narozniki` |
| WF5 | automatyczną segmentację znamienia na zdjęciu (PanDerm, we wnętrzu znacznika) | zakładka 3, `segmentuj_znamie` |
| WF6 | segmentację znacznika na termowizji modelem U-Net niezależnie od rejestracji | zakładka 3, `segmentuj_znacznik_termal` |
| WF7 | przeniesienie ROI (znamię, obrys i otwór znacznika) ze zdjęcia na termowizję | zakładka 4, `przenies` |
| WF8 | pomiary znamienia w mm: pole, obwód, średnica równoważna, średnice Fereta, kolistość, asymetria, barwa w Lab | zakładka 5, `pomiary.parametry_rgb` |
| WF9 | wyznaczenie zgodności masek znacznika między modalnościami (E2: Dice, IoU, HD95, ASSD, przesunięcie środków, stosunek pól) | zakładka 5, `zgodnosc_modalnosci` |
| WF10 | ocenę wyników względem adnotacji CVAT, gdy są dostępne (TRE, zgodność segmentacji) | zakładka 5, `zmierz` |
| WF11 | wygenerowanie raportu (HTML + JSON + obrazy PNG) z objaśnieniem wielkości | zakładka 6, `zapisz_raport` |
| WF12 | zapis każdej analizy i jej miar w bazie danych | `Baza.zapisz_analize` |
| WF13 | przetwarzanie wsadowe wielu par i raport zbiorczy | `potok_pary.py`, `raport_zbiorczy.py` |
| WF14 | wykonanie wszystkich etapów jednym poleceniem | przycisk „Wykonaj wszystkie etapy” |

Uwaga: w pracy podaj tylko kolumny ID / wymaganie / (priorytet). Kolumna „Gdzie w kodzie” jest dla Ciebie – przyda się w rozdz. 5 i w dokumentacji.

**Zwroty:**
- „Wymagania funkcjonalne zestawiono w tabeli 3.1.”
- „System powinien umożliwiać…” / „System umożliwia…” (wybierz jedną formę i trzymaj się jej)
- „Wymaganie WF6 wynika bezpośrednio z celu pracy…”
- „Wymagania zostały pogrupowane według etapów przetwarzania.”
- „Priorytet wymagań określono w skali: wymagane / pożądane.”

### 3.3 Wymagania pozafunkcjonalne (≈ 0,75 s.)

**Forma:** tabela WN1…WNn pogrupowana według kategorii. Każde wymaganie powinno być **mierzalne** albo weryfikowalne. Zapis „system jest szybki” jest zły, a „rejestracja jednej pary trwa < 15 s na komputerze klasy PC” – dobry.

| Kategoria | Propozycja wymagania | Fakty / jak zweryfikować |
|---|---|---|
| Wydajność | Rejestracja jednej pary trwa krócej niż X s na komputerze użytkownika | Mój pomiar 26.10 (maszyna wirtualna, 2 rdzenie CPU, 5 par): **5,3–8,0 s, średnio 6,5 s**. Zmierz na swoim laptopie i wpisz próg z zapasem. Stary system: 20–30 s. |
| Wydajność | Segmentacja znacznika na termowizji < 1 s bez GPU | U-Net ONNX przez OpenCV: **ok. 67 ms / obraz** (ta sama VM, CPU). |
| Wydajność | Interfejs nie blokuje się w czasie obliczeń | Obliczenia w osobnym wątku; przyciski blokowane, pasek postępu, log. |
| Dokładność | Kryterium akceptacji rejestracji, np. mediana TRE ≤ 1 mm | E1: mediana TRE 0,61 mm. Próg ustal i uzasadnij **przed** pokazaniem wyników (np. względem otworu 17 mm albo rozmiaru znamion). |
| Dokładność | Kryterium segmentacji, np. Dice ≥ 0,9 dla znacznika na termowizji | U-Net vs CVAT: Dice 0,969. |
| Niezawodność | Czytelny komunikat zamiast awarii przy złych danych (brak pliku, brak znacznika, pusta maska) | wyjątek `BladEtapu`. Ostrzeżenie, gdy zgodność kształtu znacznika z wzorcem Π < 0,65 (pary 75, 76 odrzucone). |
| Użyteczność | Etapy w stałej kolejności (6 zakładek), objaśnienie każdej miary, podgląd z powiększaniem | zakładki 1–6; kliknięcie nazwy miary pokazuje objaśnienie. |
| Przenośność / instalacja | Aplikacja działa bez PyTorch; PanDerm w osobnym środowisku | ONNX przez `cv2.dnn`; środowisko modeli: `modele_segmentacja/README.md`. |
| Utrzymywalność | Wspólny kod etapów dla GUI i potoku wsadowego; modułowa budowa | klasa `Analiza` w `analiza/system.py`. |
| Powtarzalność | Każda analiza zapisana z datą, modelami, macierzą T i wersją kodu (commit) | tabela `analiza` w bazie. |
| Ochrona danych | Brak danych osobowych w systemie; pary i znamiona identyfikowane numerami; dane lokalnie | baza zawiera numery i ścieżki, bez nazwisk. |

**Zwroty:**
- „Wymagania pozafunkcjonalne określają…” / „…dotyczą jakości działania systemu.”
- „Przyjęto, że czas … nie powinien przekraczać…”
- „Wymaganie to weryfikowano przez pomiar…”
- „Za kryterium akceptacji przyjęto…”
- „System powinien zachować responsywność interfejsu podczas…”
- „W przypadku niepowodzenia etapu system wyświetla komunikat…”

### 3.4 Przypadki użycia (≈ 1 s.)

**Co opisać:** aktorzy, diagram UML przypadków użycia (rysunek – pkt 5), 1–2 scenariusze tekstowe dla głównych przypadków.

**Aktorzy – propozycja:**
- **Użytkownik** (student / lekarz) – analiza pary, przegląd raportu.
- **Badacz / administrator danych** (opcjonalnie; w praktyce Ty): import adnotacji CVAT, trening modeli, przetwarzanie wsadowe, raport zbiorczy, obsługa bazy. Drugi aktor pokazuje, że system ma dwie warstwy użycia (kliniczną i badawczą). Jeśli chcesz prościej – jeden aktor jak w starej wersji.

**Przypadki użycia (Użytkownik):**
- PU1 Wczytaj parę obrazów («include»: wybierz parę z bazy | wybierz pliki – jako alternatywa)
- PU2 Wykonaj rejestrację («include»: wykryj znacznik, wyznacz macierz T)
- PU3 Oceń nałożenie («extend» PU2: zmień przezroczystość, zapisz nałożenie)
- PU4 Wyznacz obszary (segmentacja znamienia i znacznika, narożniki)
- PU5 Przenieś ROI na termowizję
- PU6 Oblicz pomiary i zgodność («extend»: ocena względem CVAT – tylko gdy są adnotacje)
- PU7 Wygeneruj raport («include»: zapisz w bazie)
- PU8 Wykonaj wszystkie etapy («include» PU2–PU7)

**Badacz:** PU9 Importuj adnotacje CVAT · PU10 Trenuj model segmentacji · PU11 Przetwórz pary wsadowo · PU12 Wygeneruj raport zbiorczy · PU13 Przeglądaj / eksportuj bazę.

**Szablon scenariusza (tabela):** Nazwa · Aktor · Warunki początkowe · Scenariusz główny (kroki 1…n) · Scenariusze alternatywne · Warunki końcowe.

Przykład scenariuszy alternatywnych dla PU2:
- 2a – znacznik nie wykryty → komunikat, koniec;
- 2b – zgodność z wzorcem < 0,65 → ostrzeżenie;
- 2c – homografia niestabilna → system wybiera model afiniczny.

**Zwroty:**
- „Funkcjonalność systemu przedstawiono w postaci diagramu przypadków użycia (rys. 3.1).”
- „W systemie wyróżniono dwóch aktorów: …”
- „Przypadek użycia … obejmuje (relacja «include»)…”
- „Przypadek … jest opcjonalnym rozszerzeniem (relacja «extend») przypadku…”
- „Scenariusz główny przypadku użycia … przedstawiono w tabeli 3.3.”
- „Warunkiem rozpoczęcia jest…”, „W wyniku wykonania przypadku użycia…”

### 3.5 Architektura systemu (≈ 0,75 s.)

**Co opisać:** podział na warstwy / moduły i przepływ danych – na poziomie bloków, bez nazw funkcji. Rysunek: schemat blokowy potoku (pkt 5).

**Fakty do opisu:**
- **Architektura potokowa** (ang. *pipeline*): 6 etapów – wejście → rejestracja → segmentacja → przeniesienie ROI → pomiary → raport. Każdy etap korzysta z wyników poprzedniego; system sprawdza, czy poprzedni etap wykonano.
- **Warstwy:**
  - prezentacji – aplikacja okienkowa i skrypty `.bat`;
  - logiki – klasa `Analiza`, wspólna dla GUI i potoku wsadowego;
  - modułów obliczeniowych – rejestracja, segmentacja, geometria, miary, pomiary, raport;
  - danych – pliki obrazów i masek + baza SQLite ze ścieżkami i wynikami.
- **Dwa środowiska uruchomieniowe:**
  - aplikacja (lekka, bez PyTorch);
  - środowisko modeli z PyTorch (PanDerm, trening). Aplikacja uruchamia PanDerm jako osobny proces.
  - U-Net wyeksportowany do ONNX działa bezpośrednio w aplikacji.
- **Niezależność ścieżek dla badania E2:** maska znacznika z termowizji (U-Net) nie bierze udziału w wyznaczaniu T, dlatego porównanie z maską przeniesioną ze zdjęcia jest niezależną kontrolą rejestracji.

**Zwroty:**
- „System zaprojektowano w architekturze potokowej, w której…”
- „Wyróżniono następujące moduły: …”
- „Moduł … odpowiada za…”
- „Przepływ danych między modułami przedstawiono na rysunku 3.2.”
- „Rozdzielenie … i … pozwala…”
- „Dzięki temu ten sam kod jest wykorzystywany zarówno przez…, jak i…”

**Typowe błędy w rozdz. 3:** wymagania niemierzalne; wymagania opisujące implementację („system używa OpenCV” – to decyzja projektowa, rozdz. 4); diagram UC bez opisu; aktorzy-systemy (CVAT nie jest aktorem, jeśli system się z nim nie łączy).

---

## 4. Rozdział 4 „Projekt systemu” (≈ 4,5 strony)

**Rola rozdziału:** opisuje, **JAK** spełniono wymagania z rozdz. 3: decyzje projektowe z uzasadnieniem i odrzuconymi alternatywami. Kod i szczegóły algorytmów są w rozdz. 5. Dobry test: każda decyzja w rozdz. 4 ma „ponieważ” i odsyłacz do wymagania (WFx / WNx) albo ograniczenia.

### 4.1 Dobór technologii (≈ 1 s.)

**Forma:** tabela element → technologia → uzasadnienie (+ rozważona alternatywa). Podawaj wersje bibliotek, bo to część dokumentacji. Są **dwa środowiska**:
- aplikacja (`inzynierka\`): Python 3.14.3, OpenCV 4.13.0, NumPy 2.4.3, customtkinter 5.2.2, SimpleITK 2.5.3, flirpy 0.3.0, matplotlib 3.10.8, Pillow 12.1.1;
- modele (`modele_dane\srodowisko`, lista w `modele_segmentacja/wymagania_srodowiska.txt`): PyTorch 2.11.0 + CUDA 12.8, torchvision 0.26.0, OpenCV 5.0.0, NumPy 2.5.2, SimpleITK 2.5.6, onnx.

Wersje odczytano 26.10 z zainstalowanych pakietów.

| Element | Technologia | Uzasadnienie | Rozważona alternatywa |
|---|---|---|---|
| Język | Python 3.14 (aplikacja) | ekosystem przetwarzania obrazów i uczenia głębokiego; jeden język dla aplikacji i modeli | – |
| Przetwarzanie obrazów, rejestracja | OpenCV (`findTransformECC`, segmentacja interaktywna, morfologia) | gotowa implementacja ECC (`evangelidis2008`); szybkie | SimpleITK + informacja wzajemna (metryka `MattesMutualInformation`; cytować ogólnie `zitova2003`/`correlation-ratio`, bez Mattesa) – wcześniejsza wersja, porównana w E4 (mediana TRE 3,47 vs 0,62 mm) |
| Obliczenia | NumPy | standard | – |
| Uczenie głębokie | PyTorch 2.11 (CUDA 12.8), osobne środowisko | trening PanDerm i U-Net; wagi PanDerm udostępnione w PyTorch | – |
| Wnioskowanie U-Net w aplikacji | ONNX + `cv2.dnn` | aplikacja nie wymaga PyTorch; ok. 67 ms / obraz na CPU | wnioskowanie w PyTorch (ciężkie środowisko) |
| Model znamienia | PanDerm (ViT-L) + UperNet | model bazowy dermatologii; segmentacja ISIC 2018 (`yan2025panderm`) | – |
| Model termowizji | U-Net (1,94 mln parametrów) | mało danych (94 obrazy), mały obraz 320 × 240 (`ronneberger2015`) | detektor klasyczny (zostaje w rejestracji; Dice 0,954 vs 0,969) |
| Interfejs | customtkinter 5.2 (nakładka na tkinter) | lekki, otwarta licencja, nowoczesny wygląd; tkinter jest częścią Pythona | stary interfejs w tkinter (1 okno) |
| Baza danych | SQLite (moduł `sqlite3`) | jeden plik, bez serwera, wystarczający dla jednego użytkownika; SQL do analiz | pliki CSV (poprzednio) – brak relacji i historii analiz |
| Adnotacje | CVAT (eksport „CVAT for images 1.1”) | maski i punkty (narożniki), praca w przeglądarce | – |
| Raport | HTML + JSON + PNG | HTML czytelny bez dodatkowych programów; JSON do dalszej analizy | PDF |
| Konwersja danych | flirpy 0.3.0 (`read_flirpy.py`: SEQ → obraz), pillow-heif (`heic_do_jpg.py`: HEIC → JPG, instalowany doraźnie) | formaty z kamery i telefonu | – |
| Kontrola wersji | git | historia kodu; wersja kodu zapisywana przy każdej analizie | – |

**Zwroty:**
- „Przy wyborze technologii kierowano się następującymi kryteriami: …”
- „Zdecydowano się na…, ponieważ…”
- „Alternatywą było…, jednak…”
- „Wybór ten wynika z wymagania WN…”
- „Zastosowanie formatu ONNX pozwoliło…”
- „Zestawienie wykorzystanych bibliotek wraz z wersjami zawiera tabela 4.1.”

### 4.2 Projekt znacznika referencyjnego Π (≈ 1 s.)

**Co opisać:**
1. **Wymagania wobec znacznika** (wynikają z rozdz. 3):
   - widoczny w obu modalnościach;
   - kształt pozwalający jednoznacznie wyznaczyć położenie, skalę i kąt;
   - punkty charakterystyczne (narożniki) do skali w mm i do oceny TRE;
   - miejsce na znamię (ROI);
   - tani, jednorazowy, łatwy do naklejenia.
2. **Materiał:** taśma pokryta folią aluminiową.
   - Termowizja: folia ma niską emisyjność i odbija otoczenie, więc wygląda inaczej niż skóra (ciemniejsza lub teksturowana – tak działa detektor).
   - Zdjęcie: szara, metaliczna, z teksturą załamań, chłodniejsza w barwie od skóry.
   - Uwaga: zjawisko emisyjności opisz ostrożnie (źródło: `infared-thermal-imaging` – emisyjność skóry 0,96–0,98). Emisyjności folii nie podawaj liczbowo bez źródła.
3. **Kształt i wymiary:**
   - belka 35 mm, ramiona 26 mm, szerokość paska 9 mm;
   - otwór 17 × 17 mm = 289 mm²;
   - 8 narożników;
   - znamię leży między ramionami.
4. **Uzasadnienie kształtu Π:**
   - brak symetrii obrotowej → kąt jednoznaczny w 360°;
   - otwór wyznacza ROI;
   - narożniki dają homografię px → mm.
   - Ograniczenie: Π ma oś symetrii lustrzanej, więc odbicie lustrzane obrazu dałoby fałszywe dopasowanie (ramiona zamienione, błąd ok. 25 mm na parach 10, 55, 72). Kamery nie odwracają obrazu, więc sprawdzanie odbicia wyłączono (`SPRAWDZ_LUSTRO = False`).
5. **Ewolucja** (1–2 zdania): wcześniej znacznik o dowolnym kształcie bez wyróżnionych punktów (stary rozdz. 3) → kształt Π z wzorcem i narożnikami.

**Zwroty:**
- „Znacznik powinien spełniać następujące wymagania: …”
- „Wymiary znacznika przedstawiono na rysunku 4.x.”
- „Kształt dobrano tak, aby…”
- „Otwór znacznika wyznacza obszar zainteresowania, w którym…”
- „Znacznik Π jest symetryczny względem osi pionowej, co oznacza, że…”

### 4.3 Projekt bazy danych (≈ 1 s.)

**Co opisać:** cel bazy, model (diagram ERD jest gotowy: `praca/rysunki/baza_erd.pdf`), tabele i relacje, widoki, decyzja „obrazy w plikach, w bazie ścieżki”.

**Fakty:**

| Tabela | Zawartość | Relacja |
|---|---|---|
| `znamie` | numer znamienia, fold walidacji krzyżowej | 1 : N z `para` |
| `para` | ścieżki zdjęcia, termowizji i mapy °C, oryginalne pliki (HEIC, SEQ), data, rozdzielczości | N : 1 `znamie`; 1 : N `adnotacja`, `analiza` |
| `adnotacja` | maski z CVAT (znamię, znacznik), narożniki, homografia px → mm | N : 1 `para` |
| `analiza` | każde uruchomienie: data, status (`ok`/`blad`), modele, macierz T, folder wyników, commit gita | N : 1 `para`; 1 : N `miara` |
| `miara` | grupa, nazwa, wartość, jednostka (wszystkie liczby z `metryki.json`) | N : 1 `analiza` |

- Widoki: `ostatnia_analiza` (najnowsza udana analiza pary), `wyniki_par` (jej miary z numerem znamienia i foldem).
- Dlaczego tabela `miara` w układzie „długim” (grupa, nazwa, wartość)? Nowe miary nie wymagają zmiany schematu (np. dodanie E2 nie zmieniło tabel).
- Dlaczego obrazy poza bazą? Duże pliki, podgląd w eksploratorze, baza mała i szybka.
- Baza tworzy się sama przy pierwszym zapisie raportu; zapis automatyczny z aplikacji i potoku.

**Zwroty:**
- „Model danych przedstawiono na diagramie związków encji (rys. 4.x).”
- „Baza składa się z pięciu tabel powiązanych relacjami jeden do wielu.”
- „Kluczem głównym tabeli … jest…, a kluczem obcym…”
- „Zastosowano układ…, który pozwala dodawać nowe miary bez zmiany schematu.”
- „Pliki obrazów przechowywane są poza bazą, a baza przechowuje ich ścieżki względne.”
- „Widok … udostępnia…”

### 4.4 Diagram klas (≈ 0,75 s.)

**Co opisać:** główne klasy, ich odpowiedzialności i relacje. Diagram ma być czytelny: 8–12 klas, tylko najważniejsze atrybuty i metody (rysunek – pkt 5).

**Klasy w kodzie (stan 26.10):**
- `Analiza` (`analiza/system.py`) – stan analizy jednej pary.
  - Atrybuty: ścieżki, obrazy, macierz T, maski, narożniki, wyniki.
  - Metody = etapy: `rejestruj`, `ustaw_narozniki`, `segmentuj_znamie`, `segmentuj_znacznik_termal`, `przenies`, `zmierz`, `zapisz_raport`, `zapisz_w_bazie`.
- `Aplikacja` (`aplikacja.py`, dziedziczy po `ctk.CTk`) – okno, 6 zakładek. Zawiera obiekty `Podglad` (podgląd obrazu z powiększaniem) i korzysta z `Analiza`.
- `Baza` (`analiza/baza.py`) – dostęp do SQLite: `utworz`, `importuj_dane`, `zapisz_analize`, `importuj_wyniki`, `info_pary`, `tabela_wynikow`.
- `ModelSegmentacji` (`modele_segmentacja/interfejs.py`) – klasa bazowa (interfejs) modeli segmentacji: `wczytaj`, `segmentuj`, `_prawdopodobienstwo`; wynik → `WynikSegmentacji`.
  - Podklasy: `Model` w `modele/panderm_upernet` (PanDerm + UperNet, M1) i `Model` w `modele/progowanie` (model odniesienia).
- `SegmentacjaZnacznikaTermal` (`unet_termal/wnioskowanie.py`) – wnioskowanie U-Net (ONNX): `segmentuj`.
- `UNet` (`unet_termal/architektura.py`, `nn.Module`) – architektura M3, złożona z obiektów `Blok`.
- `Znacznik` (`modele_segmentacja/znacznik.py`) – wykryty znacznik i jego wnętrze.
- `BladEtapu` (wyjątek) – komunikaty dla użytkownika.
- Moduły funkcyjne jako klasy ze stereotypem «utility»: `dopasowanie3` (rejestracja), `geometria`, `miary`, `pomiary`, `raport`.

**Relacje do pokazania:**
- `Aplikacja` → `Analiza` (asocjacja);
- `Analiza` → `Baza` (zależność);
- `Analiza` → `SegmentacjaZnacznikaTermal` (zależność);
- `Analiza` → `dopasowanie3` (zależność);
- `Model` (PanDerm) → `ModelSegmentacji` (dziedziczenie);
- `UNet` ◆ `Blok` (kompozycja).

**Zwroty:**
- „Strukturę statyczną systemu przedstawiono na diagramie klas (rys. 4.x).”
- „Centralną klasą systemu jest…, która…”
- „Klasa … pełni rolę interfejsu dla…, co umożliwia dodanie kolejnych modeli bez zmiany…”
- „Moduły … zrealizowano jako zbiory funkcji, oznaczone na diagramie stereotypem «utility».”
- „Dla czytelności pominięto metody pomocnicze.”

### 4.5 Projekt interfejsu użytkownika (≈ 0,75 s.)

**Co opisać:** układ okna, przepływ pracy, główne elementy, decyzje projektowe. Rysunek: zrzut ekranu jednej zakładki z opisanymi obszarami (pkt 5). Szczegółowa obsługa należy do instrukcji (Dodatek A), nie tutaj.

**Fakty (z `aplikacja.py`):**
- **Okno** 1360 × 940 px (min. 1100 × 760). Od góry:
  - pasek tytułu z numerem pary;
  - pasek 6 etapów (przyciski = zakładki): 1. Dane · 2. Rejestracja · 3. Segmentacja · 4. Przeniesienie ROI · 5. Pomiary · 6. Raport;
  - obszar zakładki;
  - na dole: status, pasek postępu i log.
- **Układ zakładki:** lewa kolumna z przyciskami i opisem (ok. 330 px), prawa – podglądy obrazów.
- **Podglądy:** kółko myszy = powiększenie, przeciąganie = przesuwanie, dwuklik = widok początkowy. Termowizja z widocznymi pikselami.
- **Prowadzenie użytkownika:**
  - przycisk „Dalej: …” na końcu każdej zakładki;
  - przyciski etapów, których nie da się jeszcze wykonać, są nieaktywne;
  - komunikaty błędów w oknach dialogowych;
  - przycisk „Wykonaj wszystkie etapy”.
- **Dwa tryby wejścia:** „Para z bazy” (numer, strzałki ◀ ▶) i „Własne pliki”.
- Rejestracja: suwak przezroczystości nałożenia, zapis nałożenia.
- Pomiary: tabela wyników, kliknięcie nazwy miary → objaśnienie.
- Raport: podgląd obrazów raportu (m.in. „E2”), otwarcie raportu HTML i folderu.
- **Kolory:** turkusowe kontury masek z U-Netu (grubsze linie). Zmieniono z żółtego ze względu na czytelność na palecie inferno.
- **Obliczenia w tle:** wątek roboczy + kolejka komunikatów; okno pozostaje responsywne (WN – wydajność).

**Decyzje projektowe do uzasadnienia:**
- zakładki = etapy potoku (model mentalny = architektura);
- liniowy przepływ z możliwością powrotu;
- podgląd każdego wyniku pośredniego (kontrola jakości przez użytkownika);
- automatyzacja z możliwością wglądu.

**Zwroty:**
- „Interfejs zaprojektowano tak, aby odzwierciedlał kolejność etapów przetwarzania.”
- „Okno aplikacji składa się z … obszarów (rys. 4.x): …”
- „Elementy sterujące umieszczono w lewej kolumnie, a podglądy wyników w prawej.”
- „Przyciski etapów, które nie mogą zostać jeszcze wykonane, są nieaktywne, co zapobiega…”
- „Obliczenia wykonywane są w osobnym wątku, dzięki czemu interfejs pozostaje responsywny.”
- „Szczegółowy opis obsługi zawiera instrukcja użytkownika (Dodatek A).”

**Typowe błędy w rozdz. 4:** opis kodu zamiast decyzji; brak uzasadnień („wybrano Pythona” bez „ponieważ”); diagram klas wygenerowany automatycznie ze wszystkimi metodami (nieczytelny); zrzut ekranu bez opisu elementów; powtarzanie wymagań z rozdz. 3.

---

## 5. Uniwersalne zwroty pomocnicze

**Wprowadzenie rozdziału / podrozdziału:**
- „W niniejszym rozdziale przedstawiono…”
- „Rozdział rozpoczyna się od…, a następnie omówiono…”
- „Celem tego podrozdziału jest…”

**Uzasadnienie:**
- „Wynika to z faktu, że…”
- „Rozwiązanie to przyjęto ze względu na…”
- „Takie podejście pozwala…, a jednocześnie…”
- „Zaletą … jest…, natomiast wadą…”

**Porównanie i kontrast:**
- „W odróżnieniu od…, w niniejszej pracy…”
- „Podobnie jak w pracy [x], …”
- „W przeciwieństwie do…”

**Odwołania:**
- „…co opisano w podrozdziale 2.2.”
- „Szczegóły implementacji przedstawiono w rozdziale 5.”
- „Zgodnie z wymaganiem WF6…”

**Podsumowanie fragmentu:**
- „Podsumowując, …”
- „Przyjęte rozwiązania zapewniają spełnienie wymagań…”
- „W kolejnym rozdziale opisano…”

**Unikaj:**
- słów potocznych („fajnie”, „super”, „ogarnąć”);
- anglicyzmów, gdy jest polskie słowo (pipeline → potok przetwarzania; feature → cecha; overlay → nałożenie, przy pierwszym użyciu z ang.);
- „ciekawych” przymiotników bez treści („innowacyjny”, „zaawansowany”);
- zdań w 1. osobie.
