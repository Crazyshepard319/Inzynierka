@echo off
rem Ocena segmentacji znacznika na termowizji wzgledem CVAT: U-Net M3 (modele foldow) i detektor klasyczny.
rem Wybrane pary: ocen_unet_termal.bat --pary 1-20
rem Wynik: Inzynierka\wyniki\wyniki_segmentacji\unet_termal\ocena_DATA\ (ocena.csv, podsumowanie.txt, tabela.tex)
cd /d "%~dp0.."
"%USERPROFILE%\modele_dane\srodowisko\Scripts\python.exe" -u -m modele_segmentacja.unet_termal.ocena %*
pause
