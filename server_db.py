# -*- coding: utf-8 -*-
"""
TCL表格比对系统 - 服务器端数据库管理模块
使用SQLite数据库存储所有数据，替代原来的JSON文件存储
"""

import sqlite3
import json
import os
import sys
from datetime import datetime

class ServerDatabase:
    def __init__(self, db_path=None):
        if db_path is None:
            # 数据库文件在 data/ 目录
            db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'tcl_server_data.db')
        # 直接使用传入的路径，如果是绝对路径则直接使用
        # 如果是相对路径，则基于当前工作目录解析
        elif not os.path.isabs(db_path):
            db_path = os.path.join(os.getcwd(), db_path)
        self.db_path = db_path

        # 检查数据库文件是否有效
        if os.path.exists(db_path):
            if not self._validate_database():
                # 数据库损坏，删除重建
                try:
                    os.remove(db_path)
                    print(f"[WARN] 数据库文件已损坏，已删除并重建: {db_path}")
                except Exception as e:
                    print(f"[ERROR] 无法删除损坏的数据库: {e}")

        self.init_database()

    def _validate_database(self):
        """验证数据库文件是否有效"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            cursor.fetchone()
            conn.close()
            return True
        except Exception:
            return False

    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_database(self):
        """初始化数据库表结构"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # 1. 数据库管理表（原db_cache.json）
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS db_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                headers TEXT NOT NULL,
                data_json TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # 2. 批量导入数据表（原batch_import_cache.json）
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS batch_import_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                headers TEXT NOT NULL,
                data_json TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # 3. 出货数据表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS shipment_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_name TEXT,
                data_json TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # 4. 配置表（原output_dir_config.json等）
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS config (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # 5. 操作日志表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS operation_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_id TEXT,
                operation TEXT NOT NULL,
                details TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        conn.commit()
        conn.close()
        print(f"[OK] 数据库初始化完成: {self.db_path}")

    # ========== 数据库管理功能 ==========

    def save_db_data(self, headers, data):
        """保存数据库管理页面的数据"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # 删除旧数据
        cursor.execute('DELETE FROM db_data')

        # 插入新数据
        cursor.execute('''
            INSERT INTO db_data (headers, data_json)
            VALUES (?, ?)
        ''', (json.dumps(headers, ensure_ascii=False), json.dumps(data, ensure_ascii=False)))

        conn.commit()
        conn.close()
        print(f"[OK] 已保存数据库管理数据: {len(data)} 条记录")

    def load_db_data(self):
        """加载数据库管理页面的数据"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT headers, data_json FROM db_data ORDER BY id DESC LIMIT 1')
        row = cursor.fetchone()

        conn.close()

        if row:
            headers = json.loads(row['headers'])
            data = json.loads(row['data_json'])
            return headers, data
        else:
            return [], []

    def delete_db_data(self, item_ids=None):
        """删除数据库管理数据"""
        conn = self.get_connection()
        cursor = conn.cursor()

        if item_ids:
            # 删除指定ID的数据
            headers, data = self.load_db_data()
            data = [row for idx, row in enumerate(data) if idx not in item_ids]
            if data:
                self.save_db_data(headers, data)
        else:
            # 清空所有数据
            cursor.execute('DELETE FROM db_data')
            conn.commit()

        conn.close()

    # ========== 批量导入功能 ==========

    def save_batch_import_data(self, headers, data):
        """保存批量导入的数据"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('DELETE FROM batch_import_data')

        cursor.execute('''
            INSERT INTO batch_import_data (headers, data_json)
            VALUES (?, ?)
        ''', (json.dumps(headers, ensure_ascii=False), json.dumps(data, ensure_ascii=False)))

        conn.commit()
        conn.close()
        print(f"[OK] 已保存批量导入数据: {len(data)} 条记录")

    def load_batch_import_data(self):
        """加载批量导入的数据"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT headers, data_json FROM batch_import_data ORDER BY id DESC LIMIT 1')
        row = cursor.fetchone()

        conn.close()

        if row:
            headers = json.loads(row['headers'])
            data = json.loads(row['data_json'])
            return headers, data
        else:
            return [], []

    def delete_batch_import_items(self, indices=None):
        """删除批量导入的指定项"""
        if indices is None:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('DELETE FROM batch_import_data')
            conn.commit()
            conn.close()
            return

        headers, data = self.load_batch_import_data()
        data = [row for idx, row in enumerate(data) if idx not in indices]
        self.save_batch_import_data(headers, data)

    # ========== 配置管理 ==========

    def save_config(self, key, value):
        """保存配置项"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT OR REPLACE INTO config (key, value, updated_at)
            VALUES (?, ?, ?)
        ''', (key, str(value), datetime.now().isoformat()))

        conn.commit()
        conn.close()

    def load_config(self, key, default=None):
        """加载配置项"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT value FROM config WHERE key = ?', (key,))
        row = cursor.fetchone()

        conn.close()

        if row:
            try:
                return json.loads(row['value'])
            except:
                return row['value']
        else:
            return default

    def load_all_config(self):
        """加载所有配置"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT key, value FROM config')
        rows = cursor.fetchall()

        conn.close()

        config = {}
        for row in rows:
            try:
                config[row['key']] = json.loads(row['value'])
            except:
                config[row['key']] = row['value']

        return config

    # ========== 备份恢复功能 ==========

    def backup_database(self, backup_dir=None):
        """备份数据库到指定目录，返回备份文件路径"""
        import shutil
        if backup_dir is None:
            backup_dir = os.path.join(os.path.dirname(self.db_path), 'backups')
        os.makedirs(backup_dir, exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = os.path.join(backup_dir, f'tcl_server_backup_{timestamp}.db')
        shutil.copy2(self.db_path, backup_path)
        return backup_path

    def restore_database(self, backup_path):
        """从备份文件恢复数据库"""
        import shutil
        if not os.path.exists(backup_path):
            raise FileNotFoundError(f"备份文件不存在: {backup_path}")
        shutil.copy2(backup_path, self.db_path)

    def list_backups(self, backup_dir=None):
        """列出所有备份文件"""
        if backup_dir is None:
            backup_dir = os.path.join(os.path.dirname(self.db_path), 'backups')
        if not os.path.exists(backup_dir):
            return []
        backups = []
        for f in os.listdir(backup_dir):
            if f.endswith('.db') and f.startswith('tcl_server_backup_'):
                path = os.path.join(backup_dir, f)
                backups.append({
                    'filename': f,
                    'path': path,
                    'size': os.path.getsize(path),
                    'created': datetime.fromtimestamp(os.path.getctime(path)).isoformat()
                })
        return sorted(backups, key=lambda x: x['created'], reverse=True)

    # ========== 日志功能 ==========

    def add_operation_log(self, client_id, operation, details=""):
        """添加操作日志"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO operation_log (client_id, operation, details)
            VALUES (?, ?, ?)
        ''', (client_id, operation, details))

        conn.commit()
        conn.close()

    def get_operation_logs(self, limit=100):
        """获取操作日志"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT * FROM operation_log
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (limit,))

        logs = [dict(row) for row in cursor.fetchall()]
        conn.close()

        return logs

    # ========== 统计信息 ==========

    def get_statistics(self):
        """获取数据库统计信息"""
        conn = self.get_connection()
        cursor = conn.cursor()

        stats = {}

        # 数据库管理数据量
        cursor.execute('SELECT data_json FROM db_data LIMIT 1')
        row = cursor.fetchone()
        if row:
            data = json.loads(row['data_json'])
            stats['db_data_count'] = len(data)
        else:
            stats['db_data_count'] = 0

        # 批量导入数据量
        cursor.execute('SELECT data_json FROM batch_import_data LIMIT 1')
        row = cursor.fetchone()
        if row:
            data = json.loads(row['data_json'])
            stats['batch_import_count'] = len(data)
        else:
            stats['batch_import_count'] = 0

        # 操作日志数量
        cursor.execute('SELECT COUNT(*) as count FROM operation_log')
        row = cursor.fetchone()
        stats['log_count'] = row['count']

        # 最后更新时间
        cursor.execute('SELECT MAX(updated_at) as last_update FROM db_data')
        row = cursor.fetchone()
        stats['last_db_update'] = row['last_update'] or '从未'

        conn.close()

        return stats


# 测试代码
if __name__ == "__main__":
    db = ServerDatabase("test_server.db")

    # 测试保存和加载
    test_headers = ["物料号", "物料描述", "总缺料"]
    test_data = [
        {"物料号": "MAT001", "物料描述": "测试物料", "总缺料": 100},
        {"物料号": "MAT002", "物料描述": "测试物料2", "总缺料": 200}
    ]

    print("\n测试数据库管理功能...")
    db.save_db_data(test_headers, test_data)
    h, d = db.load_db_data()
    print(f"加载成功: {len(d)} 条记录")

    # 测试配置
    print("\n测试配置功能...")
    db.save_config("output_dir", "C:/test")
    val = db.load_config("output_dir")
    print(f"配置值: {val}")

    # 测试统计
    print("\n统计信息:")
    stats = db.get_statistics()
    for k, v in stats.items():
        print(f"  {k}: {v}")

    # 清理测试文件
    os.remove("test_server.db")
    print("\n[OK] 所有测试通过！")
