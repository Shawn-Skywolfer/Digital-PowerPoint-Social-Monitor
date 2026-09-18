@echo off
REM 本机一键启动（无 Docker）：后端 + 前端 各开一个窗口
REM 双击运行，或在项目根执行： start-local.bat
setlocal
set ROOT=%~dp0

echo [1/2] 启动后端 http://127.0.0.1:8000 ...
start "社媒监测-后端" cmd /k "cd /d "%ROOT%backend" && "%ROOT%.venv\Scripts\python.exe" -m uvicorn app.main:app --port 8000"

echo [2/2] 启动前端 http://localhost:5173 ...
start "社媒监测-前端" cmd /k "cd /d "%ROOT%frontend" && npm run dev"

echo.
echo 两个窗口已启动。浏览器访问: http://localhost:5173
echo 默认账号: Admin / Seek22626301 （首登改密）
echo 当前为 Mock 数据源（.env 中 PROVIDER_MOCK=true），离线可测全流程。
echo 关闭对应窗口即停止服务。
endlocal
