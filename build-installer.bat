@echo off
chcp 65001 >nul 2>&1
setlocal enabledelayedexpansion

echo.
echo ╔════════════════════════════════════════╗
echo ║   4Paws Agent Installer Builder       ║
echo ║        NSIS Installer Creation        ║
echo ╚════════════════════════════════════════╝
echo.

:: Step 1: Build executable
echo ==================================================
echo   Step 1: Building Executable
echo ==================================================
echo.
python build-exe.py
if errorlevel 1 (
    echo.
    echo ❌ Failed to build executable!
    pause
    exit /b 1
)

:: Step 2: Prepare installer files
echo.
echo ==================================================
echo   Step 2: Preparing Installer Files
echo ==================================================
echo.
python installer\prepare-installer.py
if errorlevel 1 (
    echo.
    echo ❌ Failed to prepare installer files!
    pause
    exit /b 1
)

:: Step 3: Check for NSIS
echo.
echo ==================================================
echo   Step 3: Building NSIS Installer
echo ==================================================
echo.

set "NSIS_PATH="
set "MAKENSIS="

:: Check common NSIS installation paths
if exist "C:\Program Files (x86)\NSIS\makensis.exe" (
    set "MAKENSIS=C:\Program Files (x86)\NSIS\makensis.exe"
    set "NSIS_PATH=C:\Program Files (x86)\NSIS"
)
if exist "C:\Program Files\NSIS\makensis.exe" (
    set "MAKENSIS=C:\Program Files\NSIS\makensis.exe"
    set "NSIS_PATH=C:\Program Files\NSIS"
)

:: Check if makensis is in PATH
where makensis >nul 2>&1
if !errorlevel! equ 0 (
    set "MAKENSIS=makensis"
)

if "!MAKENSIS!"=="" (
    echo.
    echo ╔════════════════════════════════════════════════╗
    echo ║   NSIS Not Found - Manual Installation Needed ║
    echo ╚════════════════════════════════════════════════╝
    echo.
    echo ❌ NSIS is not installed on this system.
    echo.
    echo To build the installer, you need to:
    echo.
    echo 1. Download NSIS from:
    echo    https://nsis.sourceforge.io/Download
    echo.
    echo 2. Install NSIS (default location is fine^)
    echo.
    echo 3. Run this script again
    echo.
    echo OR manually compile:
    echo    Right-click installer\installer.nsi
    echo    Select "Compile NSIS Script"
    echo.
    pause
    exit /b 1
)

echo ✓ Found NSIS at: !NSIS_PATH!
echo.
echo 🔨 Compiling installer...
echo    This may take 2-5 minutes (compressing ~145 MB)
echo.

:: Compile installer
"!MAKENSIS!" /V3 installer\installer.nsi

if errorlevel 1 (
    echo.
    echo ❌ Failed to compile installer!
    echo.
    echo Check the output above for errors.
    pause
    exit /b 1
)

:: Check output
if exist "dist\4PawsAgent-Setup.exe" (
    echo.
    echo ╔════════════════════════════════════════╗
    echo ║   Installer Build Complete!           ║
    echo ╚════════════════════════════════════════╝
    echo.
    
    :: Get file size
    for %%A in ("dist\4PawsAgent-Setup.exe") do set SIZE=%%~zA
    set /a SIZE_MB=!SIZE! / 1048576
    
    echo ✓ Installer created successfully!
    echo.
    echo 📦 File: dist\4PawsAgent-Setup.exe
    echo 📊 Size: !SIZE_MB! MB
    echo.
    echo ==================================================
    echo   Testing & Distribution
    echo ==================================================
    echo.
    echo To test the installer:
    echo   1. Run: dist\4PawsAgent-Setup.exe
    echo   2. Follow installation wizard
    echo   3. Launch from Start Menu
    echo.
    echo To distribute:
    echo   - Share: dist\4PawsAgent-Setup.exe
    echo   - Users just need to run it (no dependencies^)
    echo   - Includes Node.js + MariaDB + Agent
    echo.
) else (
    echo.
    echo ❌ Installer file not found after compilation!
    pause
    exit /b 1
)

echo.
pause

