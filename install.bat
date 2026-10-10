@echo off
setlocal EnableDelayedExpansion
title OMNI-AI Setup

echo.
echo  ====================================================
echo    OMNI-AI  ^|  First-Time Setup
echo  ====================================================
echo.

:: Verify Python
where python >nul 2>&1
if errorlevel 1 (
    echo  [!] Python not found. Please install Python 3.10+ from:
    echo      https://www.python.org/downloads/
    pause
    start https://www.python.org/downloads/
    exit /b 1
)

for /f "tokens=*" %%v in ('python --version 2^>^&1') do set PY_VER=%%v
echo  [+] %PY_VER% detected

echo.
echo  [+] Upgrading pip...
python -m pip install --upgrade pip

echo.
echo  [+] Installing required packages...
python -m pip install -r requirements.txt
if errorlevel 1 (
    echo  [!] Required package install failed. Check your internet connection.
    pause
    exit /b 1
)

echo.
echo  [?] Install optional AI / Voice packages? (takes several minutes, ~2GB)
echo      These enable: PyTorch model, speech recognition, text-to-speech
echo.
set /p INSTALL_OPT="  Install optional packages? [y/N]: "

if /i "!INSTALL_OPT!"=="y" (
    echo  [+] Installing optional packages (this may take a while)...
    python -m pip install -r requirements-optional.txt
    if errorlevel 1 (
        echo  [!] Some optional packages failed — this is OK.
        echo      The app will still run with reduced features.
    ) else (
        echo  [+] Optional packages installed.
    )
)

echo.
echo  ====================================================
echo    Setup complete!  Run START_OMNI_AI.bat to launch.
echo  ====================================================
echo.
pause
endlocal
