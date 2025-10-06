@echo off
REM Start 4Paws Agent with verbose pnpm output

echo ========================================
echo 4Paws Agent - Verbose Mode
echo ========================================
echo.
echo This mode shows detailed pnpm output
echo during dependency installation.
echo.
echo Useful for:
echo   - Troubleshooting slow installations
echo   - Seeing download progress
echo   - Debugging package issues
echo.
echo ========================================
echo.

REM Set verbose mode
set PNPM_VERBOSE=1
set VERBOSE=1

REM Start agent
python agent.py %*

