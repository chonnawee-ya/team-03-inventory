"""
commands/list_items.py — US-01: ดูรายการสินค้าทั้งหมดพร้อมจำนวนคงเหลือ
"""

from __future__ import annotations

import argparse
from pathlib import Path

from storage import InventoryStore


def cmd_list(args: argparse.Namespace) -> None:
    """AC-1: มีสินค้า -> แสดงชื่อ/รหัส/จำนวนครบทุกรายการ
    AC-2: ไม่มีสินค้า -> แสดง "ยังไม่มีสินค้าในระบบ" """
    service = getattr(args, "service", None)
    if service is not None:
        items = service.list_products()
    else:
        store = getattr(args, "store", None) or InventoryStore(Path(args.data))
        items = store.load_products()

    if not items:
        print("ยังไม่มีสินค้าในระบบ")
        return

    items.sort(key=lambda i: getattr(i, "sku", getattr(i, "code", "")))
    name_w = max(len(i.name) for i in items) + 2
    name_w = max(name_w, 14)
    print(f"{'รหัส':<12}{'ชื่อสินค้า':<{name_w}}{'หมวดหมู่':<14}{'คงเหลือ':>10}  {'สถานะ'}")
    print("-" * (12 + name_w + 14 + 10 + 15))
    for item in items:
        code = getattr(item, "sku", getattr(item, "code", ""))
        cat = getattr(item, "category", "-")
        status = "[LOW STOCK]" if getattr(item, "is_low_stock", False) else "ปกติ"
        # แสดงจำนวน: ถ้าเป็นจำนวนเต็มแสดงเป็น int ไม่ติดจุดทศนิยม
        qty_str = f"{int(item.quantity)}" if item.quantity == int(item.quantity) else f"{item.quantity:.2f}"
        print(f"{code:<12}{item.name:<{name_w}}{cat:<14}{qty_str:>10}  {status}")
    print(f"\nรวมทั้งหมด {len(items)} รายการ")


def register(subparsers: argparse._SubParsersAction) -> None:
    """เพิ่มคำสั่ง list เข้า argparse subparsers"""
    p = subparsers.add_parser("list", help="US-01: ดูรายการสินค้าทั้งหมด")
    p.set_defaults(func=cmd_list)

