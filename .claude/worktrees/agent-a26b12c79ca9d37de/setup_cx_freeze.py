# -*- coding: utf-8 -*-
"""
TCL表格比对系统 - Windows 7 兼容版打包配置
使用 cx_Freeze 打包，解决 PyInstaller 在 Win7 上的启动问题
"""

import sys
import os
from cx_Freeze import setup, Executable

# 获取当前目录
base_dir = os.path.dirname(os.path.abspath(__file__))

# 包含的包
packages = [
    'os', 'sys', 'datetime', 'json', 'sqlite3',
    'PyQt5', 'PyQt5.QtCore', 'PyQt5.QtGui', 'PyQt5.QtWidgets',
    'openpyxl', 'openpyxl.utils', 'openpyxl.styles'
]

# 排除不需要的模块（减小体积，提高兼容性）
excludes = [
    'tkinter', 'matplotlib', 'numpy', 'pandas', 'scipy',
    'IPython', 'jupyter', 'notebook', 'pytest', 'unittest',
    'email', 'html', 'xmlrpc', 'xml.etree.ElementTree',
    'multiprocessing', 'asyncio', 'concurrent', 'logging.config'
]

# 包含的文件
include_files = [
    ('TCL表格数据库.db', 'TCL表格数据库.db'),
    ('db_cache.json', 'db_cache.json'),
    ('batch_import_cache.json', 'batch_import_cache.json'),
    ('output_dir_config.json', 'output_dir_config.json'),
    ('network_config.json', 'network_config.json'),
    ('database.py', 'database.py'),
    ('excel_processor.py', 'excel_processor.py'),
    ('network_manager.py', 'network_manager.py'),
    ('server_db.py', 'server_db.py'),
    ('server.py', 'server.py')
]

# Windows可执行文件基础设置
base = None
if sys.platform == 'win32':
    base = 'Win32GUI'  # GUI程序，无控制台窗口

# 构建选项
build_exe_options = {
    "packages": packages,
    "excludes": excludes,
    "include_files": include_files,
    "path": sys.path,
    "optimize": 2,
    "include_msvcr": True
}

# 主程序入口（使用Win7兼容启动脚本）
executables = [
    Executable(
        script='win7_launcher.py',
        base=base,
        target_name='TCL表格比对_Win7.exe'
    )
]

# 设置信息
setup(
    name='TCL表格比对_Win7兼容版',
    version='1.0.0',
    description='TCL表格比对系统 - Windows 7 兼容版本',
    options={'build_exe': build_exe_options},
    executables=executables
)