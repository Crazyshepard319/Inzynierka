@echo off
rem Douczanie PanDerm + UperNet na ISIC 2018 (parametry: --wznow, --epoki N, --proba, --tylko_test)
cd /d "%~dp0.."
"%USERPROFILE%\modele_dane\srodowisko\Scripts\python.exe" -u -m modele_segmentacja.modele.panderm_upernet.trening %*
pause
