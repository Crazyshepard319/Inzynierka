@echo off
rem Aplikacja do testowania modeli segmentacji znamion
cd /d "%~dp0.."
"%USERPROFILE%\modele_dane\srodowisko\Scripts\python.exe" -m modele_segmentacja.tester %*
if errorlevel 1 pause
