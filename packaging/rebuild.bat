@echo off
REM 一键重新打包：前端构建 → PyInstaller 主程序 → 一键配置 exe → Inno Setup 安装包
REM 在项目根任意位置执行：packaging\rebuild.bat
REM 注意：若开发库里配置的 Key 有新增/变更，请先执行一次
REM   .venv\Scripts\python.exe packaging\configurator\prepare_seed.py
REM 重新生成种子数据（会换发新的分发密钥），再运行本脚本。
setlocal
set ROOT=%~dp0..
set PKG=%~dp0

echo [1/4] 构建前端 ...
cd /d "%ROOT%\frontend" || exit /b 1
call npm run build || exit /b 1

echo [2/4] PyInstaller 打包后端+前端 ...
cd /d "%PKG%"
"%ROOT%\.venv\Scripts\pyinstaller.exe" social-monitor.spec --noconfirm --clean || exit /b 1

echo [3/4] PyInstaller 打包一键配置程序 ...
cd /d "%PKG%configurator"
if not exist seed_data.py (
    echo 缺少 seed_data.py，请先在项目根执行：
    echo   .venv\Scripts\python.exe packaging\configurator\prepare_seed.py
    exit /b 1
)
"%ROOT%\.venv\Scripts\pyinstaller.exe" --noconfirm --clean --onefile --windowed ^
    --name "社媒监测一键配置" --distpath "dist-config" oneclick_config.py || exit /b 1

echo [4/4] 生成安装包 ...
cd /d "%PKG%"
"%LOCALAPPDATA%\Programs\Inno Setup 6\ISCC.exe" installer.iss || exit /b 1
copy /y "configurator\dist-config\社媒监测一键配置.exe" "输出\" >nul

echo.
echo 完成！分发产物位于： %PKG%输出\
echo   - 社媒监测洞察系统-Setup-*.exe   （主程序安装包）
echo   - 社媒监测一键配置.exe           （装后运行一次，自动配好 Key）
endlocal
