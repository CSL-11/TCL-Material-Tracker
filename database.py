import sqlite3
from datetime import datetime
import os

class DatabaseManager:
    def __init__(self, db_path=None):
        if db_path is None:
            # 数据库文件在 data/ 目录
            db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'TCL表格数据库.db')
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        self.connect()

    def connect(self):
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS 一级表格 (
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                序号 INTEGER,
                订单号 TEXT,
                物料号 TEXT NOT NULL,
                物料描述 TEXT,
                供方 TEXT,
                总缺料 INTEGER,
                采购组 INTEGER,
                采购组名称 TEXT,
                跟单 TEXT,
                供方在途量 INTEGER,
                已承诺量 INTEGER,
                销售订单 TEXT,
                销售订单行号 TEXT,
                内需单号 TEXT,
                送货日期 TEXT,
                分类 TEXT,
                创建时间 TEXT,
                UNIQUE(物料号, 订单号)
            )
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS 二级表格 (
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                一级ID INTEGER,
                物料号 TEXT NOT NULL,
                物料描述 TEXT,
                序号 INTEGER,
                订单号 TEXT,
                总缺料 INTEGER,
                分类 TEXT,
                下单时间 TEXT,
                FOREIGN KEY (一级ID) REFERENCES 一级表格(ID)
            )
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS 出货记录 (
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                物料号 TEXT NOT NULL,
                数量 INTEGER,
                出货日期 TEXT,
                订单号 TEXT,
                创建时间 TEXT
            )
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS 表头配置 (
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                表格类型 TEXT,
                列名 TEXT,
                列顺序 INTEGER,
                显示名称 TEXT
            )
        ''')

        self.conn.commit()

    def insert_or_update_level1(self, data_list):
        for data in data_list:
            self.cursor.execute('''
                INSERT OR REPLACE INTO 一级表格 (
                    序号, 订单号, 物料号, 物料描述, 供方, 总缺料,
                    采购组, 采购组名称, 跟单, 供方在途量, 已承诺量,
                    销售订单, 销售订单行号, 内需单号, 送货日期, 分类, 创建时间
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                data.get('序号'), data.get('订单号'), data.get('物料号'),
                data.get('物料描述'), data.get('供方'), data.get('总缺料'),
                data.get('采购组'), data.get('采购组名称'), data.get('跟单'),
                data.get('供方在途量'), data.get('已承诺量'),
                data.get('销售订单'), data.get('销售订单行号'),
                data.get('内需单号'), data.get('送货日期'),
                data.get('分类'), datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            ))
        self.conn.commit()

    def insert_level2(self, data_list):
        for data in data_list:
            self.cursor.execute('''
                INSERT INTO 二级表格 (
                    一级ID, 物料号, 物料描述, 序号, 订单号, 总缺料, 分类, 下单时间
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                data.get('一级ID'), data.get('物料号'), data.get('物料描述'),
                data.get('序号'), data.get('订单号'), data.get('总缺料'),
                data.get('分类'), data.get('下单时间')
            ))
        self.conn.commit()

    def insert_shipment(self, data_list):
        for data in data_list:
            self.cursor.execute('''
                INSERT INTO 出货记录 (物料号, 数量, 出货日期, 订单号, 创建时间)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                data.get('物料号'), data.get('数量'), data.get('出货日期'),
                data.get('订单号'), datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            ))
        self.conn.commit()

    def get_level1_all(self):
        self.cursor.execute('SELECT * FROM 一级表格 ORDER BY ID')
        return [dict(row) for row in self.cursor.fetchall()]

    def get_level2_all(self):
        self.cursor.execute('SELECT * FROM 二级表格 ORDER BY ID')
        return [dict(row) for row in self.cursor.fetchall()]

    def get_shipments(self):
        self.cursor.execute('SELECT * FROM 出货记录 ORDER BY ID DESC')
        return [dict(row) for row in self.cursor.fetchall()]

    def delete_shipment(self, material_number):
        self.cursor.execute('DELETE FROM 出货记录 WHERE 物料号 = ?', (material_number,))
        self.conn.commit()

    def search_by_material_number(self, material_number):
        self.cursor.execute('''
            SELECT * FROM 一级表格 WHERE 物料号 = ?
        ''', (material_number,))
        return [dict(row) for row in self.cursor.fetchall()]

    def get_by_category(self, category):
        self.cursor.execute('SELECT * FROM 一级表格 WHERE 分类 = ?', (category,))
        return [dict(row) for row in self.cursor.fetchall()]

    def update_sequence_order(self, material_number, sequence, order_number):
        self.cursor.execute('''
            UPDATE 一级表格 SET 序号 = ?, 订单号 = ? WHERE 物料号 = ?
        ''', (sequence, order_number, material_number))
        self.conn.commit()

    def close(self):
        if self.conn:
            self.conn.close()