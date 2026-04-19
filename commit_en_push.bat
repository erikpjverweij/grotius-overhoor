@echo off
REM Script om de openstaande wijzigingen te committen en te pushen.
REM Draai dit vanuit de map C:\Users\ErikVerweij\Claude\Grotius\Algemeen\overhoor-app\

cd /d "%~dp0"

REM Verwijder de stale index.lock als die bestaat
if exist ".git\index.lock" (
    echo Verwijder stale index.lock...
    del /f /q ".git\index.lock"
)

echo Git status:
git status

echo.
echo Bestanden toevoegen...
git add cards.json cards.js Kaarten_review_v3.xlsx

echo.
echo Commit maken...
git commit -m "Uitbreiding: 128 kaarten toegevoegd voor modules 04, 06, 07, 08, 11 en 19 (totaal 187 kaarten, 9 modules)"

echo.
echo Pushen naar origin/main...
git push origin main

echo.
echo Klaar. Druk op een toets om te sluiten.
pause
