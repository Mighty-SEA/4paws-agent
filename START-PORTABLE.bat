@echo off
REM Quick start script for portable 4Paws Agent
REM Validates installation and starts the application

echo ========================================
echo  4Paws Agent - Portable Quick Start
echo ========================================
echo.

REM Change to script directory
cd /d "%~dp0"

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed!
    echo.
    echo Please install Python 3.8 or later:
    echo https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

echo [1/3] Validating portable installation...
python validate-portable.py
if %errorlevel% neq 0 (
    echo.
    echo [WARNING] Validation found issues!
    echo Continue anyway? (Y/N)
    set /p continue=
    if /i not "%continue%"=="Y" (
        echo Installation cancelled.
        pause
        exit /b 1
    )
)

echo.
echo [2/3] Starting Web GUI server...
echo.
echo Web GUI will open at: http://localhost:5000
echo Press Ctrl+C to stop the server
echo.
timeout /t 3 /nobreak

REM Start the GUI server
python gui_server.py

pause

