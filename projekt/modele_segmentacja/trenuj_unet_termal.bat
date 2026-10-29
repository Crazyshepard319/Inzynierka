@echo off
rem Trening U-Netu (model M3): znacznik Pi na termowizji - 5 foldow (walidacja krzyzowa po znamionach)
rem + model na wszystkich parach. Parametry: --epoki N, --proba (szybki test), --foldy 1 2, --bez_koncowego
rem Wagi: %USERPROFILE%\modele_dane\wagi\unet_termal\ (fold1..5.onnx, wszystkie.onnx)
rem Logi i ocena: Inzynierka\wyniki\wyniki_segmentacji\unet_termal\trening_DATA\
cd /d "%~dp0.."
set PY="%USERPROFILE%\modele_dane\srodowisko\Scripts\python.exe"
%PY% -c "import onnx" 2>nul || %PY% -m pip install onnx
%PY% -u -m modele_segmentacja.unet_termal.trening %*
pause
