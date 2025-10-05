@echo off
chcp 65001 >nul 2>&1
title 4Paws Agent - Starting...

echo.
echo ╔════════════════════════════════════════╗
echo ║   4Paws Agent Web GUI                 ║
echo ║   Starting Dashboard...               ║
echo ╚════════════════════════════════════════╝
echo.

python gui_server.py
echo.
pause

