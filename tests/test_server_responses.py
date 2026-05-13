# -*- coding: utf-8 -*-
import os
import shutil
import tempfile
import unittest

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
SERVER_IMPORT_DIR = tempfile.mkdtemp()
ORIGINAL_CWD = os.getcwd()
os.chdir(SERVER_IMPORT_DIR)

try:
    from server import (
        delete_batch_data_response,
        delete_db_data_response,
        get_batch_data_response,
        get_config_response,
        get_db_data_response,
        save_batch_data_response,
        save_config_response,
        save_db_data_response,
    )
finally:
    os.chdir(ORIGINAL_CWD)
    shutil.rmtree(SERVER_IMPORT_DIR)


class FakeServerDatabase:
    def __init__(self):
        self.db_headers = []
        self.db_data = []
        self.batch_headers = []
        self.batch_data = []
        self.config = {}
        self.logs = []

    def load_db_data(self):
        return self.db_headers, self.db_data

    def save_db_data(self, headers, data):
        self.db_headers = headers
        self.db_data = data

    def delete_db_data(self, item_ids=None):
        if item_ids:
            self.db_data = [row for idx, row in enumerate(self.db_data) if idx not in item_ids]
        else:
            self.db_data = []

    def load_batch_import_data(self):
        return self.batch_headers, self.batch_data

    def save_batch_import_data(self, headers, data):
        self.batch_headers = headers
        self.batch_data = data

    def delete_batch_import_items(self, indices=None):
        if indices:
            self.batch_data = [row for idx, row in enumerate(self.batch_data) if idx not in indices]
        else:
            self.batch_data = []

    def save_config(self, key, value):
        self.config[key] = value

    def load_config(self, key):
        return self.config.get(key)

    def add_operation_log(self, client_id, operation, details):
        self.logs.append((client_id, operation, details))


class ServerResponseTests(unittest.TestCase):
    def setUp(self):
        self.database = FakeServerDatabase()

    def test_db_data_responses_keep_shape(self):
        payload = {'headers': ['物料号'], 'data': [{'物料号': 'A001'}]}

        save_response = save_db_data_response(self.database, payload, 'client-a')
        get_response = get_db_data_response(self.database)

        self.assertEqual({'success': True, 'message': '成功保存 1 条记录'}, save_response)
        self.assertEqual(True, get_response['success'])
        self.assertEqual(['物料号'], get_response['headers'])
        self.assertEqual([{'物料号': 'A001'}], get_response['data'])
        self.assertEqual(1, get_response['count'])
        self.assertEqual(('client-a', '保存数据库数据', '保存了 1 条记录'), self.database.logs[-1])

    def test_db_delete_response_supports_partial_delete(self):
        self.database.db_headers = ['物料号']
        self.database.db_data = [{'物料号': 'A001'}, {'物料号': 'A002'}]

        response = delete_db_data_response(self.database, {'ids': [0]}, 'client-a')

        self.assertEqual({'success': True, 'message': '删除成功'}, response)
        self.assertEqual([{'物料号': 'A002'}], self.database.db_data)
        self.assertEqual(('client-a', '删除数据库数据', '删除了 1 条记录'), self.database.logs[-1])

    def test_batch_data_responses_keep_shape(self):
        payload = {'headers': ['订单名称'], 'data': [{'订单名称': '订单1'}]}

        save_response = save_batch_data_response(self.database, payload, 'client-b')
        get_response = get_batch_data_response(self.database)

        self.assertEqual({'success': True, 'message': '成功保存 1 条记录'}, save_response)
        self.assertEqual(True, get_response['success'])
        self.assertEqual(['订单名称'], get_response['headers'])
        self.assertEqual([{'订单名称': '订单1'}], get_response['data'])
        self.assertEqual(1, get_response['count'])
        self.assertEqual(('client-b', '保存批量导入数据', '保存了 1 条记录'), self.database.logs[-1])

    def test_batch_delete_response_supports_partial_delete(self):
        self.database.batch_headers = ['订单名称']
        self.database.batch_data = [{'订单名称': '订单1'}, {'订单名称': '订单2'}]

        response = delete_batch_data_response(self.database, {'indices': [1]}, 'client-b')

        self.assertEqual({'success': True, 'message': '删除成功'}, response)
        self.assertEqual([{'订单名称': '订单1'}], self.database.batch_data)
        self.assertEqual(('client-b', '删除批量导入数据', '删除了 1 条记录'), self.database.logs[-1])

    def test_config_responses_keep_shape(self):
        save_response = save_config_response(self.database, 'output_dir', {'value': 'D:/out'})
        get_response = get_config_response(self.database, 'output_dir')

        self.assertEqual({'success': True, 'message': '配置 [output_dir] 已更新'}, save_response)
        self.assertEqual({'success': True, 'key': 'output_dir', 'value': 'D:/out'}, get_response)


if __name__ == '__main__':
    unittest.main()
