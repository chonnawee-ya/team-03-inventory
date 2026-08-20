"""
commands/export_items.py — US-05: ส่งออกรายงานสต็อกเป็นไฟล์ CSV
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

from storage import InventoryStore


def cmd_export(args: argparse.Namespace) -> None:
    """เขียนไฟล์ CSV พร้อม header code,name,quantity,updated_at"""
    store = InventoryStore(Path(args.data))
    items = store.load_items()

    output_path = Path(args.output)
    with output_path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(["code", "name", "quantity", "updated_at"])
        for item in sorted(items, key=lambda i: i.code):
            writer.writerow([item.code, item.name, item.quantity, item.updated_at])

    print(f"ส่งออกรายงานสต็อก {len(items)} รายการ ไปที่ '{output_path}' เรียบร้อยแล้ว")


def register(subparsers: argparse._SubParsersAction) -> None:
    """เพิ่มคำสั่ง export เข้า argparse subparsers"""
    p = subparsers.add_parser("export", help="US-05: ส่งออกรายงานสต็อกเป็น CSV")
    p.add_argument("--output", default="stock_report.csv", help="ชื่อไฟล์ CSV ที่จะสร้าง")
    p.set_defaults(func=cmd_export)
