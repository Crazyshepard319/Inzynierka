@echo off
rem Baza danych systemu (SQLite): Inzynierka\dane\baza.sqlite
rem   baza_danych.bat utworz             schemat + znamiona, pary i adnotacje z CVAT (ponownie = aktualizacja)
rem   baza_danych.bat importuj_wyniki    dotychczasowe wyniki z wyniki\wyniki_obu\para_N\metryki.json
rem   baza_danych.bat pokaz              podsumowanie
rem   baza_danych.bat eksport [plik]     ostatnie wyniki par jako CSV (domyslnie wyniki\baza_wyniki_par.csv)
rem   baza_danych.bat eksport_piksele [plik]  piksele znamion na termowizji (domyslnie wyniki\baza_piksele_znamion.csv)
rem   baza_danych.bat sql "SELECT ..."   dowolne zapytanie
cd /d "%~dp0"
"%USERPROFILE%\modele_dane\srodowisko\Scripts\python.exe" -m analiza.baza %*
pause
