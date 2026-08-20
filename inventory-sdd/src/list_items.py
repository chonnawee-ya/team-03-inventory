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
    store = InventoryStore(Path(args.data))
    items = store.load_items()

    if not items:
        print("ยังไม่มีสินค้าในระบบ")
        return

    items.sort(key=lambda i: i.code)
    name_w = max(len(i.name) for i in items) + 2
    print(f"{'รหัส':<10}{'ชื่อสินค้า':<{name_w}}{'จำนวนคงเหลือ':>15}")
    print("-" * (10 + name_w + 15))
    for item in items:
        print(f"{item.code:<10}{item.name:<{name_w}}{item.quantity:>15}")
    print(f"\nรวมทั้งหมด {len(items)} รายการ")


def register(subparsers: argparse._SubParsersAction) -> None:
    """เพิ่มคำสั่ง list เข้า argparse subparsers"""
    p = subparsers.add_parser("list", help="US-01: ดูรายการสินค้าทั้งหมด")
    p.set_defaults(func=cmd_list)
