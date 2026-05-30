# -*- coding: utf-8 -*-
"""
新计算公式验证测试
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from excel_processor import ExcelProcessor


def test_new_formula():
    processor = ExcelProcessor()

    print("=" * 70)
    print("[TEST] New Formula Validation")
    print("=" * 70)

    # 截图数据
    yesterday_data = [
        {'物料号': 'M001', '销售订单': 'SO1', '销售订单行号': '10', '内需单号': 'N1',
         '总缺料': 235, '供应商在途量': 205},
        {'物料号': 'M002', '销售订单': 'SO2', '销售订单行号': '20', '内需单号': 'N2',
         '总缺料': 274, '供应商在途量': 18},
        {'物料号': 'M003', '销售订单': 'SO3', '销售订单行号': '30', '内需单号': 'N3',
         '总缺料': 20, '供应商在途量': 0},
        {'物料号': 'M004', '销售订单': 'SO4', '销售订单行号': '40', '内需单号': 'N4',
         '总缺料': 52, '供应商在途量': 27},
    ]

    today_data = [
        {'物料号': 'M001', '销售订单': 'SO1', '销售订单行号': '10', '内需单号': 'N1',
         '总缺料': 255, '供应商在途量': 205},
        {'物料号': 'M002', '销售订单': 'SO2', '销售订单行号': '20', '内需单号': 'N2',
         '总缺料': 284, '供应商在途量': 18},
        {'物料号': 'M003', '销售订单': 'SO3', '销售订单行号': '30', '内需单号': 'N3',
         '总缺料': 1, '供应商在途量': 0},
        {'物料号': 'M004', '销售订单': 'SO4', '销售订单行号': '40', '内需单号': 'N4',
         '总缺料': 28, '供应商在途量': 27},
    ]

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
    diff_result = processor.compare_and_get_diff(yesterday_data, today_data, shipment_dict)

    print("\n[RESULT]")
    print(f"{'物料':<6} {'在途':<6} {'送货':<6} {'昨天':<6} {'今天':<6} {'真实出货量':<10} {'新增数量':<8}")
    print("-" * 65)
    for item in diff_result:
        print(f"{item['物料号']:<6} {item['供应商在途量']:<6} {item['本次送货数量']:<6} "
              f"{item['昨天总缺料']:<6} {item['今天总缺料']:<6} "
              f"{item['真实出货量']:<10} {item['新增数量']:<8}")

    # 验证
    expected = [
        {'物料号': 'M001', '真实出货量': 235, '新增数量': 20},
        {'物料号': 'M002', '真实出货量': 274, '新增数量': 10},
        {'物料号': 'M003', '真实出货量': 0, '新增数量': 1},
        {'物料号': 'M004', '真实出货量': 0, '新增数量': 28},
    ]

    print("\n[VERIFY]")
    all_pass = True
    for exp in expected:
        for item in diff_result:
            if item['物料号'] == exp['物料号']:
                ok = (item['真实出货量'] == exp['真实出货量'] and
                      item['新增数量'] == exp['新增数量'])
                status = "PASS" if ok else "FAIL"
                print(f"  [{status}] {exp['物料号']}: real={item['真实出货量']}, new={item['新增数量']}")
                if not ok:
                    all_pass = False
                    print(f"         expected: real={exp['真实出货量']}, new={exp['新增数量']}")
                break

    return all_pass


def test_all_conditions():
    """测试所有5个条件"""
    processor = ExcelProcessor()

    print("\n" + "=" * 70)
    print("[TEST] All 5 Conditions")
    print("=" * 70)

    test_cases = [
        # 条件5: 四个值都相同
        {'name': 'Cond5', 'transit': 100, 'ship': 100, 'yest': 100, 'today': 100,
         'expect_real': 0, 'expect_new': 0},
        # 条件1: 在途=送货
        {'name': 'Cond1', 'transit': 100, 'ship': 100, 'yest': 80, 'today': 120,
         'expect_real': 80, 'expect_new': 40},
        # 条件2: 在途>送货
        {'name': 'Cond2', 'transit': 50, 'ship': 30, 'yest': 40, 'today': 60,
         'expect_real': 40, 'expect_new': 20},
        # 条件3: 昨天=送货
        {'name': 'Cond3', 'transit': 10, 'ship': 20, 'yest': 20, 'today': 30,
         'expect_real': 0, 'expect_new': 30},
        # 条件4: 四值都不同
        {'name': 'Cond4', 'transit': 10, 'ship': 20, 'yest': 30, 'today': 40,
         'expect_real': 30, 'expect_new': 10},
    ]

    print(f"\n{'Case':<8} {'InTransit':<10} {'Shipped':<8} {'Yest':<6} {'Today':<6} {'RealShip':<10} {'NewQty':<8}")
    print("-" * 70)

    all_pass = True
    for tc in test_cases:
        real, new = processor._calc_real_shipment_and_new_qty(
            tc['transit'], tc['ship'], tc['yest'], tc['today'])
        ok = (real == tc['expect_real'] and new == tc['expect_new'])
        status = "PASS" if ok else "FAIL"
        print(f"  [{status}] {tc['name']:<6} {tc['transit']:<10} {tc['ship']:<8} "
              f"{tc['yest']:<6} {tc['today']:<6} {real:<10} {new:<8}")
        if not ok:
            all_pass = False
            print(f"         expected: real={tc['expect_real']}, new={tc['expect_new']}")

    return all_pass


if __name__ == '__main__':
    r1 = test_new_formula()
    r2 = test_all_conditions()

    print("\n" + "=" * 70)
    if r1 and r2:
        print("[SUCCESS] All tests passed!")
    else:
        print("[FAIL] Some tests failed!")
        sys.exit(1)
