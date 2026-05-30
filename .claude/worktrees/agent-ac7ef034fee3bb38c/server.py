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
import json
import hashlib
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from datetime import datetime
import argparse

# 导入数据库管理模块
from server_db import ServerDatabase
from version import __version__

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
        'version': __version__,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/stats', methods=['GET'])
def get_statistics():
    """获取服务器统计信息"""
    stats = db.get_statistics()
    stats['connected_clients'] = len(app.config.get('clients', []))
    return jsonify(stats)

# ==================== 数据库管理 API ====================

def get_db_data_response(database):
    headers, data = database.load_db_data()
    return {
        'success': True,
        'headers': headers,
        'data': data,
        'count': len(data)
    }


def save_db_data_response(database, payload, client_id):
    payload = payload or {}
    headers = payload.get('headers', [])
    rows = payload.get('data', [])
    database.save_db_data(headers, rows)
    database.add_operation_log(client_id, '保存数据库数据', f'保存了 {len(rows)} 条记录')
    return {
        'success': True,
        'message': f'成功保存 {len(rows)} 条记录'
    }


def delete_db_data_response(database, payload, client_id):
    payload = payload or {}
    item_ids = payload.get('ids')
    database.delete_db_data(item_ids)
    database.add_operation_log(client_id, '删除数据库数据', f'删除了 {len(item_ids) if item_ids else "全部"} 条记录')
    return {
        'success': True,
        'message': '删除成功'
    }


@app.route('/api/db/data', methods=['GET', 'POST', 'DELETE'])
def handle_db_data():
    """
    数据库管理数据的CRUD操作

    GET  - 获取所有数据
    POST - 保存数据 (JSON: {headers: [], data: []})
    DELETE - 清空数据
    """
    if request.method == 'GET':
        return jsonify(get_db_data_response(db))

    elif request.method == 'POST':
        try:
            client_id = request.headers.get('X-Client-ID', 'unknown')
            return jsonify(save_db_data_response(db, request.json, client_id))
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    elif request.method == 'DELETE':
        try:
            client_id = request.headers.get('X-Client-ID', 'unknown')
            return jsonify(delete_db_data_response(db, request.json, client_id))
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

# ==================== 批量导入 API ====================

def get_batch_data_response(database):
    headers, data = database.load_batch_import_data()
    return {
        'success': True,
        'headers': headers,
        'data': data,
        'count': len(data)
    }


def save_batch_data_response(database, payload, client_id):
    payload = payload or {}
    headers = payload.get('headers', [])
    rows = payload.get('data', [])
    database.save_batch_import_data(headers, rows)
    database.add_operation_log(client_id, '保存批量导入数据', f'保存了 {len(rows)} 条记录')
    return {
        'success': True,
        'message': f'成功保存 {len(rows)} 条记录'
    }


def delete_batch_data_response(database, payload, client_id):
    payload = payload or {}
    indices = payload.get('indices')
    database.delete_batch_import_items(indices)
    database.add_operation_log(client_id, '删除批量导入数据', f'删除了 {len(indices) if indices else "全部"} 条记录')
    return {
        'success': True,
        'message': '删除成功'
    }


@app.route('/api/batch/data', methods=['GET', 'POST', 'DELETE'])
def handle_batch_data():
    """
    批量导入数据的CRUD操作

    GET  - 获取批量导入的数据
    POST - 保存批量导入的数据
    DELETE - 删除数据（支持部分删除）
    """
    if request.method == 'GET':
        return jsonify(get_batch_data_response(db))

    elif request.method == 'POST':
        try:
            client_id = request.headers.get('X-Client-ID', 'unknown')
            return jsonify(save_batch_data_response(db, request.json, client_id))
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    elif request.method == 'DELETE':
        try:
            client_id = request.headers.get('X-Client-ID', 'unknown')
            return jsonify(delete_batch_data_response(db, request.json, client_id))
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

# ==================== 配置管理 API ====================

def get_config_response(database, key):
    value = database.load_config(key)
    return {
        'success': True,
        'key': key,
        'value': value
    }


def save_config_response(database, key, payload):
    payload = payload or {}
    value = payload.get('value')
    database.save_config(key, value)
    return {
        'success': True,
        'message': f'配置 [{key}] 已更新'
    }


@app.route('/api/config/<key>', methods=['GET', 'POST'])
def handle_config(key):
    """
    配置项的读写操作

    GET  - 获取配置值
    POST - 设置配置值
    """
    if request.method == 'GET':
        return jsonify(get_config_response(db, key))

    elif request.method == 'POST':
        try:
            return jsonify(save_config_response(db, key, request.json))
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


# ==================== 自动更新 API ====================

def _parse_version(v):
    """解析版本号字符串为元组，用于比较"""
    try:
        return tuple(map(int, v.split('.')))
    except (ValueError, AttributeError):
        return (0, 0, 0)

def _get_updates_dir():
    """获取更新包目录"""
    updates_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'updates')
    if not os.path.exists(updates_dir):
        os.makedirs(updates_dir)
    return updates_dir

def _load_manifest():
    """加载更新清单"""
    manifest_path = os.path.join(_get_updates_dir(), 'manifest.json')
    if os.path.exists(manifest_path):
        with open(manifest_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {'versions': []}

@app.route('/api/update/check', methods=['GET'])
def check_update():
    """
    检查是否有新版本

    参数: current_version - 客户端当前版本号
    响应: {
        has_update: bool,
        latest_version: str,
        update_url: str,
        changelog: str,
        file_size: int
    }
    """
    current_version = request.args.get('current_version', '0.0.0')
    manifest = _load_manifest()
    versions = manifest.get('versions', [])

    if not versions:
        return jsonify({
            'has_update': False,
            'latest_version': current_version,
            'message': '暂无更新'
        })

    # 获取最新版本
    latest = max(versions, key=lambda v: _parse_version(v.get('version', '0.0.0')))
    latest_version = latest.get('version', '0.0.0')

    # 比较版本
    if _parse_version(latest_version) > _parse_version(current_version):
        update_file = latest.get('filename', f'update_{latest_version}.zip')
        update_path = os.path.join(_get_updates_dir(), update_file)
        file_size = os.path.getsize(update_path) if os.path.exists(update_path) else 0

        return jsonify({
            'has_update': True,
            'latest_version': latest_version,
            'update_url': f'/api/update/download/{latest_version}',
            'changelog': latest.get('changelog', ''),
            'file_size': file_size,
            'files': latest.get('files', [])
        })

    return jsonify({
        'has_update': False,
        'latest_version': current_version,
        'message': '已是最新版本'
    })

@app.route('/api/update/download/<version>', methods=['GET'])
def download_update(version):
    """下载指定版本的更新包"""
    manifest = _load_manifest()
    versions = manifest.get('versions', [])

    # 查找对应版本
    target = None
    for v in versions:
        if v.get('version') == version:
            target = v
            break

    if not target:
        return jsonify({'success': False, 'error': f'版本 {version} 不存在'}), 404

    update_file = target.get('filename', f'update_{version}.zip')
    update_path = os.path.join(_get_updates_dir(), update_file)

    if not os.path.exists(update_path):
        return jsonify({'success': False, 'error': '更新包文件不存在'}), 404

    return send_file(update_path, as_attachment=True, download_name=f'update_{version}.zip')

@app.route('/api/sync/check', methods=['GET'])
def sync_check():
    """轻量级同步检查 - 返回数据变更时间戳，客户端用于检测是否需要刷新"""
    stats = db.get_statistics()
    return jsonify({
        'last_db_update': stats.get('last_db_update', '从未'),
        'db_data_count': stats.get('db_data_count', 0),
        'batch_import_count': stats.get('batch_import_count', 0),
    })


@app.route('/api/update/changelog', methods=['GET'])
def get_changelog():
    """获取更新日志"""
    manifest = _load_manifest()
    versions = manifest.get('versions', [])

    # 按版本号降序排列
    sorted_versions = sorted(versions, key=lambda v: _parse_version(v.get('version', '0.0.0')), reverse=True)

    return jsonify({
        'success': True,
        'changelog': [{
            'version': v.get('version'),
            'date': v.get('date'),
            'changelog': v.get('changelog'),
            'files': v.get('files', [])
        } for v in sorted_versions]
    })


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
