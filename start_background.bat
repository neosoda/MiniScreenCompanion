@echo off
cd /d "%~dp0"
title Turing 3.5 Companion Launcher

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0launch_service.ps1"

timeout /t 2 >nul
