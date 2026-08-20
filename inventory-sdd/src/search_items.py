"""
commands/search_items.py -- US-04: ค้นหาสินค้าด้วยชื่อหรือรหัส
"""

from __future__ import annotations

import argparse
from pathlib import Path

from storage import InventoryStore


def cmd_search(args: argparse.Namespace) -> None:
    """ค้นแบบ partial match ไม่สนตัวพิมพ์เล็ก-ใหญ่"""
    store = InventoryStore(Path(args.data))
    items = store.load_items()

    query = args.query.strip().lower()
    results = [
        i for i in items if query in i.code.lower() or query in i.name.lower()
    ]

    if not results:
        print(f"ไม่พบสินค้าที่ตรงกับคำค้นหา '{args.query}'")
        return

    results.sort(key=lambda i: i.code)
    name_w = max(len(i.name) for i in results) + 2
    print(f"{'รหัส':<10}{'ชื่อสินค้า':<{name_w}}{'จำนวนคงเหลือ':>15}")
    print("-" * (10 + name_w + 15))
    for item in results:
        print(f"{item.code:<10}{item.name:<{name_w}}{item.quantity:>15}")
    print(f"\nพบ {len(results)} รายการ")


def register(subparsers: argparse._SubParsersAction) -> None:
    """เพิ่มคำสั่ง search เข้า argparse subparsers"""
    p = subparsers.add_parser("search", help="US-04: ค้นหาสินค้าด้วยชื่อหรือรหัส")
    p.add_argument("--query", required=True, help="คำค้นหา (ชื่อหรือรหัสสินค้า)")
    p.set_defaults(func=cmd_search)

