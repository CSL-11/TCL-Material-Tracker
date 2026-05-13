# -*- coding: utf-8 -*-
"""
Windows 7 兼容性启动脚本
解决 cx_Freeze 打包后在 Win7 上可能出现的启动问题
"""

import sys
import os

# 设置环境变量，确保Win7兼容性
os.environ['PYTHONIOENCODING'] = 'utf-8'
os.environ['PYTHONUNBUFFERED'] = '1'

# 预导入关键模块，避免动态导入问题
try:
    import importlib
    import importlib.util
    
    # 确保基础模块可用
    if 'importlib' not in sys.modules:
        sys.modules['importlib'] = importlib
        
    if '_frozen_importlib' not in sys.modules:
        try:
            import _frozen_importlib
            sys.modules['_frozen_importlib'] = _frozen_importlib
        except ImportError:
            pass
            
except Exception as e:
    print(f"初始化警告: {e}", file=sys.stderr)

# 修复sys.meta_path
if not hasattr(sys, 'meta_path') or sys.meta_path is None:
    sys.meta_path = []

# 确保sys.path正确
if '' not in sys.path:
    sys.path.insert(0, '')

# 添加当前目录到路径
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# 导入并运行主程序
try:
    from main_app import TCLApplication
    from PyQt5.QtWidgets import QApplication
    import sys as qt_sys
    
    # 创建Qt应用
    app = QApplication(qt_sys.argv)
    
    # 创建主窗口
    window = TCLApplication()
    window.show()
    
    # 运行事件循环
    qt_sys.exit(app.exec_())
    
except Exception as e:
    import traceback
    error_msg = f"""程序启动失败！

错误信息: {str(e)}

详细错误:
{traceback.format_exc()}

请确保：
1. Windows 7 已安装所有更新
2. Visual C++ Redistributable 已安装
3. 以管理员身份运行此程序"""

    print(error_msg, file=sys.stderr)
    
    # 尝试显示错误对话框（如果PyQt5可用）
    try:
        from PyQt5.QtWidgets import QMessageBox, QApplication
        if not QApplication.instance():
            app = QApplication([])
        QMessageBox.critical(None, "启动错误", error_msg)
    except:
        pass
    
    sys.exit(1)