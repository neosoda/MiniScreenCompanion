@echo off
title Turing 3.5 Companion Status
cd /d "%~dp0"

"C:\Users\NEO.NEO-PC\AppData\Local\Programs\Python\Python312\python.exe" "%~dp0run.py" --status
echo.
echo --- Last 10 Log Entries ---
powershell -NoProfile -Command "if (Test-Path '%~dp0companion.log') { Get-Content '%~dp0companion.log' -Tail 10 } else { Write-Host 'No log file found.' }"
echo.
pause
