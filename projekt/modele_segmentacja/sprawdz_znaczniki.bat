@echo off
rem Sprawdzenie znacznika Pi na wszystkich zdjeciach w folderze (podfoldery = znamiona).
rem Uzycie: przeciagnij folder ze zdjeciami na ten plik albo: sprawdz_znaczniki.bat "C:\sciezka\do\folderu"
rem Wynik: Inzynierka\wyniki\wyniki_segmentacji\znaczniki\NAZWA-FOLDERU_DATA\ (podglady + znaczniki.csv)
cd /d "%~dp0.."
if "%~1"=="" (
  echo Przeciagnij folder ze zdjeciami na plik sprawdz_znaczniki.bat
  pause
  exit /b 1
)
"%USERPROFILE%\modele_dane\srodowisko\Scripts\python.exe" -u -m modele_segmentacja.znacznik "%~1"
pause
