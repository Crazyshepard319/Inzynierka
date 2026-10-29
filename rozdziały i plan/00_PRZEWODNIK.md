# Przewodnik końcowy – praca inżynierska (stan 29.10.2026)

Jeden plik, od którego warto zaczynać. Zbiera: co gdzie leży, w jakiej kolejności pisać, listę rzeczy do zrobienia przed oddaniem, pytania do promotorki, sugestie poprawek (tekst i system), ściągę poleceń i wskazówki do LaTeX-a. Pytania na obronę: `materialy/08_pytania_na_obrone.md`.

---

## 0. Zrób przed 31.10 (pilne, ok. 30 min)

1. **Zapisz zmiany w gicie.** Od 26.10 w `projekt/` i `praca/` jest dużo zmian (U-Net M3, baza SQLite, badanie E2, piksele z .SEQ, testy, wzór pracy, rysunki). W `cmd`:
   ```bat
   cd /d "C:\Users\groch\OneDrive\Pulpit\Inzynierka"
   git status
   git add projekt praca\wzor praca\materialy praca\rysunki praca\plan_pracy.md praca\00_PRZEWODNIK.md praca\notatki_claude
   git commit -m "U-Net M3, baza SQLite, E2, piksele z .SEQ, testy; wzor rozdzialow 1-7 i dodatkow"
   ```
   `dane/`, `wyniki/` i `praca/literatura/` są poza gitem (`.gitignore`), ale leżą na OneDrive.
2. **Kopia zapasowa poza OneDrive.** Folder `C:\Users\groch\modele_dane\` nie jest na OneDrive. Najważniejsze są wagi: `modele_dane\wagi\` (U-Net `unet_termal\fold1..5.onnx` i `wszystkie.onnx`, wytrenowany PanDerm). Bez nich system nie zrobi segmentacji, a ponowny trening PanDerm trwa wiele godzin. Skopiuj `wagi\` na dysk zewnętrzny lub do chmury. Środowisko Pythona odtworzysz z `projekt\modele_segmentacja\wymagania_srodowiska.txt`.
3. **Sprawdź aplikację na Windowsie.** 28.10 zmieniłem `aplikacja.py` (podgląd „Piksele”, informacja o nagraniu .SEQ). Uruchom ją, wczytaj parę 14, kliknij „Wykonaj wszystkie etapy” i zajrzyj do zakładek 5 i 6. Przy okazji zrób zrzuty ekranu (lista w punkcie 3).
4. **Uruchom testy:** `projekt\testy\uruchom_testy.bat`. U Ciebie powinno przejść wszystkie 18 testów; u mnie T09 był pominięty, bo w mojej maszynie nie było wag U-Netu.
5. **Posprzątaj `Claude outputs\`.** Folder `test_piksele\` to moje pliki testowe – można go usunąć. Folder `dane_rozdz6\` zastępuje teraz `praca\rysunki\dane_wynikow\`, więc też jest zbędny.

---

## 1. Co gdzie leży

| Co | Gdzie |
|---|---|
| Ten przewodnik | `praca\00_PRZEWODNIK.md` |
| Plan pracy, decyzje, przydział literatury | `praca\plan_pracy.md` |
| Materiały i zwroty do rozdz. 1, 3, 4 | `praca\materialy\01_materialy_rozdzialy_1_3_4.md` |
| Zwroty do rozdz. 2 (stan wiedzy) | `praca\materialy\02_zwroty_analiza_stanu_wiedzy.md` |
| Karty 23 artykułów (co cytować, liczby ze stronami) | `praca\materialy\03_streszczenia_artykulow.md` |
| Rysunki, tabele, dane z artykułów (rozdz. 2) + wycinki | `praca\materialy\04_…md`, `materialy\rysunki_z_artykulow\` |
| Rysunki do rozdz. 1, 3, 4 | `praca\materialy\05_…md` |
| Plan i zwroty do rozdz. 4–7 | `praca\materialy\06_plan_zwroty_rozdzialy_4_7.md` |
| Plan dodatków, streszczeń, wykazu skrótów, lista zrzutów | `praca\materialy\07_plan_dodatki_streszczenie_skroty.md` |
| Pytania na obronę z odpowiedziami | `praca\materialy\08_pytania_na_obrone.md` |
| **Wzór całej pracy (LaTeX)** + podgląd PDF | `praca\wzor\` (`README.md` – opis plików, liczba stron, lista cięć) |
| Bibliografia z Twoimi kluczami (acm.bst) | `praca\wzor\literatura_wzor.bib` |
| Rysunki i wykresy (PDF do LaTeX-a, PNG podgląd) | `praca\rysunki\` |
| Skrypty liczb i wykresów | `praca\rysunki\liczby_wynikow.py`, `wykresy_wyniki.py` |
| Notatki z pracy z Claude (archiwum) | `praca\notatki_claude\` |
| Kod systemu + opis uruchomienia | `projekt\` (`README.md`), `projekt\modele_segmentacja\README.md` |
| Testy | `projekt\testy\` |
| Wyniki par, raport zbiorczy, baza | `wyniki\wyniki_obu\`, `wyniki\raport_zbiorczy\`, `dane\baza.sqlite` |

---

## 2. Jak pisać – kolejność i metoda

**Kolejność:** 3 → 4 → 5 → 6 → 2 → 7 → 1 → Streszczenie i Abstract → wykaz skrótów (na samym końcu). Rozdziały „techniczne” najłatwiej napisać, bo opisujesz to, co sam zrobiłeś. Wstęp i streszczenie pisze się na końcu, gdy wiadomo, co w pracy jest.

**Metoda dla każdego rozdziału:**
1. Przeczytaj plan rozdziału (`01_…` albo `06_…`) – co ma się znaleźć i jakie liczby.
2. Przeczytaj wzór (`wzor\rozdzialN_…tex`), **zamknij go** i napisz tekst własnymi słowami.
3. Porównaj z planem: czy są wszystkie elementy, rysunki zapowiedziane w tekście, liczby z `liczby_wynikow.py`.
4. Sprawdź listę „Unikaj” na końcu sekcji w `06_…` (najczęstsze błędy).

**Antyplagiat i narzędzia AI:**
- Praca przechodzi przez system antyplagiatowy (JSA). Wzór napisałem na podstawie Twoich materiałów, ale tekstu nie wklejaj – przepisz go. Tak samo z fragmentami artykułów: parafraza + cytowanie.
- Sprawdź aktualne zasady PG dotyczące korzystania z narzędzi AI przy pracy dyplomowej (regulamin, oświadczenie autora) i zapytaj promotorkę, czy i jak to zadeklarować.

**Limit stron:** wzór ma ok. 45 stron rozdz. 1–7 z dodatkami (podgląd w klasie `report`), limit to 30–40. Lista cięć z oszczędnością: `wzor\README.md`. Najwięcej dają rozdz. 3 i 4 oraz dodatki.

---

## 3. Lista rzeczy do zrobienia przed oddaniem

| # | Co | Gdzie |
|---|---|---|
| 1 | Porównaj cel pracy z kartą tematu (Moja PG) | rozdz. 1.2 |
| 2 | Potwierdź grupę użytkowników | rozdz. 3.1 |
| 3 | Uzasadnij próg 1 mm dla TRE (np. ≈ 3–4 piksele termowizji, < 1/2 średnicy typowego znamienia 2,1 mm) | rozdz. 3.3 (WN4) |
| 4 | Zrzut ekranu zakładki „2. Rejestracja” (para 14) → `rysunki\interfejs_rejestracja.png` | rys. 4.4 |
| 5 | (opcja) zrzut zakładki „5. Pomiary” z sekcją pikseli → `rysunki\interfejs_pomiary.png` | Dodatek A |
| 6 | Wynik testów z `testy\wynik_testow.txt` (zmień T09 „pominięty” na wynik) | tab. 6.4 |
| 7 | Testy ręczne GUI TG1–TG6 i zdanie z wynikiem | rozdz. 6.6 |
| 8 | Procesor i pamięć komputera, na którym mierzono czasy (E4) | rozdz. 6.2 |
| 9 | Dziedzina OECD w brzmieniu z szablonu PG | Streszczenie, Abstract |
| 10 | Usuń wszystkie komentarze `% TODO` i `% OPCJA` po decyzji | wszystkie `.tex` |
| 11 | Wykaz skrótów: usuń skróty, które wypadły przy skracaniu | `wykaz_skrotow.tex` |
| 12 | Spis treści, rysunków i tabel – sprawdź, czy numeracja i podpisy się zgadzają | PDF |

---

## 4. Pytania do promotorki (na najbliższe spotkanie)

1. Grupa użytkowników systemu (studenci i lekarze UCK – jak w starej wersji?).
2. Czy do limitu 30–40 stron wliczają się spis treści, wykaz skrótów i bibliografia (dodatki – tak, ustalone 26.10)?
3. Czy w rozdz. 6 wystarczy tabela testów automatycznych + jedno zdanie o testach ręcznych GUI?
4. Czy można wstawiać rysunki z artykułów niebędących w otwartym dostępie (Zitová 2003 – Elsevier, Ronneberger 2015 – Springer), czy je przerysować?
5. Czy styl bibliografii `acm` (bez DOI i URL) jest akceptowany?
6. Czy wymagane jest oświadczenie o użyciu narzędzi AI i w jakiej formie?
7. Czy piksele z intensywnością z .SEQ (CSV, baza) wystarczą, czy dodać statystyki skóry wokół znamienia dla porównania?

---

## 5. Sugestie poprawek – tekst (od najważniejszych)

1. **Limit stron** – patrz `wzor\README.md` (lista cięć). Decyzję podejmij po wstawieniu do szablonu PG, bo tam liczba stron będzie inna.
2. **Prawa do rysunków z artykułów (rozdz. 2):** Oniga 2026 (Frontiers) i Taha 2015 (BMC) są na licencji CC BY – można wstawić z podaniem źródła. Zitová 2003 i Ronneberger 2015 nie są w otwartym dostępie – bezpieczniej przerysować schemat samodzielnie i podpisać „Opracowanie własne na podstawie [x]”.
3. **Stara wersja pracy (PDF z promotorką) opisuje stary system** – nie łącz jej fragmentów z nowym tekstem. Znane błędy starej wersji: „Azam i współautorzy [8]” (pod [8] jest Han), rozdzielczość 640 × 480 (teraz 320 × 240, FLIR A320), „znacznik o dowolnym kształcie”, cytowania Karami/Gaens/Zhu (usunięte).
4. **Jedno źródło liczb:** każdą liczbę z rozdz. 5–7 i streszczeń bierz z wydruku `liczby_wynikow.py` (wypisuje je z numerem podrozdziału). Po zmianie kodu lub ponownym przeliczeniu wyników uruchom go ponownie i porównaj.
5. **Spójne nazwy:** znacznik Π · macierz T · homografia H · model M1 / M3 · badania E1, E2, E4 · „obraz termowizyjny” (nie zamiennie „termogram”, „IR”, „termal”) · „znamię” (nie „pieprzyk”, „zmiana” tylko ogólnie).
6. **Odsyłacze:** każdy rysunek i tabela muszą być zapowiedziane w tekście przed miejscem wystąpienia; każdy podpis kończy się źródłem („Źródło: opracowanie własne” / „Źródło: [x]”).
7. **Skróty:** rozwinięcie przy pierwszym użyciu w tekście (także gdy jest w wykazie).
8. **Zapis:** przecinek dziesiętny, spacja przed jednostką (17 mm), znak × w wymiarach, „°C” bez spacji między ° i C; w Abstract kropka dziesiętna.
9. **Bibliografia:** `acm.bst` nie drukuje DOI ani URL. Jeśli wydział wymaga DOI, najprościej dopisać je w polu `note` każdego wpisu (np. `note = {DOI: 10.1109/TPAMI.2008.113}`); zmianę stylu uzgodnij z promotorką.

---

## 6. Sugestie poprawek – system (gdy będzie czas; każda zmienia wyniki!)

| Pomysł | Uzasadnienie z danych | Gdzie w kodzie | Wysiłek |
|---|---|---|---|
| Silniejsze ostrzeżenia: Dice folii w E2 < 0,93 (zamiast 0,85) **lub** zgodność znacznika na zdjęciu < 0,65 | Reguła wskazuje 7 par, z których 6 ma TRE > 1 mm, w tym wszystkie trzy z TRE > 1,9 mm (78, 8, 79). Dziś próg 0,85 łapie tylko parę 78. | `analiza/raport.py`, funkcja `uwagi` | 10 min (+ zmiana opisu w 5.6 i tab. A.3) |
| Przerwanie rejestracji, gdy znacznik na termowizji jest niepewny (< 0,65) | Test T05: obraz bez znacznika daje tylko ostrzeżenie (zgodność 0,54) | `analiza/system.py`, `rejestruj` | 15 min (+ test T05) |
| Sekcja pikseli w raporcie zbiorczym | Raport zbiorczy był liczony 26.10, przed dodaniem pikseli | `raport_zbiorczy.py` | 30 min |
| Douczenie M1 na własnych zdjęciach (walidacja krzyżowa po znamionach) | M1 zawyża pole (mediana stosunku pól 1,10) | `modele_segmentacja/modele/panderm_upernet/trening.py` | 1–2 dni (GPU) |
| Termografia dynamiczna (sekwencja po schłodzeniu) | σ intensywności w znamieniu ≈ 0,07 °C – znamię bez schłodzenia nie wyróżnia się | nowa funkcja na wszystkich klatkach .SEQ | duży – raczej „dalsze prace” |

Po każdej zmianie kodu: `potok_pary.bat 1-94 --z_zapisanych` → `raport_zbiorczy.bat` → `liczby_wynikow.py` → `wykresy_wyniki.py` → popraw liczby w tekście → `uruchom_testy.bat`.

---

## 7. Ściąga poleceń (z folderu `Inzynierka`)

| Co | Polecenie |
|---|---|
| Aplikacja | `inzynierka\Scripts\python.exe projekt\aplikacja.py` |
| Analiza wszystkich par (z zapisaną rejestracją i maskami, bez GPU) | `projekt\potok_pary.bat 1-94 --z_zapisanych` |
| Analiza od zera (z PanDerm, GPU) | `projekt\potok_pary.bat 1-94` |
| Raport zbiorczy + tabele LaTeX | `projekt\raport_zbiorczy.bat` |
| Badanie E4 | `"%USERPROFILE%\modele_dane\srodowisko\Scripts\python.exe" projekt\porownaj_rejestracje.py 1-94` |
| Ocena U-Netu względem CVAT | `projekt\modele_segmentacja\ocen_unet_termal.bat` |
| Baza: podsumowanie / eksport / piksele | `projekt\baza_danych.bat pokaz` · `eksport` · `eksport_piksele` |
| Surowe wartości z .SEQ dla par | `python projekt\temperatury_par.py --tylko_surowe` |
| Testy | `projekt\testy\uruchom_testy.bat` |
| Liczby do tekstu | `inzynierka\Scripts\python.exe praca\rysunki\liczby_wynikow.py` |
| Wykresy rozdz. 6 | `inzynierka\Scripts\python.exe praca\rysunki\wykresy_wyniki.py` |
| Podgląd wzoru (LaTeX) | w `praca\wzor`: `pdflatex wzor_podglad` → `bibtex wzor_podglad` → `pdflatex` ×2 |

---

## 8. LaTeX – wskazówki do szablonu PG

- Wstawiaj pliki przez `\input{wzor/rozdzial5_implementacja}` (ścieżki rysunków zakładają główny plik w `praca\`).
- Pakiety: `graphicx`, `booktabs`, `tabularx`, `longtable`, `makecell`, `amsmath`, `algorithm` (opcja `chapter`), `algpseudocode` (opcja `noend`), `listings`. Polskie nazwy algorytmów i listingów skopiuj z preambuły `wzor\wzor_podglad.tex`.
- Bibliografia: `\bibliographystyle{acm}` + `\bibliography{wzor/literatura_wzor}`; kolejność kompilacji: pdflatex → bibtex → pdflatex ×2.
- Rysunki: PDF (wektor) dla diagramów i wykresów, PNG dla zdjęć; `[htbp]`; gdy rysunek „ucieka” daleko, skróć tekst przed nim albo zmniejsz `width`.
- Przekroczenia marginesów w moim podglądzie wynikają z braku polskiego dzielenia wyrazów w mojej instalacji – w szablonie PG z `babel`/`polski` znikną.
- Jeśli piszesz w Overleaf: wgraj foldery `wzor\`, `rysunki\`, `materialy\rysunki_z_artykulow\` z zachowaniem struktury.

---

## 9. Obrona

`materialy/08_pytania_na_obrone.md` – 28 pytań, które mogą paść (metoda, wyniki, ograniczenia, decyzje projektowe), z krótkimi odpowiedziami opartymi na Twoich wynikach. Przećwicz na głos 1–2 min na pytanie. Przygotuj też 3 slajdy „na wszelki wypadek”: wykres E4, wykres E2–TRE, rysunek pikseli pary 14.
