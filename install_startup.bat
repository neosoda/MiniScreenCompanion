@echo off
title Install Turing 3.5 Autostart
cd /d "%~dp0"

echo [3.5] Installing Turing 3.5 Companion to Windows Startup...
python setup_autostart.py install

echo.
pause
