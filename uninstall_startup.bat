@echo off
title Uninstall Turing 3.5 Autostart
cd /d "%~dp0"

echo [3.5] Removing Turing 3.5 Companion from Windows Startup...
python setup_autostart.py uninstall

echo.
pause
