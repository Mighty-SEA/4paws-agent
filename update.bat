@echo off
chcp 65001 >nul 2>&1
echo.
echo ╔════════════════════════════════════════╗
echo ║   Checking for Updates                ║
echo ╚════════════════════════════════════════╝
echo.
python agent.py update
echo.
pause

