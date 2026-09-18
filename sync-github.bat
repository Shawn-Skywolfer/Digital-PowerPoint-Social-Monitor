@echo off
REM One-click sync to GitHub: git add + commit + push
REM Usage: sync-github.bat [commit message]
REM   without args, a timestamped default message is used
REM Proxy and identity are set in repo-local git config; credentials via Windows Credential Manager
cd /d %~dp0
set msg=%*
if "%msg%"=="" set msg=update %date% %time%

git add -A
git diff --cached --quiet
if %errorlevel%==0 (
  echo [sync] Nothing to commit, working tree is clean.
  exit /b 0
)
git commit -m "%msg%"
if errorlevel 1 exit /b 1
git push
if errorlevel 1 (
  echo [sync] Push failed - check network/proxy and retry.
  exit /b 1
)
echo [sync] Synced to GitHub: https://github.com/Shawn-Skywolfer/Digital-PowerPoint-Social-Monitor