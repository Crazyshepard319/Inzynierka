# Wzór pracy: rozdziały 1–7, dodatki A i B, streszczenia, wykaz skrótów

To jest **wzór do inspiracji, nie gotowa praca**. Napisany bezosobowo, na podstawie Twoich materiałów (`praca/materialy/01`–`07`), kart artykułów i wyników systemu z 28.10.2026. Przed użyciem przeczytaj i przepisz własnymi słowami.

| Plik | Zawartość |
|---|---|
| `streszczenie_abstract.tex` | Streszczenie (PL) i Abstract (EN) ze słowami kluczowymi i dziedziną OECD |
| `wykaz_skrotow.tex` | Wykaz ważniejszych oznaczeń i skrótów z całej pracy (alfabetycznie, PL + EN) |
| `rozdzial1_wstep.tex` | 1.1 Motywacja, 1.2 Cel i zakres, 1.3 Struktura (rys. pary 14) |
| `rozdzial2_analiza_stanu_wiedzy.tex` | 2.1–2.5. 4 rysunki z artykułów i 2 tabele; rysunki Hermana i Hana zakomentowane (OPCJA) |
| `rozdzial3_analiza_projektowa.tex` | 3.1–3.5: WF1–WF15 (WF15 – piksele, 28.10), WN1–WN10, scenariusz PU2, diagram przypadków użycia, potok, architektura |
| `rozdzial4_projekt_systemu.tex` | 4.1–4.5: technologie, znacznik Π, ERD (6 tabel) + tabele bazy, diagram klas, miejsce na zrzut ekranu |
| `rozdzial5_implementacja.tex` | 5.1–5.6: dane, rejestracja (algorytm 5.1, rys. pary 14), modele M1 i M3 (tab. parametrów, krzywe uczenia), przeniesienie ROI i piksele (algorytm 5.2), pomiary (wzór TRE), baza/raport/aplikacja |
| `rozdzial6_testy_wyniki.tex` | 6.1–6.7: protokół, E1 + E4 (tab., wykres), segmentacja (tab., wykres), E2 (wykres E2–TRE, rys. pary 14), znamiona i piksele (tab., rys.), testy T01–T18 (tab.), dyskusja |
| `rozdzial7_podsumowanie.tex` | 7.1 Realizacja celu, 7.2 Wnioski, 7.3 Dalsze prace |
| `dodatek_a_instrukcja.tex` | Instrukcja użytkownika: uruchomienie, przygotowanie obrazów, kroki w aplikacji, pliki wynikowe, komunikaty |
| `dodatek_b_dokumentacja.tex` | Dokumentacja techniczna: środowiska, struktura kodu, API (listing), formaty danych, baza (SQL), skrypty, rozszerzanie |
| `literatura_wzor.bib` | 23 pozycje z Twoimi kluczami, poprawione pod `acm.bst` |
| `wzor_podglad.tex` / `.pdf` | Podgląd całości poza szablonem PG (klasa `report`, 12 pt) |

Plany i zwroty: `materialy/06_plan_zwroty_rozdzialy_4_7.md` (rozdz. 4–7), `materialy/07_plan_dodatki_streszczenie_skroty.md` (dodatki, streszczenia, wykaz skrótów, lista zrzutów ekranu).

## Jak wstawić do pracy

- Pliki zakładają, że główny plik `.tex` leży w folderze `praca/`. Rysunki są w `rysunki/` i `materialy/rysunki_z_artykulow/`.
- Rozdział wstawiasz poleceniem `\input{wzor/rozdzial5_implementacja}`; dodatki po `\appendix`.
- Bibliografia: `\bibliographystyle{acm}` i `\bibliography{wzor/literatura_wzor}` albo wpisy skopiowane do Twojego `.bib`.
- Potrzebne pakiety: `graphicx`, `booktabs`, `tabularx`, `longtable`, `makecell`, `amsmath`, `algorithm` (opcja `chapter`), `algpseudocode` (opcja `noend`), `listings`. Polskie nazwy algorytmów i listingów skopiuj z preambuły `wzor_podglad.tex`.

## Do zrobienia przed użyciem (komentarze `% TODO` w plikach)

1. Sprawdź brzmienie celu z kartą tematu (1.2).
2. Potwierdź z promotorką grupę użytkowników (3.1).
3. Uzasadnij próg 1 mm dla TRE (WN4).
4. Zrób zrzuty ekranu aplikacji (lista w `materialy/07_…`): rys. 4.4 i opcjonalnie Dodatek A.
5. Uruchom `projekt\testy\uruchom_testy.bat` i wpisz wynik do tab. 6.4 (w maszynie wirtualnej: 17 zaliczonych, T09 pominięty – brak wag U-Netu).
6. Wykonaj ręczne testy interfejsu TG1–TG6 i wpisz wynik (6.6).
7. Wpisz procesor i pamięć komputera, na którym mierzono czasy rejestracji (6.2).
8. Sprawdź brzmienie dziedziny OECD w szablonie PG (Streszczenie, Abstract).

## Liczba stron (podgląd: klasa `report`, 12 pt, marginesy 2,5 cm)

| Część | Strony | Budżet |
|---|---|---|
| rozdz. 1 | 3 | 2 |
| rozdz. 2 | 8 | 8 |
| rozdz. 3 | 6 | 4 |
| rozdz. 4 | 6 | 4,5 |
| rozdz. 5 | 7 | 6 |
| rozdz. 6 | 7 | 6,5 |
| rozdz. 7 | 2 | 1,5 |
| Dodatek A | 3 | 2 |
| Dodatek B | 3 | 2 |
| **razem z dodatkami** (bez stron tytułowych, spisów i bibliografii) | **45** | 36,5 |

W szablonie PG liczba stron będzie inna (czcionka, interlinia, rozmieszczenie rysunków). Gdy przekroczysz 40 stron, skracaj w tej kolejności (oszczędność w przybliżeniu):
- rozdz. 3: usuń tabelę scenariusza PU2 (0,5 s.) i rysunek potoku (0,5 s.) – potok opisuje algorytm 5.1;
- rozdz. 4: usuń tabelę tabel bazy – ERD ją zastępuje (0,5 s.); skróć opis interfejsu – szczegóły są w Dodatku A (0,3 s.);
- rozdz. 5: usuń rysunek krzywych uczenia M1 (0,4 s., oznaczony `OPCJA`); skróć tabelę parametrów uczenia do 6 wierszy (0,2 s.);
- rozdz. 6: usuń wykres segmentacji (0,4 s., `OPCJA`) – liczby są w tabeli 6.2;
- Dodatek A: zostaw tylko tabele A.1 i A.3, pliki wynikowe opisz jednym akapitem (0,7 s.);
- Dodatek B: usuń listing SQL i tabelę skryptów – odeślij do `README.md` w projekcie (0,8 s.).

## Uwagi

- W podglądzie PDF są przekroczenia marginesów, bo moja instalacja LaTeX-a nie ma polskich wzorców dzielenia wyrazów. W Twoim szablonie (z `babel`/`polski`) problem zniknie.
- Liczby w rozdz. 5–7 i w streszczeniach pochodzą z wyników z 28.10 (`wyniki/wyniki_obu/para_N/metryki.json`, n = 92), badania E4 (`porownanie_rejestracji.csv`) i oceny U-Netu (n = 94). Zestawienie danych: `Claude outputs/dane_rozdz6/`; wykresy odtwarza `rysunki/wykresy_wyniki.py`.
- Nazwa GrabCut celowo nie występuje (decyzja 26.10) – w tekście jest „segmentacja interaktywna z biblioteki OpenCV”.
- `codella2019` zweryfikowano na pliku `nowe_artykuły/codella2018.pdf` (ISIC 2018).
- Informacja wzajemna cytowana przez `zitova2003`/`correlation-ratio` (Mattes tylko jako metryka SimpleITK); bez Blanda–Altmana.
