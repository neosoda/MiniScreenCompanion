@echo off
title Stop Turing 3.5 Companion
cd /d "%~dp0"

echo [3.5] Stopping Turing 3.5 Companion...
"C:\Users\NEO.NEO-PC\AppData\Local\Programs\Python\Python312\python.exe" "%~dp0run.py" --stop

timeout /t 2 >nul
