@echo off
chcp 65001 >nul
echo ========================================
echo     TCL表格比对系统 启动中...
echo ========================================
echo.

REM 切换到项目根目录（脚本在 scripts/ 目录）
cd /d "%~dp0.."

python main_app.py

if errorlevel 1 (
    echo.
    echo 程序运行出错，请检查错误信息
    pause
)