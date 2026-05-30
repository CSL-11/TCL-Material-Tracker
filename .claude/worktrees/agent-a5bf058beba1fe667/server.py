# -*- coding: utf-8 -*-
"""
TCL表格比对系统 - 服务器端 (Flask RESTful API)
局域网版本 - 为所有客户端提供数据存储和同步服务

启动方式:
    python server.py
    或指定端口:
    python server.py --port 8080

客户端连接:
    在客户端设置服务器IP地址即可（默认: http://服务器IP:5000）
"""

import os
import sys
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from datetime import datetime
import argparse

# 导入数据库管理模块
from server_db import ServerDatabase

app = Flask(__name__)
CORS(app)  # 允许跨域请求

# 初始化数据库
db = ServerDatabase('tcl_server_data.db')

# ==================== 基础API ====================

@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查 - 用于测试服务器是否可用"""
    return jsonify({
        'status': 'ok',
        'server': 'TCL表格比对系统服务器',
        'version': '1.0.0',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/stats', methods=['GET'])
def get_statistics():
    """获取服务器统计信息"""
    stats = db.get_statistics()
    stats['connected_clients'] = len(app.config.get('clients', []))
    return jsonify(stats)

# ==================== 数据库管理 API ====================

@app.route('/api/db/data', methods=['GET', 'POST', 'DELETE'])
def handle_db_data():
    """
    数据库管理数据的CRUD操作

    GET  - 获取所有数据
    POST - 保存数据 (JSON: {headers: [], data: []})
    DELETE - 清空数据
    """
    if request.method == 'GET':
        headers, data = db.load_db_data()
        return jsonify({
            'success': True,
            'headers': headers,
            'data': data,
            'count': len(data)
        })

    elif request.method == 'POST':
        try:
            data = request.json
            headers = data.get('headers', [])
            rows = data.get('data', [])

            db.save_db_data(headers, rows)

            # 记录操作日志
            client_id = request.headers.get('X-Client-ID', 'unknown')
            db.add_operation_log(client_id, '保存数据库数据', f'保存了 {len(rows)} 条记录')

            return jsonify({
                'success': True,
                'message': f'成功保存 {len(rows)} 条记录'
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    elif request.method == 'DELETE':
        try:
            data = request.json or {}
            item_ids = data.get('ids')  # 可选：删除指定的ID列表

            db.delete_db_data(item_ids)

            client_id = request.headers.get('X-Client-ID', 'unknown')
            db.add_operation_log(client_id, '删除数据库数据', f'删除了 {len(item_ids) if item_ids else "全部"} 条记录')

            return jsonify({
                'success': True,
                'message': '删除成功'
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

# ==================== 批量导入 API ====================

@app.route('/api/batch/data', methods=['GET', 'POST', 'DELETE'])
def handle_batch_data():
    """
    批量导入数据的CRUD操作

    GET  - 获取批量导入的数据
    POST - 保存批量导入的数据
    DELETE - 删除数据（支持部分删除）
    """
    if request.method == 'GET':
        headers, data = db.load_batch_import_data()
        return jsonify({
            'success': True,
            'headers': headers,
            'data': data,
            'count': len(data)
        })

    elif request.method == 'POST':
        try:
            data = request.json
            headers = data.get('headers', [])
            rows = data.get('data', [])

            db.save_batch_import_data(headers, rows)

            client_id = request.headers.get('X-Client-ID', 'unknown')
            db.add_operation_log(client_id, '保存批量导入数据', f'保存了 {len(rows)} 条记录')

            return jsonify({
                'success': True,
                'message': f'成功保存 {len(rows)} 条记录'
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    elif request.method == 'DELETE':
        try:
            data = request.json or {}
            indices = data.get('indices')  # 可选：删除指定的索引列表

            db.delete_batch_import_items(indices)

            client_id = request.headers.get('X-Client-ID', 'unknown')
            db.add_operation_log(client_id, '删除批量导入数据', f'删除了 {len(indices) if indices else "全部"} 条记录')

            return jsonify({
                'success': True,
                'message': '删除成功'
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

# ==================== 配置管理 API ====================

@app.route('/api/config/<key>', methods=['GET', 'POST'])
def handle_config(key):
    """
    配置项的读写操作

    GET  - 获取配置值
    POST - 设置配置值
    """
    if request.method == 'GET':
        value = db.load_config(key)
        return jsonify({
            'success': True,
            'key': key,
            'value': value
        })

    elif request.method == 'POST':
        try:
            value = request.json.get('value')
            db.save_config(key, value)

            return jsonify({
                'success': True,
                'message': f'配置 [{key}] 已更新'
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

@app.route('/api/config/all', methods=['GET'])
def get_all_config():
    """获取所有配置"""
    config = db.load_all_config()
    return jsonify({
        'success': True,
        'config': config
    })

# ==================== 日志 API ====================

@app.route('/api/logs', methods=['GET'])
def get_logs():
    """获取操作日志"""
    limit = request.args.get('limit', 100, type=int)
    logs = db.get_operation_logs(limit)
    return jsonify({
        'success': True,
        'logs': logs,
        'count': len(logs)
    })

# ==================== 文件上传/下载 API ====================

@app.route('/api/file/upload', methods=['POST'])
def upload_file():
    """
    上传Excel文件到服务器

    使用方式：
    - multipart/form-data
    - 字段名: file
    """
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': '没有文件'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'error': '未选择文件'}), 400

    try:
        # 创建上传目录
        upload_dir = os.path.join(os.path.dirname(__file__), 'uploads')
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)

        # 保存文件（使用时间戳避免重名）
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        filename = f"{timestamp}_{file.filename}"
        filepath = os.path.join(upload_dir, filename)
        file.save(filepath)

        client_id = request.headers.get('X-Client-ID', 'unknown')
        db.add_operation_log(client_id, '上传文件', file.filename)

        return jsonify({
            'success': True,
            'message': '文件上传成功',
            'filename': filename,
            'filepath': filepath
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/file/download/<filename>', methods=['GET'])
def download_file(filename):
    """下载文件"""
    upload_dir = os.path.join(os.path.dirname(__file__), 'uploads')
    filepath = os.path.join(upload_dir, filename)

    if not os.path.exists(filepath):
        return jsonify({'success': False, 'error': '文件不存在'}), 404

    return send_file(filepath, as_attachment=True)


# ==================== 错误处理 ====================

@app.errorhandler(404)
def not_found(error):
    return jsonify({'success': False, 'error': 'API不存在'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'success': False, 'error': '服务器内部错误'}), 500


# ==================== 启动服务器 ====================

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='TCL表格比对系统 - 局域网服务器')
    parser.add_argument('--host', default='0.0.0.0', help='监听地址 (默认: 0.0.0.0)')
    parser.add_argument('--port', type=int, default=5000, help='端口号 (默认: 5000)')
    parser.add_argument('--debug', action='store_true', help='调试模式')
    args = parser.parse_args()

    print("=" * 60)
    print("  TCL表格比对系统 - 局域网服务器")
    print("=" * 60)
    print(f"  监听地址: {args.host}:{args.port}")
    print(f"  数据库文件: tcl_server_data.db")
    print(f"  启动时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    print("\n  客户端连接说明:")
    print(f"  1. 确保服务器电脑的防火墙允许端口 {args.port}")
    print(f"  2. 在客户端输入服务器IP: http://服务器IP:{args.port}")
    print(f"  3. 测试连接: http://localhost:{args.port}/api/health")
    print("\n" + "=" * 60 + "\n")

    app.run(
        host=args.host,
        port=args.port,
        debug=args.debug
    )
