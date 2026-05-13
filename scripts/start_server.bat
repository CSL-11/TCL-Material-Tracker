@echo off
chcp 65001 >nul
echo ============================================
echo   TCL表格比对系统 - 局域网服务器启动脚本
echo ============================================
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] 未检测到Python，请先安装Python 3.7+
    pause
    exit /b 1
)

echo [STEP 1] 检查依赖包...
pip install -r requirements\requirements_server.txt >nul 2>&1

echo [STEP 2] 获取本机IP地址...
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /i "IPv4"') do set LOCAL_IP=%%a
set LOCAL_IP=%LOCAL_IP: =%

echo.
echo ============================================
echo   服务器信息
echo ============================================
echo   本机IP地址: %LOCAL_IP%
echo   监听端口: 5000
echo   客户端连接地址: http://%LOCAL_IP%:5000
echo ============================================
echo.
echo [IMPORTANT] 请确保：
echo   1. 防火墙允许端口5000入站连接
echo   2. 局域网内其他电脑可以ping通此IP
echo.
echo 按任意键启动服务器...
pause >nul

echo.
echo [STARTING] 正在启动服务器...
echo [TIP] 按 Ctrl+C 停止服务器
echo.

python server.py --host 0.0.0.0 --port 5000

pause
