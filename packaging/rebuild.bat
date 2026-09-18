@echo off
REM ============================================================
REM One-click rebuild: frontend -> app exe -> configurator exe -> installer
REM Usage: packaging\rebuild.bat
REM NOTE: if keys in the dev DB changed, regenerate seed data first:
REM   .venv\Scripts\python.exe packaging\configurator\prepare_seed.py
REM ============================================================
setlocal
set ROOT=%~dp0..
set PKG=%~dp0

echo [1/4] Building frontend ...
cd /d "%ROOT%\frontend" || exit /b 1
call npm run build || exit /b 1

echo [2/4] PyInstaller: main app ...
cd /d "%PKG%"
"%ROOT%\.venv\Scripts\pyinstaller.exe" social-monitor.spec --noconfirm --clean || exit /b 1

echo [3/4] PyInstaller: one-click configurator ...
cd /d "%PKG%configurator"
if not exist seed_data.py (
    echo Missing seed_data.py - run first from project root:
    echo   .venv\Scripts\python.exe packaging\configurator\prepare_seed.py
    exit /b 1
)
"%ROOT%\.venv\Scripts\pyinstaller.exe" oneclick_config.spec --noconfirm --clean || exit /b 1

echo [4/4] Building installer ...
cd /d "%PKG%"
"%LOCALAPPDATA%\Programs\Inno Setup 6\ISCC.exe" installer.iss || exit /b 1
copy /y "configurator\dist\*.exe" "Êä³ö\" >nul

echo.
echo Done! Artifacts in: %PKG%Êä³ö\
echo   - Setup exe (main installer)
echo   - one-click configurator exe
endlocal