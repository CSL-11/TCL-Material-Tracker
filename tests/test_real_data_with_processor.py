# -*- coding: utf-8 -*-
"""
使用 ExcelProcessor 类验证截图数据
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from excel_processor import ExcelProcessor


def test_real_data():
    processor = ExcelProcessor()

    # 截图数据构建为 ExcelProcessor 需要的格式
    # 注意: compare_and_get_diff 需要 yesterday_data 和 today_data
    # 每行需要 make_match_key 能提取的字段
    yesterday_data = [
        {'物料号': 'M001', '销售订单': 'SO1', '销售订单行号': '10', '内需单号': 'N1',
         '总缺料': 235, '供应商在途量': 205, '供方': 'A'},
        {'物料号': 'M002', '销售订单': 'SO2', '销售订单行号': '20', '内需单号': 'N2',
         '总缺料': 274, '供应商在途量': 18, '供方': 'B'},
        {'物料号': 'M003', '销售订单': 'SO3', '销售订单行号': '30', '内需单号': 'N3',
         '总缺料': 20, '供应商在途量': 0, '供方': 'C'},
        {'物料号': 'M004', '销售订单': 'SO4', '销售订单行号': '40', '内需单号': 'N4',
         '总缺料': 52, '供应商在途量': 27, '供方': 'D'},
    ]

    today_data = [
        {'物料号': 'M001', '销售订单': 'SO1', '销售订单行号': '10', '内需单号': 'N1',
         '总缺料': 255, '供应商在途量': 205, '供方': 'A'},
        {'物料号': 'M002', '销售订单': 'SO2', '销售订单行号': '20', '内需单号': 'N2',
         '总缺料': 284, '供应商在途量': 18, '供方': 'B'},
        {'物料号': 'M003', '销售订单': 'SO3', '销售订单行号': '30', '内需单号': 'N3',
         '总缺料': 1, '供应商在途量': 0, '供方': 'C'},
        {'物料号': 'M004', '销售订单': 'SO4', '销售订单行号': '40', '内需单号': 'N4',
         '总缺料': 28, '供应商在途量': 27, '供方': 'D'},
    ]

    # 出货数据: 本次送货数量 对应截图中的 F 列
    shipment_data = [
        {'物料号': 'M001', '销售订单': 'SO1', '销售订单行号': '10', '内需单号': 'N1',
         '本次送货数量': 205},
        {'物料号': 'M002', '销售订单': 'SO2', '销售订单行号': '20', '内需单号': 'N2',
         '本次送货数量': 18},
        {'物料号': 'M003', '销售订单': 'SO3', '销售订单行号': '30', '内需单号': 'N3',
         '本次送货数量': 20},
        {'物料号': 'M004', '销售订单': 'SO4', '销售订单行号': '40', '内需单号': 'N4',
         '本次送货数量': 52},
    ]

    shipment_dict = processor.build_shipment_quantity_map(shipment_data)

    print("[INPUT] Shipment dict:")
    for k, v in shipment_dict.items():
        print(f"  {k}: {v}")

    # 执行比对
    diff_result = processor.compare_and_get_diff(yesterday_data, today_data, shipment_dict)

    print("\n[RESULT] Compare result:")
    print(f"{'物料':<6} {'昨天':<6} {'今天':<6} {'在途':<6} {'送货':<6} {'数据1':<7} {'数据2':<7} {'变化量':<7} {'红色'}")
    print("-" * 75)
    for item in diff_result:
        key = processor.make_match_key(item)
        is_red = item['变化量'] != item['今天总缺料']
        print(f"{item['物料号']:<6} {item['昨天总缺料']:<6} {item['今天总缺料']:<6} "
              f"{item['供应商在途量']:<6} {item['本次送货数量']:<6} "
              f"{item['数据1']:<7} {item['数据2']:<7} {item['变化量']:<7} {'YES' if is_red else 'NO'}")

    # 手动验证每个结果
    print("\n[VERIFY] Manual verification:")
    expected = [
        {'物料号': 'M001', '昨天总缺料': 235, '今天总缺料': 255, '供应商在途量': 205, '本次送货数量': 205,
         '数据1': 50, '数据2': 235, '变化量': -185},
        {'物料号': 'M002', '昨天总缺料': 274, '今天总缺料': 284, '供应商在途量': 18, '本次送货数量': 18,
         '数据1': 266, '数据2': 274, '变化量': -8},
        {'物料号': 'M003', '昨天总缺料': 20, '今天总缺料': 1, '供应商在途量': 0, '本次送货数量': 20,
         '数据1': 1, '数据2': 0, '变化量': 1},
        {'物料号': 'M004', '昨天总缺料': 52, '今天总缺料': 28, '供应商在途量': 27, '本次送货数量': 52,
         '数据1': 1, '数据2': 0, '变化量': 1},
    ]

    all_pass = True
    for exp in expected:
        for item in diff_result:
            if item['物料号'] == exp['物料号']:
                ok = True
                for field in ['数据1', '数据2', '变化量']:
                    if item[field] != exp[field]:
                        print(f"  [FAIL] {exp['物料号']} {field}: got {item[field]}, expected {exp[field]}")
                        ok = False
                        all_pass = False
                if ok:
                    print(f"  [PASS] {exp['物料号']}: data1={item['数据1']}, data2={item['数据2']}, change={item['变化量']}")
                break

    if all_pass:
        print("\n[SUCCESS] All rows verified!")
    else:
        print("\n[FAIL] Some rows failed verification!")
        sys.exit(1)


if __name__ == '__main__':
    test_real_data()
