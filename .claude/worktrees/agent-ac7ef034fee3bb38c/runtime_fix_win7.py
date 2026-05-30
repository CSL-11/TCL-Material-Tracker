# -*- coding: utf-8 -*-
"""
运行时修复脚本 - 解决Windows 7上的 pyimod02_importers 错误
在PyInstaller打包的程序启动前执行，修复导入系统初始化问题

使用方法:
    在spec文件中通过 runtime_hooks 参数引用此文件:
    runtime_hooks=['runtime_fix_win7.py']
"""

import sys
import os

# 修复1: 确保sys.meta_path正确初始化
if not hasattr(sys, 'meta_path') or sys.meta_path is None:
    sys.meta_path = []

# 修复2: 确保sys.path正确设置（Win7路径问题）
if sys.path and len(sys.path) > 0:
    # 移除空路径和重复路径
    seen = set()
    clean_path = []
    for p in sys.path:
        if p and p not in seen:
            clean_path.append(p)
            seen.add(p)
    sys.path = clean_path

# 修复3: 预加载关键模块（防止NULL模块错误）
try:
    # 强制导入基础模块
    import importlib
    import importlib.abc
    import importlib.machinery

    # 确保这些模块在sys.modules中
    if 'importlib' not in sys.modules:
        __import__('importlib')
    if 'importlib.abc' not in sys.modules:
        __import__('importlib.abc')
    if 'importlib.machinery' not in sys.modules:
        __import__('importlib.machinery')

except Exception as e:
    # 忽略导入错误，让程序继续启动
    pass

# 修复4: 设置正确的编码（Win7中文支持）
if sys.version_info[0] == 3:
    try:
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except:
        pass

# 修复5: 添加当前目录到path（确保数据文件可访问）
try:
    if '' not in sys.path:
        sys.path.insert(0, '')
    
    # 获取程序所在目录并添加到path
    if getattr(sys, 'frozen', False):
        # PyInstaller打包后的路径
        app_dir = os.path.dirname(sys.executable)
        if app_dir not in sys.path:
            sys.path.insert(0, app_dir)
        
        # _internal目录
        internal_dir = os.path.join(app_dir, '_internal')
        if os.path.exists(internal_dir) and internal_dir not in sys.path:
            sys.path.insert(0, internal_dir)
except:
    pass

# 修复6: 初始化site模块（某些Win7环境缺少）
try:
    import site
    if hasattr(site, 'main'):
        site.main()  # 完整初始化site
except:
    try:
        import site
        # 基础site初始化
        if hasattr(site, 'getsitepackages'):
            site.getsitepackages()
    except:
        pass

print("[OK] Win7运行时修复完成")
