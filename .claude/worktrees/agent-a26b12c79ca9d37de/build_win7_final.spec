# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller 配置文件 - TCL表格比对系统（Windows 7 终极兼容版）
基于 build_win7_fixed.spec，添加 flask_cors 等缺失依赖

使用Python 3.8 + PyInstaller 5.6.2

特点：
- 完全兼容 Windows 7 SP1 及以上版本
- 包含客户端和服务器功能（统一版）
- 包含运行时修复脚本（解决 pyimod02_importers 错误）
- 关闭 UPX 压缩（某些 Win7 环境 UPX 有问题）

使用方法:
    D:\py\python38\python.exe -m PyInstaller build_win7_final.spec

生成文件:
    dist/TCL表格比对_Win7/ (约80-120MB)
"""

import sys
import os
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# ==================== 基础配置 ====================

block_cipher = None
work_dir = os.path.dirname(os.path.abspath(SPEC))

app_name = 'TCL表格比对'

# ==================== 数据文件 ====================

datas = []
datas += collect_data_files('PyQt5')
datas += collect_data_files('openpyxl')

# 数据文件
data_files = [
    ('db_cache.json', '.'),
    ('batch_import_cache.json', '.'),
    ('output_dir_config.json', '.'),
]

for src, dst in data_files:
    if os.path.exists(os.path.join(work_dir, src)):
        datas.append((os.path.join(work_dir, src), dst))

# ==================== 隐藏导入 ====================

hiddenimports = [
    # 核心Python模块
    'encodings',
    'encodings.utf_8',
    'encodings.gbk',
    'encodings.latin1',

    # PyQt5核心组件
    'PyQt5.QtCore',
    'PyQt5.QtGui',
    'PyQt5.QtWidgets',
    'PyQt5.sip',

    # 业务逻辑模块
    'database',
    'excel_processor',
    'network_manager',
    'server_db',

    # Excel处理
    'openpyxl',
    'et_xmlfile',

    # Flask服务器组件
    'flask',
    'flask.app',
    'flask_cors',
    'werkzeug',
    'jinja2',
    'markupsafe',
    'itsdangerous',
    'click',

    # HTTP请求库
    'requests',
    'urllib3',
    'certifi',
    'charset_normalizer',
    'idna',
]

# 只收集必需的子模块
hiddenimports += collect_submodules('PyQt5.QtCore')
hiddenimports += collect_submodules('PyQt5.QtGui')
hiddenimports += collect_submodules('PyQt5.QtWidgets')

# ==================== 排除不需要的模块 ====================

excludes = [
    # 大型不需要的库
    'numpy', 'pandas', 'scipy', 'matplotlib',
    'IPython', 'jupyter', 'notebook', 'pytest',
    'PIL', 'cv2', 'torch', 'tensorflow',

    # Qt高级功能（Win7性能差）
    'PyQt5.Qt3D',
    'PyQt5.Qt3DAnimation',
    'PyQt5.Qt3DCore',
    'PyQt5.Qt3DExtras',
    'PyQt5.Qt3DInput',
    'PyQt5.Qt3DLogic',
    'PyQt5.Qt3DRender',
    'PyQt5.QtBluetooth',
    'PyQt5.QtMultimedia',
    'PyQt5.QtMultimediaWidgets',
    'PyQt5.QtNfc',
    'PyQt5.QtPositioning',
    'PyQt5.QtQml',
    'PyQt5.QtQuick',
    'PyQt5.QtQuickWidgets',
    'PyQt5.QtSensors',
    'PyQt5.QtSerialPort',
    'PyQt5.QtSql',
    'PyQt5.QtSvg',
    'PyQt5.QtTest',
    'PyQt5.QtTextToSpeech',
    'PyQt5.QtWebChannel',
    'PyQt5.QtWebEngine',
    'PyQt5.QtWebEngineCore',
    'PyQt5.QtWebEngineWidgets',
    'PyQt5.QtWebSockets',
    'PyQt5.QtWinExtras',
    'PyQt5.QtXmlPatterns',
    'PyQt5.QAxContainer',
    'PyQt5.QtDBus',
    'PyQt5.QtDesigner',
    'PyQt5.QtHelp',
]

# ==================== 主程序分析 ====================

a = Analysis(
    [os.path.join(work_dir, 'main_app.py')],
    pathex=[work_dir],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    # 关键：添加运行时修复脚本
    runtime_hooks=[os.path.join(work_dir, 'runtime_fix_win7.py')],
    excludes=excludes,
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# ==================== EXE配置（Win7优化）====================

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name=app_name,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,  # 关闭UPX压缩（某些Win7环境UPX有问题）
    console=False,
    icon=None,
    version=None,
)

# ==================== 收集文件 ====================

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name=f'{app_name}_Win7',
)
