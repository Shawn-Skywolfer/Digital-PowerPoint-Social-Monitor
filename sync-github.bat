@echo off
rem ============================================================
rem 一键同步代码到 GitHub（git add + commit + push）
rem 用法：sync-github.bat [提交说明]
rem   不带参数时自动用时间戳作提交说明
rem 代理与身份已在仓库级 git config 配好，凭证走 Windows 凭据管理器
rem ============================================================
cd /d %~dp0
set msg=%*
if "%msg%"=="" set msg=update %date% %time%

git add -A
git diff --cached --quiet
if %errorlevel%==0 (
  echo [sync] 没有需要提交的变更，工作区已是最新。
  exit /b 0
)
git commit -m "%msg%"
if errorlevel 1 exit /b 1
git push
if errorlevel 1 (
  echo [sync] 推送失败，请检查网络/代理后重试。
  exit /b 1
)
echo [sync] 已同步到 GitHub: https://github.com/Shawn-Skywolfer/Digital-PowerPoint-Social-Monitor
