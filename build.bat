@echo off
title 4Paws Agent - Building Executable

echo.
echo ╔════════════════════════════════════════╗
echo ║   4Paws Agent Build Script            ║
echo ║   Creating Standalone .exe            ║
echo ╚════════════════════════════════════════╝
echo.

REM Install PyInstaller if not present
python -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo 📦 Installing PyInstaller...
    pip install pyinstaller
    echo.
)

REM Run build script
echo 🔨 Building executable...
python build-exe.py

echo.
echo ✅ Build process completed!
echo.
echo 📂 Check dist/4PawsAgent.exe
echo 📦 Portable package: dist/4PawsAgent-Portable/
echo.
pause

