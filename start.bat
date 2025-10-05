@echo off
chcp 65001 >nul 2>&1
echo.
echo ╔════════════════════════════════════════╗
echo ║   Starting 4Paws Services             ║
echo ╚════════════════════════════════════════╝
echo.
python agent.py start
echo.
pause

