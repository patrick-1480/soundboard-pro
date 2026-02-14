@echo off
title Soundboard Pro v3.0.0 - Windows Build
color 0A

echo.
echo ============================================
echo   SOUNDBOARD PRO v3.0.0 - WINDOWS BUILD
echo ============================================
echo.

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Install Python 3.11 from python.org
    pause & exit /b 1
)

:: Install dependencies
echo [1/4] Installing dependencies...
pip install sounddevice numpy librosa keyboard scipy numba cffi soundfile soxr resampy pyinstaller --upgrade --quiet
if errorlevel 1 (
    echo [ERROR] Dependency install failed.
    pause & exit /b 1
)
echo       Done.

:: Clean old build
echo [2/4] Cleaning previous build...
if exist build              rmdir /s /q build
if exist dist               rmdir /s /q dist
if exist "Soundboard Pro.spec" del /q "Soundboard Pro.spec"
if not exist sounds         mkdir sounds
echo       Done.

:: Build EXE
echo [3/4] Building EXE...
pyinstaller ^
    --noconsole ^
    --onefile ^
    --name "Soundboard Pro" ^
    --icon=icon.ico ^
    --add-data "ui;ui" ^
    --add-data "sounds;sounds" ^
    --add-data "config.json;." ^
    --hidden-import sounddevice ^
    --hidden-import numpy ^
    --hidden-import librosa ^
    --hidden-import scipy ^
    --hidden-import numba ^
    --hidden-import cffi ^
    --hidden-import soundfile ^
    --hidden-import keyboard ^
    app.py

if errorlevel 1 (
    echo.
    echo [ERROR] PyInstaller failed. See output above.
    pause & exit /b 1
)

if not exist "dist\Soundboard Pro.exe" (
    echo [ERROR] EXE not found after build.
    pause & exit /b 1
)
echo       EXE: dist\Soundboard Pro.exe

:: Build installer (optional - only if Inno Setup installed)
echo [4/4] Building installer...
set ISCC="C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
if exist %ISCC% (
    %ISCC% installer.iss
    if errorlevel 1 (
        echo [WARN] Installer build failed - EXE is still available.
    ) else (
        echo       Installer: installer_output\SoundboardPro_Setup_v3.0.0.exe
    )
) else (
    echo [SKIP] Inno Setup not found. Download from https://jrsoftware.org/isdl.php
    echo        The standalone EXE in dist\ still works without an installer.
)

echo.
echo ============================================
echo   BUILD COMPLETE
echo ============================================
echo.
echo   Standalone EXE:  dist\Soundboard Pro.exe
if exist "installer_output\SoundboardPro_Setup_v3.0.0.exe" (
    echo   Installer:       installer_output\SoundboardPro_Setup_v3.0.0.exe
)
echo.
echo Press any key to exit...
pause >nul
