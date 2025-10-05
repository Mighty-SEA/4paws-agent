@echo off
chcp 65001 >nul 2>&1
echo.
echo ╔════════════════════════════════════════╗
echo ║   Stopping 4Paws Services             ║
echo ╚════════════════════════════════════════╝
echo.
python agent.py stop
echo.
pause

