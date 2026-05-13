@echo off
chcp 65001 >nul
echo ============================================
echo   TCL表格比对 - Windows 7 兼容版打包
echo   Python 3.8 + PyInstaller
echo ============================================
echo.

REM 使用Python 3.8
set PYTHON_EXE=D:\py\python38\python.exe

REM 检查Python 3.8是否存在
if not exist "%PYTHON_EXE%" (
    echo [ERROR] 未找到Python 3.8: %PYTHON_EXE%
    echo 请确认已安装Python 3.8并修改此脚本中的路径
    pause
    exit /b 1
)

echo [INFO] 使用Python:
%PYTHON_EXE% --version
echo.

REM 检查并安装依赖
echo [STEP 1] 检查依赖...
%PYTHON_EXE% -c "import PyQt5" 2>nul
if errorlevel 1 (
    echo [INFO] 安装 PyQt5...
    %PYTHON_EXE% -m pip install PyQt5==5.15.9
)

%PYTHON_EXE% -c "import openpyxl" 2>nul
if errorlevel 1 (
    echo [INFO] 安装 openpyxl...
    %PYTHON_EXE% -m pip install openpyxl==3.1.2
)

%PYTHON_EXE% -c "import flask" 2>nul
if errorlevel 1 (
    echo [INFO] 安装 Flask...
    %PYTHON_EXE% -m pip install flask==2.3.3 flask-cors==4.0.0
)

%PYTHON_EXE% -c "import requests" 2>nul
if errorlevel 1 (
    echo [INFO] 安装 requests...
    %PYTHON_EXE% -m pip install requests==2.31.0
)

%PYTHON_EXE% -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo [INFO] 安装 PyInstaller...
    %PYTHON_EXE% -m pip install PyInstaller==5.6.2
)

echo [OK] 依赖检查完成
echo.

REM 清理旧的构建文件
echo [STEP 2] 清理旧文件...
if exist "build" rmdir /s /q "build"
if exist "dist\TCL表格比对_Win7" rmdir /s /q "dist\TCL表格比对_Win7"
echo [OK] 清理完成
echo.

REM 开始打包
echo ============================================
echo [STEP 3] 开始打包（Windows 7 兼容版）
echo ============================================
echo.
echo [INFO] 这可能需要5-10分钟，请耐心等待...
echo.

%PYTHON_EXE% -m PyInstaller scripts\build_win7_final.spec --clean --noconfirm

if errorlevel 1 (
    echo.
    echo [ERROR] 打包失败！请查看上方错误信息
    pause
    exit /b 1
)

echo.
echo ============================================
echo   打包成功！
echo ============================================
echo.
echo   PyInstaller 输出: dist\TCL表格比对_Win7\
echo.
echo ============================================
echo [STEP 4] 使用 Inno Setup 制作安装包
echo ============================================
echo.

set ISCC_EXE=C:\Program Files (x86)\Inno Setup 6\ISCC.exe

if not exist "%ISCC_EXE%" (
    echo [WARN] 未找到 Inno Setup 6，跳过安装包制作
    echo   请安装 Inno Setup 6: https://jrsoftware.org/isinfo.php
    echo.
    echo   分发方式（手动）:
    echo   将 dist\TCL表格比对_Win7 文件夹压缩为ZIP发送给用户
    goto :end
)

REM 检查 VC++ Redistributable
if not exist "resources\vc_redist.x64.exe" (
    echo [WARN] 未找到 resources\vc_redist.x64.exe，安装包将不包含 VC++ 运行库
    echo   下载地址: https://aka.ms/vs/17/release/vc_redist.x64.exe
    echo   下载后放到 resources\ 目录即可
    echo.
)

echo [INFO] 编译安装包...
"%ISCC_EXE%" scripts\installer.iss

if errorlevel 1 (
    echo.
    echo [ERROR] Inno Setup 编译失败！
    pause
    exit /b 1
)

echo.
echo ============================================
echo   全部完成！
echo ============================================
echo.
echo   安装包: Output\TCL表格比对_Setup.exe
echo   分发给用户后双击安装即可
echo.

:end
pause
