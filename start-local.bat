@echo off
REM Local one-click start (no Docker): backend + frontend, each in its own window
REM Double-click, or run from project root: start-local.bat
setlocal
set ROOT=%~dp0

echo [1/2] Starting backend  http://127.0.0.1:8000 ...
start "Monitor-Backend" cmd /k "cd /d "%ROOT%backend" && "%ROOT%.venv\Scripts\python.exe" -m uvicorn app.main:app --port 8000"

echo [2/2] Starting frontend http://localhost:5173 ...
start "Monitor-Frontend" cmd /k "cd /d "%ROOT%frontend" && npm run dev"

echo.
echo Both windows started. Open: http://localhost:5173
echo Default account: Admin / Seek22626301 (forced password change on first login)
echo Mock provider is on (PROVIDER_MOCK=true in .env) - full flow works offline.
echo Close a window to stop that service.
endlocal