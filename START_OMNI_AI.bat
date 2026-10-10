@echo off
setlocal EnableDelayedExpansion
title OMNI-AI Launcher

:: ============================================================
::  OMNI-AI — Single-Click Launcher for Windows
::  Double-click this file to start OMNI-AI.
::  Your browser will open automatically.
:: ============================================================

echo.
echo  ====================================================
echo    OMNI-AI  ^|  Intelligent Cross-Platform Assistant
echo  ====================================================
echo.

:: ----------------------------------------------------------
:: 1. Verify Python is available
:: ----------------------------------------------------------
where python >nul 2>&1
if errorlevel 1 (
    echo  [!] Python not found on PATH.
    echo.
    echo  Please install Python 3.10+ from https://www.python.org/downloads/
    echo  Make sure to check "Add Python to PATH" during installation.
    echo.
    pause
    start https://www.python.org/downloads/
    exit /b 1
)

for /f "tokens=*" %%v in ('python --version 2^>^&1') do set PY_VER=%%v
echo  [+] Found %PY_VER%

:: ----------------------------------------------------------
:: 2. Install required dependencies (first run or after update)
:: ----------------------------------------------------------
echo  [+] Checking dependencies...
python -m pip install -q --upgrade pip
python -m pip install -q -r requirements.txt

if errorlevel 1 (
    echo.
    echo  [!] Dependency installation failed.
    echo      Try running install.bat as Administrator.
    echo.
    pause
    exit /b 1
)

echo  [+] Dependencies OK
echo.

:: ----------------------------------------------------------
:: 3. Launch the app
:: ----------------------------------------------------------
echo  [+] Starting OMNI-AI on http://localhost:5000
echo  [+] Your browser will open automatically.
echo  [+] Press Ctrl+C in this window to stop the app.
echo.

python app.py

:: If the app exits cleanly, keep the window open so the user
:: can read any final messages.
echo.
echo  [i] OMNI-AI has stopped.
pause
endlocal
