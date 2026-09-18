@echo off
REM ============================================================
REM One-click rebuild: frontend -> app exe -> configurator exe -> installer
REM Usage: packaging\rebuild.bat
REM NOTE: if keys in the dev DB changed, regenerate seed data first:
REM   .venv\Scripts\python.exe packaging\configurator\prepare_seed.py
REM NOTE: PyInstaller rebuilds the onedir folder and WIPES dist data/.env,
REM so this script backs them up first and restores them afterwards.
REM ============================================================
setlocal
set ROOT=%~dp0..
set PKG=%~dp0
set DISTDIR=%PKG%dist\社媒监测洞察系统
set BACKUP=%PKG%dist-backup

echo [0/4] Backing up dist data/.env ...
if exist "%DISTDIR%\data" (
    if not exist "%BACKUP%" mkdir "%BACKUP%"
    xcopy /e /i /y /q "%DISTDIR%\data" "%BACKUP%\data\" >nul
)
if exist "%DISTDIR%\.env" copy /y "%DISTDIR%\.env" "%BACKUP%\" >nul

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
copy /y "configurator\dist\*.exe" "输出\"
if errorlevel 1 echo WARN: copying configurator exe failed - copy manually from configurator\dist

echo Restoring dist data/.env ...
if exist "%BACKUP%\data" xcopy /e /i /y /q "%BACKUP%\data" "%DISTDIR%\data\" >nul
if exist "%BACKUP%\.env" copy /y "%BACKUP%\.env" "%DISTDIR%\" >nul

echo.
echo Done! Artifacts in: %PKG%输出\
echo   - Setup exe (main installer)
echo   - one-click configurator exe
endlocal