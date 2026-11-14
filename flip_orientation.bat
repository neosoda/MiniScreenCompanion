@echo off
title Flip Turing 3.5 Orientation (180deg)
cd /d "%~dp0"

echo [3.5] Toggling Turing screen orientation between 0 and 180 degrees...
python "%~dp0flip_orientation.py"
echo.
echo Termine. Appuyez sur une touche pour fermer...
pause >nul
