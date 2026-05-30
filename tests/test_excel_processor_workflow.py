# -*- coding: utf-8 -*-
import unittest

from excel_processor import ExcelProcessor


class ExcelProcessorWorkflowTests(unittest.TestCase):
    def setUp(self):
        self.processor = ExcelProcessor()

    def test_build_shipment_quantity_map_uses_compound_key_and_accumulates(self):
        shipment_data = [
            {'物料号': 'A001', '销售订单号': 'SO1', '销售订单行号': '10', '内需单号': 'N1', '本次送货数量': 3},
            {'物料号': 'A001', '销售订单号': 'SO1', '销售订单行号': '10', '内需单号': 'N1', '本次送货数量': 2},
            {'物料号': '', '销售订单号': '', '销售订单行号': '', '内需单号': '', '本次送货数量': 9},
        ]

        result = self.processor.build_shipment_quantity_map(shipment_data)

        self.assertEqual({'A001|SO1|10|N1': 5}, result)

    def test_attach_shipment_quantities_keeps_diff_shape(self):
        diff_data = [
            {'物料号': 'A001', '销售订单': 'SO1', '销售订单行号': '10', '内需单号': 'N1', '变化量': 4, '今天总缺料': 8},
            {'物料号': 'A002', '销售订单': 'SO2', '销售订单行号': '20', '内需单号': 'N2', '变化量': 1, '今天总缺料': 1},
        ]

        result = self.processor.attach_shipment_quantities(diff_data, {'A001|SO1|10|N1': 5})

        self.assertIs(result, diff_data)
        self.assertEqual(5, result[0]['本次送货数量'])
        self.assertEqual(0, result[1]['本次送货数量'])

    def test_build_level1_records_preserves_existing_database_shape(self):
        diff_data = [
            {
                '物料号': 'A001',
                '物料描述': '透明商标',
                '供方': '供应商1',
                '今天总缺料': 8,
            },
            {
                '物料号': 'A002',
                '物料描述': '普通材料',
                '供方': '供应商2',
                '今天总缺料': 3,
            },
        ]
        today_data = [
            {'物料号': 'A001', '销售订单': 'SO1', '供方': '供应商1'},
            {'物料号': 'A002', '销售订单': 'SO2', '供方': '供应商2'},
        ]

        result = self.processor.build_level1_records(diff_data, today_data)

        self.assertEqual([
            {
                '序号': 1,
                '物料号': 'A001',
                '物料描述': '透明商标',
                '供方': '供应商1',
                '总缺料': 8,
                '分类': '透明商标类',
                '订单号': 'SO1',
                '送货日期': '供应商1',
            },
            {
                '序号': 2,
                '物料号': 'A002',
                '物料描述': '普通材料',
                '供方': '供应商2',
                '总缺料': 3,
                '分类': '其他',
                '订单号': 'SO2',
                '送货日期': '供应商2',
            },
        ], result)

    def test_compare_flow_can_be_composed_without_ui(self):
        yesterday_data = [
            {'物料号': 'A001', '销售订单': 'SO1', '销售订单行号': '10', '内需单号': 'N1', '总缺料': 4, '物料描述': '透明商标', '供方': '供应商1'},
        ]
        today_data = [
            {'物料号': 'A001', '销售订单': 'SO1', '销售订单行号': '10', '内需单号': 'N1', '总缺料': 8, '物料描述': '透明商标', '供方': '供应商1'},
        ]
        shipment_data = [
            {'物料号': 'A001', '销售订单号': 'SO1', '销售订单行号': '10', '内需单号': 'N1', '本次送货数量': 5},
        ]

        shipment_map = self.processor.build_shipment_quantity_map(shipment_data)
        diff_data = self.processor.compare_and_get_diff(yesterday_data, today_data)
        diff_data = self.processor.attach_shipment_quantities(diff_data, shipment_map)
        diff_data = self.processor.sort_diff_data(diff_data)
        db_records = self.processor.build_level1_records(diff_data, today_data)

        self.assertEqual(4, diff_data[0]['变化量'])
        self.assertEqual(5, diff_data[0]['本次送货数量'])
        self.assertEqual(8, db_records[0]['总缺料'])
        self.assertEqual('透明商标类', db_records[0]['分类'])

    def test_normalize_row_maps_alias_to_standard_field(self):
        row = {'物料号': 'A001', '总缺料（差异数部分标红）': 100}
        result = self.processor.normalize_row(row)
        self.assertEqual(100, result.get('总缺料'))

    def test_normalize_row_maps_material_code_alias(self):
        row = {'物料编码': 'A002', '总缺料': 200}
        result = self.processor.normalize_row(row)
        self.assertEqual('A002', result.get('物料号'))

    def test_normalize_row_preserves_standard_field(self):
        row = {'物料号': 'A003', '总缺料': 300}
        result = self.processor.normalize_row(row)
        self.assertEqual(300, result.get('总缺料'))

    def test_compare_with_alias_fields(self):
        yesterday_data = [
            {'物料号': 'A001', '销售订单': 'SO1', '销售订单行号': '10', '内需单号': 'N1', '总缺料': 4},
        ]
        today_data = [
            {'物料号': 'A001', '销售订单': 'SO1', '销售订单行号': '10', '内需单号': 'N1', '总缺料（差异数部分标红）': 8},
        ]
        # 模拟 read_excel_with_color 的规范化行为
        today_data_normalized = [self.processor.normalize_row(row) for row in today_data]
        diff_data = self.processor.compare_and_get_diff(yesterday_data, today_data_normalized)
        self.assertEqual(4, diff_data[0]['变化量'])
        self.assertEqual(8, diff_data[0]['今天总缺料'])


if __name__ == '__main__':
    unittest.main()
