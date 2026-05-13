# -*- coding: utf-8 -*-
import unittest

from PyQt5.QtWidgets import QApplication, QMessageBox

from main_app import TCLApplication


class FakeNetwork:
    def __init__(self):
        self.is_server_mode = False
        self.saved_db = None
        self.saved_batch = None
        self.db_load_result = (['server_header'], [{'source': 'server'}], None)
        self.batch_load_result = (['server_batch_header'], [{'source': 'server_batch'}], None)
        self.save_success = True
        self.save_message = '保存成功'

    def save_db_data(self, headers, data):
        self.saved_db = (headers, data)
        return self.save_success, self.save_message

    def load_db_data(self):
        return self.db_load_result

    def save_batch_import_data(self, headers, data):
        self.saved_batch = (headers, data)
        return self.save_success, self.save_message

    def load_batch_import_data(self):
        return self.batch_load_result


class PersistenceModeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.window = TCLApplication.__new__(TCLApplication)
        self.window.network = FakeNetwork()
        self.window.local_db_saved = None
        self.window.local_batch_saved = None
        self.warnings = []
        self.original_warning = QMessageBox.warning
        QMessageBox.warning = self.capture_warning

    def tearDown(self):
        QMessageBox.warning = self.original_warning

    def capture_warning(self, parent, title, message):
        self.warnings.append((title, message))
        return QMessageBox.Ok

    def local_save_db(self, headers, data):
        self.window.local_db_saved = (headers, data)

    def local_load_db(self):
        return ['local_header'], [{'source': 'local'}]

    def local_save_batch(self, headers, data):
        self.window.local_batch_saved = (headers, data)

    def local_load_batch(self):
        return ['local_batch_header'], [{'source': 'local_batch'}]

    def test_local_mode_uses_local_db_methods(self):
        self.window._save_db_data_local = self.local_save_db
        self.window._load_db_data_local = self.local_load_db

        self.window.save_db_data_with_mode(['h'], [{'v': 1}])
        headers, data = self.window.load_db_data_with_mode()

        self.assertEqual((['h'], [{'v': 1}]), self.window.local_db_saved)
        self.assertIsNone(self.window.network.saved_db)
        self.assertEqual(['local_header'], headers)
        self.assertEqual([{'source': 'local'}], data)
        self.assertEqual([], self.warnings)

    def test_server_mode_uses_server_db_methods(self):
        self.window.network.is_server_mode = True
        self.window._save_db_data_local = self.local_save_db
        self.window._load_db_data_local = self.local_load_db

        self.window.save_db_data_with_mode(['h'], [{'v': 1}])
        headers, data = self.window.load_db_data_with_mode()

        self.assertEqual((['h'], [{'v': 1}]), self.window.network.saved_db)
        self.assertIsNone(self.window.local_db_saved)
        self.assertEqual(['server_header'], headers)
        self.assertEqual([{'source': 'server'}], data)
        self.assertEqual([], self.warnings)

    def test_server_failure_falls_back_to_local_db_methods(self):
        self.window.network.is_server_mode = True
        self.window.network.save_success = False
        self.window.network.save_message = '网络错误'
        self.window.network.db_load_result = (None, None, '加载失败')
        self.window._save_db_data_local = self.local_save_db
        self.window._load_db_data_local = self.local_load_db

        self.window.save_db_data_with_mode(['h'], [{'v': 1}])
        headers, data = self.window.load_db_data_with_mode()

        self.assertEqual((['h'], [{'v': 1}]), self.window.local_db_saved)
        self.assertEqual(['local_header'], headers)
        self.assertEqual([{'source': 'local'}], data)
        self.assertEqual(2, len(self.warnings))
        self.assertIn('保存到服务器失败', self.warnings[0][1])
        self.assertIn('从服务器加载数据失败', self.warnings[1][1])

    def test_batch_import_uses_same_mode_strategy(self):
        self.window.network.is_server_mode = True
        self.window._save_batch_import_data_local = self.local_save_batch
        self.window._load_batch_import_data_local = self.local_load_batch

        self.window.save_batch_import_data_with_mode(['h'], [{'v': 1}])
        headers, data = self.window.load_batch_import_data_with_mode()

        self.assertEqual((['h'], [{'v': 1}]), self.window.network.saved_batch)
        self.assertIsNone(self.window.local_batch_saved)
        self.assertEqual(['server_batch_header'], headers)
        self.assertEqual([{'source': 'server_batch'}], data)


if __name__ == '__main__':
    unittest.main()
