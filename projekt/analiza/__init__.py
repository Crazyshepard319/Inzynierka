"""
Analiza wielomodalna pary RGB - termowizja (potok: projekt/potok_pary.py).

    dane.py      wczytanie pary z dane/pary/N/ (obrazy, mapa °C, maski z CVAT, narozniki znacznika)
    geometria.py przenoszenie punktow i masek przez macierz T, homografia px -> mm, skala mm/px
    miary.py     miary zgodnosci: Dice, IoU, HD95, ASSD, przesuniecie srodkow, stosunek pol, TRE
    pomiary.py   parametry znamienia: geometria i kolor (RGB), temperatura i ΔT (termowizja)
    raport.py    raport HTML pary (obrazy osadzone w pliku)
"""
