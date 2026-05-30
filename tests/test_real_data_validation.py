# -*- coding: utf-8 -*-
"""
使用真实数据验证计算公式
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_with_real_data():
    """使用截图中的真实数据验证"""
    print("=" * 70)
    print("[TEST] Real Data Validation")
    print("=" * 70)

    # 从截图中提取的数据
    # 格式: transit(供应商在途量), yest(昨天总缺料), today(今天总缺料), ship(本次送货数量)
    test_data = [
        {'no': 1, 'transit': 205, 'yest': 235, 'today': 255, 'ship': 205},
        {'no': 2, 'transit': 18, 'yest': 274, 'today': 284, 'ship': 18},
        {'no': 3, 'transit': 0, 'yest': 20, 'today': 1, 'ship': 20},
        {'no': 4, 'transit': 27, 'yest': 52, 'today': 28, 'ship': 52},
    ]

    print("\n[INPUT] Original Data")
    print("Row  | Transit | Yest | Today | Ship")
    print("-" * 50)
    for row in test_data:
        print(f"  {row['no']}  |   {row['transit']:<6}|  {row['yest']:<4}|  {row['today']:<4}|  {row['ship']}")

    print("\n" + "=" * 70)
    print("[CALC] Step-by-Step Calculation")
    print("=" * 70)

    results = []
    for row in test_data:
        print(f"\n--- Row {row['no']} ---")

        yesterday_total = row['yest']
        today_total = row['today']
        transit_qty = row['transit']
        shipment_qty = row['ship']

        print(f"  Input: yest={yesterday_total}, today={today_total}")
        print(f"         transit={transit_qty}, ship={shipment_qty}")

        # 数据1 = 今天总缺料 - 供应商在途量
        data1 = today_total - transit_qty
        print(f"\n  [Data1] = today - transit")
        print(f"         = {today_total} - {transit_qty}")
        print(f"         = {data1}")

        # 数据2 = 昨天总缺料 - 本次送货数量（仅当相同时才减）
        if yesterday_total == shipment_qty:
            data2 = 0
            print(f"\n  [Data2] = 0")
            print(f"         (yest==ship, {yesterday_total}=={shipment_qty})")
        else:
            data2 = yesterday_total
            print(f"\n  [Data2] = yest")
            print(f"         (yest!=ship, {yesterday_total}!={shipment_qty})")
            print(f"         = {yesterday_total}")

        # 变化量 = 数据1 - 数据2
        change = data1 - data2
        print(f"\n  [Change] = data1 - data2")
        print(f"          = {data1} - {data2}")
        print(f"          = {change}")

        # 红色标记判断
        is_red = change != today_total
        print(f"\n  [Red Flag] change({change}) != today({today_total}) ? -> {'YES' if is_red else 'NO'}")

        results.append({
            'row': row['no'],
            'yest': yesterday_total,
            'today': today_total,
            'transit': transit_qty,
            'ship': shipment_qty,
            'data1': data1,
            'data2': data2,
            'change': change,
            'is_red': is_red,
        })

    # 汇总表格
    print("\n" + "=" * 70)
    print("[SUMMARY] Results Table")
    print("=" * 70)
    print("\nRow | Yest | Today | Transit | Ship  | Data1 | Data2 | Change | Red")
    print("-" * 80)
    for r in results:
        red_mark = "YES" if r['is_red'] else "NO"
        print(f"  {r['row']} | {r['yest']:<4} | {r['today']:<5} | {r['transit']:<7} | {r['ship']:<4} | {r['data1']:<5} | {r['data2']:<5} | {r['change']:<6} | {red_mark}")

    # 分析结果
    print("\n" + "=" * 70)
    print("[ANALYSIS] Result Analysis")
    print("=" * 70)

    red_count = sum(1 for r in results if r['is_red'])
    non_red_count = len(results) - red_count

    print(f"\n  Red flagged rows: {red_count}")
    print(f"  Non-red rows:     {non_red_count}")

    print("\n  Red flag meaning:")
    print("    change != today means data anomaly or attention needed")

    for r in results:
        if r['is_red']:
            print(f"\n  Row {r['row']} anomaly:")
            print(f"    change={r['change']}, today={r['today']}")
            print(f"    diff={abs(r['change'] - r['today'])}")

    print("\n" + "=" * 70)
    print("[DONE] Validation Complete")
    print("=" * 70)


if __name__ == '__main__':
    test_with_real_data()
