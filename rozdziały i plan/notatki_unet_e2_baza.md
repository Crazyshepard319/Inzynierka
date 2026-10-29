# U-Net dla termowizji (M3), badanie E2 i baza SQLite – stan 26.10.2026

## Co dodano do kodu (folder Inzynierka/projekt, niezacommitowane w gicie)
- `modele_segmentacja/unet_termal/` – model M3: U-Net (4 poziomy, 16–256 kanałów, 1,94 mln parametrów) segmentujący folię znacznika Π na termowizji 320 × 240. Wejście: skala szarości (jak `dopasowanie3.wczytaj_termal`) standaryzowana per obraz. Trening: BCE + (1 − miękki Dice), AdamW 2e-3, wd 1e-4, cosinus, paczka 8, 60 epok (bez wyboru epoki na teście), augmentacja (obrót 0–360°, skala 0,75–1,3, przesunięcie, odbicia, gamma, kontrast, rozmycie, szum). Eksport ONNX → wnioskowanie przez `cv2.dnn` (aplikacja bez PyTorch).
- Walidacja krzyżowa 5-krotna po znamionach (`dane/znamiona.csv`); system używa modelu foldu, w którym para była testowa; obrazy spoza bazy → `wszystkie.onnx`.
- Wagi: `C:\Users\groch\modele_dane\wagi\unet_termal\fold1..5.onnx`, `wszystkie.onnx` (+ .pth). Logi: `wyniki/wyniki_segmentacji/unet_termal/trening_20261026_152813/`. Ocena: `.../ocena_20261026_152810/` (CSV, podsumowanie, `tabela.tex`).
- `.bat`: `trenuj_unet_termal.bat` (sam doinstalowuje `onnx`), `ocen_unet_termal.bat`, `baza_danych.bat`; `potok_pary.bat 1-94 --z_zapisanych` (bez GPU: zapisana rejestracja + maska PanDerm).
- Badanie E2 w `analiza/system.py` (`zgodnosc_modalnosci`): folia ze zdjęcia (detektor z rejestracji) przeniesiona przez T vs folia z U-Netu; otwór (ROI) = otoczka wypukła − folia, ta sama funkcja dla obu (`geometria.wnetrze_znacznika`), siatka 4×. Raport pary: sekcja E2 + obraz `znacznik_modalnosci.png`; aplikacja: krok 3 (U-Net), 5 (tabela), 6 (podgląd „E2”); raport zbiorczy: grupy `e2` i `unet` + tabele LaTeX `tab:e2`, `tab:unet`.
- Baza SQLite `dane/baza.sqlite` (`analiza/baza.py`): tabele znamie, para, adnotacja, analiza, miara; widoki ostatnia_analiza, wyniki_par. Zapis automatyczny przy każdym raporcie (aplikacja, potok). `dane.info_pary` czyta z bazy (fallback CSV). Diagram ERD: `praca/rysunki/baza_erd.{mmd,png,pdf}`.
- Uwaga: SQLite nie działa na folderze zamontowanym w maszynie wirtualnej Claude (disk I/O error) – na Windowsie działa normalnie. W `dane/` jest pusty plik `baza.sqlite-journal` (0 B) – nieszkodliwy.

## Wyniki (do rozdziału 6)
- U-Net vs CVAT (94 pary, walidacja krzyżowa): Dice 0,969 ± 0,008 (mediana 0,970, min 0,937), IoU 0,939, HD95 0,68 ± 0,27 mm (mediana 0,62), ASSD 0,23 mm, stosunek pól 1,004. Foldy: 0,970/0,968/0,968/0,968/0,970.
- Detektor klasyczny (z rejestracji) vs CVAT: Dice 0,954 ± 0,017, HD95 1,06 ± 0,59 mm, stosunek pól 0,950 (zaniża brzeg folii).
- E2 (92 pary, bez CVAT): Dice folii 0,957 ± 0,032 (mediana 0,966), Dice otworu 0,949 ± 0,045 (mediana 0,960), HD95 otworu mediana 0,88 mm, przesunięcie środków otworu mediana 0,23 mm; Dice folii ≥ 0,9 na 89/92.
- E2 wykrywa złą rejestrację bez adnotacji: najniższe E2 = pary z największym TRE (78: Dice 0,72 / TRE 24,7 mm; 8: 0,86 / 2,3 mm; 79: 0,89 / 1,9 mm); korelacja rang E2–TRE ok. −0,72.
- Para 1: E2 otworu 0,81 – maska folii ze zdjęcia (GrabCut) wchodzi w otwór; E2 ujawnia błędy segmentacji w jednej z modalności.
- Pary 75, 76: znacznik na zdjęciu niepewny (zgodność z Π 0,54 / 0,58) – odrzucone.
- Raporty par i raport zbiorczy przeliczone 26.10 (`--z_zapisanych`, ta sama rejestracja i maski PanDerm co 25.10).

## Do zrobienia przez Mateusza
- Sprawdzić aplikację na Windowsie (GUI nie było testowane – tylko etapy w Pythonie).
- Zacommitować zmiany w gicie (projekt/ + praca/rysunki/baza_erd.*).
