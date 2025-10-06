@echo off
REM Start 4Paws Complete System (Agent + Frontend + Backend)

echo ========================================
echo 4Paws Complete System Launcher
echo ========================================
echo.
echo Starting all services...
echo.

REM Start agent server (GUI + API)
echo [1/3] Starting Agent Server (API + Management GUI)...
start "4Paws Agent Server" cmd /c "cd /d %~dp0 && python gui_server.py"
echo       Started at: http://localhost:5000
echo.

REM Wait for agent server to initialize
echo Waiting for agent server to initialize...
timeout /t 5 /nobreak >nul

echo.
echo [2/3] Agent will auto-start frontend and backend...
echo       This may take 30-60 seconds...
echo.
echo ========================================
echo System Access URLs:
echo ========================================
echo.
echo    Agent GUI: http://localhost:5000
echo    Frontend:  http://localhost:3100
echo    Backend:   http://localhost:3200
echo.
echo ========================================
echo.
echo Opening browser in 5 seconds...
timeout /t 5 /nobreak >nul

REM Open frontend in browser
start http://localhost:3100

echo.
echo ========================================
echo System is starting...
echo ========================================
echo.
echo The agent server window will open.
echo DO NOT close it - it manages all services.
echo.
echo To stop all services:
echo   1. Close the "4Paws Agent Server" window
echo   OR
echo   2. Press Ctrl+C in agent window
echo.
echo ========================================

