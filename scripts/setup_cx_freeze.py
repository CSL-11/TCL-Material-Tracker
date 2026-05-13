# -*- coding: utf-8 -*-
"""
TCL表格比对系统 - Windows 7 兼容版打包配置
使用 cx_Freeze 打包，解决 PyInstaller 在 Win7 上的启动问题

使用方法（从项目根目录运行）:
    py -3.8 scripts\setup_cx_freeze.py build
"""

import sys
import os
from cx_Freeze import setup, Executable

# 脚本在 scripts/ 目录，项目根目录是上一级
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 从 version.py 读取版本号
def get_version():
    version_file = os.path.join(base_dir, 'version.py')
    with open(version_file, 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith('__version__'):
                return line.split('=')[1].strip().strip('"').strip("'")
    return '1.0.0'

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

# 包含的文件（配置和数据库在 data/ 目录，图标在 resources/ 目录）
include_files = [
    ('data/TCL表格数据库.db', 'TCL表格数据库.db'),
    ('data/db_cache.json', 'db_cache.json'),
    ('data/batch_import_cache.json', 'batch_import_cache.json'),
    ('data/output_dir_config.json', 'output_dir_config.json'),
    ('data/network_config.json', 'network_config.json'),
    ('resources/icon.png', 'icon.png'),
    ('database.py', 'database.py'),
    ('excel_processor.py', 'excel_processor.py'),
    ('network_manager.py', 'network_manager.py'),
    ('server_db.py', 'server_db.py'),
    ('server.py', 'server.py'),
    ('version.py', 'version.py')
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
    version=get_version(),
    description='TCL表格比对系统 - Windows 7 兼容版本',
    options={'build_exe': build_exe_options},
    executables=executables
)