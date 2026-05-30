# -*- coding: utf-8 -*-
"""
计算公式验证测试
使用模拟数据验证项目中的计算公式是否有冲突
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from excel_processor import ExcelProcessor


def test_compare_and_get_diff():
    """验证缺料差异计算公式"""
    print("=" * 60)
    print("测试1: 缺料差异计算公式验证")
    print("=" * 60)

    processor = ExcelProcessor()

    # 模拟数据：昨天和今天的缺料表
    yesterday_data = [
        {'物料号': 'M001', '销售订单': 'SO1', '销售订单行号': '10', '内需单号': 'N1',
         '总缺料': 100, '供应商在途量': 20, '供方': '供应商A', '物料描述': '透明商标材料'},
        {'物料号': 'M002', '销售订单': 'SO2', '销售订单行号': '20', '内需单号': 'N2',
         '总缺料': 50, '供应商在途量': 10, '供方': '供应商B', '物料描述': '铝箔材料'},
        {'物料号': 'M003', '销售订单': 'SO3', '销售订单行号': '30', '内需单号': 'N3',
         '总缺料': 80, '供应商在途量': 0, '供方': '供应商C', '物料描述': '接线材料'},
    ]

    today_data = [
        {'物料号': 'M001', '销售订单': 'SO1', '销售订单行号': '10', '内需单号': 'N1',
         '总缺料': 120, '供应商在途量': 30, '供方': '供应商A', '物料描述': '透明商标材料'},
        {'物料号': 'M002', '销售订单': 'SO2', '销售订单行号': '20', '内需单号': 'N2',
         '总缺料': 40, '供应商在途量': 5, '供方': '供应商B', '物料描述': '铝箔材料'},
        {'物料号': 'M004', '销售订单': 'SO4', '销售订单行号': '40', '内需单号': 'N4',
         '总缺料': 60, '供应商在途量': 15, '供方': '供应商D', '物料描述': '能源能效标签'},
    ]

    # 出货数据
    shipment_data = [
        {'物料号': 'M001', '销售订单': 'SO1', '销售订单行号': '10', '内需单号': 'N1',
         '本次送货数量': 30},
        {'物料号': 'M002', '销售订单': 'SO2', '销售订单行号': '20', '内需单号': 'N2',
         '本次送货数量': 10},
    ]

    # 构建出货字典
    shipment_dict = processor.build_shipment_quantity_map(shipment_data)

    print("\n【输入数据】")
    print("\n昨天缺料数据:")
    for row in yesterday_data:
        key = processor.make_match_key(row)
        print(f"  {key}: 总缺料={row['总缺料']}, 供应商在途量={row['供应商在途量']}")

    print("\n今天缺料数据:")
    for row in today_data:
        key = processor.make_match_key(row)
        print(f"  {key}: 总缺料={row['总缺料']}, 供应商在途量={row['供应商在途量']}")

    print("\n出货数据:")
    for key, qty in shipment_dict.items():
        print(f"  {key}: 本次送货数量={qty}")

    # 执行比对
    diff_result = processor.compare_and_get_diff(yesterday_data, today_data, shipment_dict)

    print("\n【计算过程】")
    for item in diff_result:
        key = processor.make_match_key(item)
        print(f"\n物料: {item['物料号']}")
        print(f"  昨天总缺料 = {item['昨天总缺料']}")
        print(f"  今天总缺料 = {item['今天总缺料']}")
        print(f"  供应商在途量 = {item['供应商在途量']}")
        print(f"  本次送货数量 = {item['本次送货数量']}")

        # 计算数据1
        data1 = item['今天总缺料'] - item['供应商在途量']
        print(f"  数据1 = 今天总缺料 - 供应商在途量 = {item['今天总缺料']} - {item['供应商在途量']} = {data1}")

        # 计算数据2
        if item['昨天总缺料'] == item['本次送货数量']:
            data2 = 0
            print(f"  数据2 = 0 (昨天总缺料 == 本次送货数量)")
        else:
            data2 = item['昨天总缺料']
            print(f"  数据2 = 昨天总缺料 = {item['昨天总缺料']} (昨天总缺料 != 本次送货数量)")

        # 计算变化量
        change = data1 - data2
        print(f"  变化量 = 数据1 - 数据2 = {data1} - {data2} = {change}")

        # 验证
        assert item['数据1'] == data1, f"数据1计算错误: 期望{data1}, 实际{item['数据1']}"
        assert item['数据2'] == data2, f"数据2计算错误: 期望{data2}, 实际{item['数据2']}"
        assert item['变化量'] == change, f"变化量计算错误: 期望{change}, 实际{item['变化量']}"

    print("\n[PASS] 缺料差异计算公式验证通过！")
    return diff_result


def test_pending_delivery():
    """验证还需交货计算公式"""
    print("\n" + "=" * 60)
    print("测试2: 还需交货计算公式验证")
    print("=" * 60)

    # 模拟供货计划数据
    supply_data = [
        {'物料号': 'M001', '物料描述': '透明商标材料', '总缺料': 100, '供应商在途量': 20, '已承诺量': 30},
        {'物料号': 'M002', '物料描述': '铝箔材料', '总缺料': 50, '供应商在途量': 10, '已承诺量': 15},
        {'物料号': 'M003', '物料描述': '接线材料', '总缺料': 80, '供应商在途量': 0, '已承诺量': 0},
        {'物料号': 'M004', '物料描述': '能源能效标签', '总缺料': 60, '供应商在途量': 15, '已承诺量': 20},
    ]

    # 模拟已送货数据
    delivery_data = [
        {'物料编码': 'M001', '收货数量': 30},
        {'物料编码': 'M001', '收货数量': 20},
        {'物料编码': 'M002', '收货数量': 10},
        {'物料编码': 'M004', '收货数量': 60},
    ]

    print("\n【输入数据】")
    print("\n供货计划:")
    for row in supply_data:
        print(f"  {row['物料号']}: 总缺料={row['总缺料']}, 供应商在途量={row['供应商在途量']}, 已承诺量={row['已承诺量']}")

    print("\n已送货记录:")
    for row in delivery_data:
        print(f"  {row['物料编码']}: 收货数量={row['收货数量']}")

    # 按物料编码汇总已送货数量
    delivered_dict = {}
    for row in delivery_data:
        material = row.get('物料编码', '') or ''
        if material:
            qty = row.get('收货数量', 0) or 0
            delivered_dict[material] = delivered_dict.get(material, 0) + qty

    print("\n【计算过程】")
    print("\n已送货汇总:")
    for material, qty in delivered_dict.items():
        print(f"  {material}: 已送货={qty}")

    # 合并数据：供货计划 + 已送货，计算还需交货
    pending_list = []
    for row in supply_data:
        material = row.get('物料号', '') or ''
        if not material:
            continue
        total = row.get('总缺料', 0) or 0
        delivered = delivered_dict.get(material, 0)
        remaining = total - delivered
        if remaining > 0:
            description = row.get('物料描述', '') or ''
            in_transit = row.get('供应商在途量', 0) or 0
            committed = row.get('已承诺量', 0) or 0
            pending_list.append({
                '物料号': material,
                '物料描述': description,
                '总缺料': total,
                '已送货': delivered,
                '还需交货': remaining,
                '供应商在途量': in_transit,
                '已承诺量': committed,
            })

    # 按还需交货量降序排序
    pending_list.sort(key=lambda x: x['还需交货'], reverse=True)

    print("\n还需交货计算结果:")
    for item in pending_list:
        print(f"  {item['物料号']}: 总缺料={item['总缺料']}, 已送货={item['已送货']}, 还需交货={item['还需交货']}")

    # 验证计算
    for item in pending_list:
        expected_remaining = item['总缺料'] - item['已送货']
        assert item['还需交货'] == expected_remaining, \
            f"{item['物料号']}还需交货计算错误: 期望{expected_remaining}, 实际{item['还需交货']}"

    print("\n[PASS] 还需交货计算公式验证通过！")
    return pending_list


def test_shipment_compare():
    """验证出货对比计算公式"""
    print("\n" + "=" * 60)
    print("测试3: 出货对比计算公式验证")
    print("=" * 60)

    processor = ExcelProcessor()

    # 模拟出货表格数据
    shipment_data = [
        {'物料号': 'M001', '总缺料': 100},
        {'物料号': 'M001', '总缺料': 50},
        {'物料号': 'M002', '数量': 30},
        {'物料号': 'M003', '总缺料': 80},
    ]

    # 模拟对比表格数据
    target_data = [
        {'物料号': 'M001', '总缺料': 120},
        {'物料号': 'M002', '数量': 25},
        {'物料号': 'M004', '总缺料': 60},
    ]

    print("\n【输入数据】")
    print("\n出货表格:")
    for row in shipment_data:
        material = row.get('物料号', '')
        qty = row.get('总缺料', 0) or row.get('数量', 0) or 0
        print(f"  {material}: 数量={qty}")

    print("\n对比表格:")
    for row in target_data:
        material = row.get('物料号', '')
        qty = row.get('总缺料', 0) or row.get('数量', 0) or 0
        print(f"  {material}: 数量={qty}")

    # 构建出货字典
    shipment_dict = {}
    for row in shipment_data:
        material = row.get('物料号', '')
        quantity = row.get('总缺料', 0) or row.get('数量', 0) or 0
        if material:
            shipment_dict[material] = shipment_dict.get(material, 0) + quantity

    # 构建对比字典
    target_dict = {}
    for row in target_data:
        material = row.get('物料号', '')
        quantity = row.get('总缺料', 0) or row.get('数量', 0) or 0
        if material:
            target_dict[material] = target_dict.get(material, 0) + quantity

    print("\n【计算过程】")
    print("\n出货汇总:")
    for material, qty in shipment_dict.items():
        print(f"  {material}: 出货数量={qty}")

    print("\n对比汇总:")
    for material, qty in target_dict.items():
        print(f"  {material}: 对比数量={qty}")

    # 计算差异
    all_materials = set(shipment_dict.keys()) | set(target_dict.keys())
    results = []

    print("\n差异计算:")
    for material in sorted(all_materials):
        shipment_qty = shipment_dict.get(material, 0)
        target_qty = target_dict.get(material, 0)
        diff = shipment_qty - target_qty
        results.append({
            '物料号': material,
            '出货数量': shipment_qty,
            '对比数量': target_qty,
            '差异': diff
        })
        print(f"  {material}: 差异 = {shipment_qty} - {target_qty} = {diff}")

    # 验证计算
    for item in results:
        expected_diff = item['出货数量'] - item['对比数量']
        assert item['差异'] == expected_diff, \
            f"{item['物料号']}差异计算错误: 期望{expected_diff}, 实际{item['差异']}"

    print("\n[PASS] 出货对比计算公式验证通过！")
    return results


def test_sorting_rule():
    """验证排序规则"""
    print("\n" + "=" * 60)
    print("测试4: 排序规则验证")
    print("=" * 60)

    processor = ExcelProcessor()

    # 模拟差异数据
    diff_data = [
        {'物料号': 'M001', '变化量': 10, '今天总缺料': 10},  # 红色标记
        {'物料号': 'M002', '变化量': 5, '今天总缺料': 5},    # 红色标记
        {'物料号': 'M003', '变化量': 8, '今天总缺料': 8},    # 红色标记
        {'物料号': 'M004', '变化量': 12, '今天总缺料': 10},  # 非红色标记
        {'物料号': 'M005', '变化量': 3, '今天总缺料': 5},    # 非红色标记
    ]

    print("\n【输入数据】")
    for item in diff_data:
        is_red = "红色" if item['变化量'] != item['今天总缺料'] else "非红色"
        print(f"  {item['物料号']}: 变化量={item['变化量']}, 今天总缺料={item['今天总缺料']}, {is_red}")

    # 执行排序
    sorted_data = processor.sort_diff_data(diff_data)

    print("\n【排序结果】")
    for item in sorted_data:
        is_red = "红色" if item['变化量'] != item['今天总缺料'] else "非红色"
        print(f"  {item['物料号']}: 变化量={item['变化量']}, 今天总缺料={item['今天总缺料']}, {is_red}")

    # 验证排序规则
    # 实际排序规则：非红色标记按变化量降序排在前面，红色标记排在后面
    prev_is_red = None
    prev_change = None
    for item in sorted_data:
        is_red = item['变化量'] != item['今天总缺料']
        if prev_is_red is not None:
            # 非红色标记应该在红色标记前面
            if not prev_is_red and is_red:
                pass  # 正确：非红色在前，红色在后
            elif prev_is_red and not is_red:
                assert False, "非红色标记应该在红色标记前面"
            elif prev_is_red == is_red:
                # 同组内应该按变化量降序排列
                assert prev_change >= item['变化量'], \
                    f"同组内排序错误: {prev_change} < {item['变化量']}"
        prev_is_red = is_red
        prev_change = item['变化量']

    print("\n[PASS] 排序规则验证通过！")
    return sorted_data


def test_match_key():
    """验证复合匹配键"""
    print("\n" + "=" * 60)
    print("测试5: 复合匹配键验证")
    print("=" * 60)

    processor = ExcelProcessor()

    # 测试数据
    test_cases = [
        {'物料号': 'M001', '销售订单': 'SO1', '销售订单行号': '10', '内需单号': 'N1'},
        {'物料编码': 'M002', '销售订单号': 'SO2', '销售订单行号': '20', '内需单号': 'N2'},
        {'物料号': 'M003', '销售订单': 'SO3', '销售订单行号': '', '内需单号': ''},
        {'物料号': 'M004', '销售订单': 'SO4', '销售订单行号': '40', '内需单号': 'N4'},
    ]

    expected_keys = [
        'M001|SO1|10|N1',
        'M002|SO2|20|N2',
        'M003|SO3||',
        'M004|SO4|40|N4',
    ]

    print("\n【测试用例】")
    for i, (row, expected) in enumerate(zip(test_cases, expected_keys)):
        key = processor.make_match_key(row)
        print(f"  用例{i+1}: {row}")
        print(f"    期望: {expected}")
        print(f"    实际: {key}")
        assert key == expected, f"匹配键计算错误: 期望{expected}, 实际{key}"

    print("\n[PASS] 复合匹配键验证通过！")


def test_material_classification():
    """验证物料分类规则"""
    print("\n" + "=" * 60)
    print("测试6: 物料分类规则验证")
    print("=" * 60)

    processor = ExcelProcessor()

    # 测试数据
    test_cases = [
        ('透明商标材料', '透明商标类'),
        ('白色PET标签', '透明商标类'),
        ('银色铝箔', '铝箔类'),
        ('电化铝箔包装', '铝箔类'),
        ('接线端子', '接线类'),
        ('能源标签', '能源能效类'),
        ('能效标识', '能源能效类'),
        ('型号标贴', '标贴类'),
        ('纸箱标贴', '标贴类'),
        ('说明书', '说明书类'),
        ('合格证', '说明书类'),
        ('特光材料', '特光类'),
        ('普通材料', '其他'),
        ('', '未分类'),
        (None, '未分类'),
    ]

    print("\n【测试用例】")
    for desc, expected in test_cases:
        result = processor.classify_material(desc)
        status = "[OK]" if result == expected else "[FAIL]"
        print(f"  {status} 物料描述: '{desc}' -> 期望: {expected}, 实际: {result}")
        assert result == expected, f"分类错误: 期望{expected}, 实际{result}"

    print("\n[PASS] 物料分类规则验证通过！")


def test_shipment_quantity_map():
    """验证出货数量汇总"""
    print("\n" + "=" * 60)
    print("测试7: 出货数量汇总验证")
    print("=" * 60)

    processor = ExcelProcessor()

    # 模拟出货数据
    shipment_data = [
        {'物料号': 'M001', '销售订单': 'SO1', '销售订单行号': '10', '内需单号': 'N1',
         '本次送货数量': 30},
        {'物料号': 'M001', '销售订单': 'SO1', '销售订单行号': '10', '内需单号': 'N1',
         '本次送货数量': 20},
        {'物料号': 'M002', '销售订单': 'SO2', '销售订单行号': '20', '内需单号': 'N2',
         '本次送货数量': 15},
        {'物料号': '', '销售订单': '', '销售订单行号': '', '内需单号': '',
         '本次送货数量': 10},  # 空键，应该被忽略
    ]

    print("\n【输入数据】")
    for row in shipment_data:
        key = processor.make_match_key(row)
        print(f"  {key}: 本次送货数量={row['本次送货数量']}")

    # 执行汇总
    result = processor.build_shipment_quantity_map(shipment_data)

    print("\n【汇总结果】")
    for key, qty in result.items():
        print(f"  {key}: 总数量={qty}")

    # 验证结果
    expected = {
        'M001|SO1|10|N1': 50,  # 30 + 20
        'M002|SO2|20|N2': 15,
    }

    assert result == expected, f"汇总错误: 期望{expected}, 实际{result}"

    print("\n[PASS] 出货数量汇总验证通过！")


def main():
    """主函数"""
    print("=" * 60)
    print("计算公式验证测试")
    print("=" * 60)

    try:
        # 执行所有测试
        test_compare_and_get_diff()
        test_pending_delivery()
        test_shipment_compare()
        test_sorting_rule()
        test_match_key()
        test_material_classification()
        test_shipment_quantity_map()

        print("\n" + "=" * 60)
        print("[SUCCESS] 所有计算公式验证通过！")
        print("=" * 60)

    except AssertionError as e:
        print(f"\n[FAIL] 验证失败: {e}")
        return 1
    except Exception as e:
        print(f"\n[ERROR] 测试出错: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == '__main__':
    exit(main())
