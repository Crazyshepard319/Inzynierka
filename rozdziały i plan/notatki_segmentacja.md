# Segmentacja znamienia (RGB): PanDerm, dane, obszar ze znacznika Π

Stan na 25.10.2026.

## Na czym jest wytrenowany model
- **Backbone PanDerm** (ViT-L/16, `panderm_ll_data6_checkpoint-499.pth`): uczenie samonadzorowane (masked latent modeling z dopasowaniem do cech nauczyciela CLIP-L, 500 epok, maska 50%) na 2 149 706 obrazach z 11 źródeł:
  - TBP 35,3%
  - dermatopatologia 25,4%
  - zdjęcia kliniczne 21,4%
  - dermoskopia 17,9%

  Źródło: Yan i in., arXiv 2410.15038 / Nature Medicine 2025. Licencja CC-BY-NC-ND 4.0.
- **Głowica UperNet i douczony backbone**: własny trening na ISIC 2018 Task 1 (2594 obrazy dermoskopowe, 224×224, znamię ok. 53% dłuższego boku kadru).
  - Test (1000 obrazów): Dice 0,899, Jaccard 0,833.
  - Najlepsza epoka na walidacji: 11.
- **Wniosek**: reprezentacje widziały zdjęcia kliniczne, ale wiedza o granicy znamienia pochodzi tylko z dermoskopii. Na zdjęciach z telefonu maska wychodzi za duża (przesunięcie domeny).
- W pracy PanDerm z 5% ISIC 2018 (104 obrazy) dorównał najlepszemu konkurentowi uczonemu na całym zbiorze, więc ~100 własnych zdjęć to sensowna skala douczania.

## Publiczne zbiory: dlaczego własne zdjęcia
- **PAD-UFES-20** (2298 zdjęć smartfonem), SCIN, Fitzpatrick17k, DDI: bez masek segmentacji.
- **Kliniczne z maskami**:
  - Dermofit: 1300 zdjęć, lustrzanka, płatna licencja.
  - DermIS+DermQuest: 206 zdjęć, Mendeley bfmpbx432k.
- **iToBoS 2024**: TBP, ok. 60 tys. zmian, CC-BY, ale tylko bounding boxy.
- We wszystkich znamię jest zwykle duże i wyśrodkowane. Własna domena (telefon, taśma Π, małe znamiona) jest wąska, więc własne dane mają pierwszeństwo, a publiczne mogą być najwyżej dodatkiem.

## Decyzje
- Obszar = wnętrze znacznika Π (otwór 17 × 17 mm, `modele_segmentacja/znacznik.py`, w aplikacji z maski folii z rejestracji). Folia poza obszarem jest zastępowana medianą koloru skóry, a maska jest ograniczona do obszaru.
- Model nie dostaje całego wnętrza, tylko kadry wokół kandydatów na znamię (`propozycje.py`, od 25.10) – patrz niżej.
- **Zbiór**: ok. 100 zdjęć, 35–50 różnych znamion po 2–3 zdjęcia. Zdjęcia jednego znamienia różnią się obrotem znacznika, odległością i kątem. Folder na znamię (`znamie_01/`…).
- **CVAT**: tylko etykieta znamienia.
- **Podział i ocena**: 5-krotna walidacja krzyżowa po znamionach, nie po zdjęciach (94 pary = 34 znamiona, `dane/znamiona.csv`). Nowe zdjęcia znaczników ze znamionami mogą dojść jako dane tylko do treningu.
- **Porównanie do pracy**:
  - (A) ISIC + kandydaci na znamię + auto-przybliżenie,
  - (B) ISIC douczony na własnych zdjęciach,
  - (C) backbone PanDerm uczony tylko na własnych danych.

## Kandydaci na znamię (25.10)
- **Problem**: przy kadrze = całe wnętrze (17 × 17 mm) znamię 1–4 mm zajmuje ułamek wejścia 224×224, a model z ISIC oczekuje znamienia na ~53% kadru. W pierwszym przebiegu zaznaczał duży fragment skóry (cień przy folii, włosy, całą skórę), a auto-przybliżenie przybliżało się do tego błędnego obszaru. Dice z CVAT na 94 parach: średnio 0,38, mediana 0,06, Dice < 0,5 na 56/94 (pary 49–58 ok. 0,02, maska ~100× za duża). W testerze ręczny prostokąt wokół znamienia omijał problem.
- **Rozwiązanie** (`propozycje.py` + `znacznik.segmentuj_w_znaczniku`): do 3 kandydatów = ciemne plamy względem lokalnego tła skóry (L po domknięciu ~0,2 mm usuwającym włosy, tło = mediana w oknie 8 mm, poza obszarem wartość najbliższej skóry, więc cień przy folii nie odstaje; odrzucane pasy wzdłuż folii, kształty niezwarte i wydłużone) → PanDerm na każdym w kadrze jak w ISIC z auto-przybliżeniem → wybór wyniku o największym kontraście brzegu (średnia ciemność w masce minus w pasie 0,4 mm za brzegiem); gdy przybliżanie odpłynie (kontrast < 0,7 najlepszego przebiegu), zostaje przebieg o najlepszym kontraście.
- **Wynik** (94 pary): Dice średnio 0,85, mediana 0,90, Dice < 0,5 na 3/94 (75 i 76 – brak znacznika, 81 – znamię w cieniu przy folii), Dice ≥ 0,8 na 81/94; nigdzie gorzej niż dawniej. Słabsze: 57 (0,54, przy folii), 59 (0,55, bardzo blade znamię).
- Ocena na GPU: `modele_segmentacja/ocen_segmentacje.bat` (obie metody, CSV).

## Detekcja znacznika Π
- Od 23.10 ta sama detekcja co w rejestracji (`dopasowanie3.wykryj_folie_rgb`, wzorzec 35 × 26 mm, pasek 9 mm), zgodność kształtu ≥ 0,65.
- (17.10, stary szablon) na 5/5 zdjęć ze znacznikiem zgodność 0,91–0,95, na 5 bez znacznika brak fałszywych wykryć (≤ 0,55).
