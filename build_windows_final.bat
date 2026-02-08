@echo off
echo ====================================
echo Building Soundboard Pro for Windows
echo ====================================
echo.

REM Check for icon
if not exist icon.ico (
    echo WARNING: icon.ico not found!
    echo Download an icon and save as icon.ico in the project folder.
    echo You can continue without it, but the app won't have a custom icon.
    echo.
    pause
)

REM Clean old builds
echo [1/3] Cleaning old build files...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist "Soundboard Pro.spec" del /q "Soundboard Pro.spec"
echo Done!
echo.

REM Build with PyInstaller
echo [2/3] Building executable with PyInstaller...
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

echo.
if %ERRORLEVEL% NEQ 0 (
    echo ====================================
    echo BUILD FAILED! Check errors above.
    echo ====================================
    pause
    exit /b 1
)

echo [3/3] Build successful!
echo.

REM Create portable package
echo Creating portable package...
if not exist "dist\portable" mkdir "dist\portable"
copy "dist\Soundboard Pro.exe" "dist\portable\"
if not exist "dist\portable\sounds" mkdir "dist\portable\sounds"
copy config.json "dist\portable\"

echo.
echo ====================================
echo SUCCESS!
echo ====================================
echo.
echo Standalone EXE: dist\Soundboard Pro.exe
echo Portable package: dist\portable\
echo.
echo NEXT STEPS:
echo 1. Test the EXE by running it
echo 2. (Optional) Create installer with Inno Setup
echo    - Install Inno Setup from https://jrsoftware.org/isdl.php
echo    - Open installer.iss and compile
echo.
echo *** IMPORTANT FOR DISTRIBUTION ***
echo For the EXE to run properly on other computers:
echo - They need VB-Audio Cable installed
echo - Run as Administrator for global hotkeys
echo - Windows may show SmartScreen warning (normal for unsigned apps)
echo.
pause