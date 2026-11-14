@echo off
setlocal enabledelayedexpansion
title Mini Screen Companion

echo ======================================================
echo           MINI SCREEN COMPANION - STARTUP
echo ======================================================
echo.

:: 1. Check Python
where python >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Python is not installed or not in PATH!
    echo Please install Python 3.9+ from https://www.python.org/
    pause
    exit /b 1
)

:: 2. Check / Create Virtualenv
if not exist ".venv" (
    echo [*] Creating virtual environment (.venv)...
    python -m venv .venv
)

:: 3. Activate Virtualenv
call .venv\Scripts\activate.bat

:: 4. Install requirements if needed
echo [*] Checking dependencies...
pip install -q -r requirements.txt

:: 5. Check configuration
if not exist "config.json" (
    echo [*] Generating default config.json from template...
    copy config.example.json config.json >nul
    echo [!] Created config.json. You can edit it with your screen IP.
)

:: 6. Launch CLI
echo.
echo [*] Starting Mini Screen Companion...
python -m mini_screen_companion once
if %ERRORLEVEL% equ 0 (
    echo.
    echo [*] First upload test succeeded!
    echo [*] Starting continuous background loop...
    python -m mini_screen_companion run
) else (
    echo.
    echo [!] Initial push failed. Make sure your screen is connected to Wi-Fi.
    echo [*] You can scan your network with: python -m mini_screen_companion discover
    pause
)
