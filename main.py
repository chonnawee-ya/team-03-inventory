#!/usr/bin/env python3
"""
main.py — entry point ของระบบสต็อกร้านเขียนดี

หน้าที่ของไฟล์นี้คือ "เชื่อมต่อและควบคุม" เท่านั้น
ตัวลอจิกจริงของแต่ละคำสั่งอยู่แยกไฟล์ในโฟลเดอร์ commands/
(1 ไฟล์ต่อ 1 user story) ไฟล์นี้ไม่รู้รายละเอียดข้างในของแต่ละคำสั่งเลย
มีหน้าที่แค่สร้าง argparse แล้วเรียก register() ของแต่ละคำสั่ง

โครงสร้าง:
  models.py              โครงสร้างข้อมูล Item
  storage.py              อ่าน/เขียนไฟล์ JSON
  commands/list_items.py     US-01
  commands/add_item.py       US-02
  commands/update_item.py    US-03
  commands/search_items.py   US-04
  commands/export_items.py   US-05
  main.py                 ไฟล์นี้ — จุดเริ่มโปรแกรม

ตัวอย่างการใช้งาน:
  python3 main.py list
  python3 main.py add --code A001 --name "ปากกาลูกลื่นสีน้ำเงิน" --qty 50
  python3 main.py update --code A001 --delta -5 --reason "ขายให้ลูกค้า"
  python3 main.py search --query ปากกา
  python3 main.py export --output stock_report.csv
"""

from __future__ import annotations

import argparse
import sys
from typing import Optional

# บังคับให้ stdout/stderr เป็น UTF-8 เสมอ กัน UnicodeEncodeError / ข้อความไทย
# เพี้ยนตอนรันบน Windows ที่ console ไม่ได้ตั้งเป็น UTF-8 (เช่น cp874, cp1252)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

from storage import DEFAULT_DATA_FILE
from commands import add_item, export_items, list_items, search_items, update_item

# ลงทะเบียนคำสั่งทั้งหมดที่นี่ที่เดียว — เพิ่มคำสั่งใหม่แค่เพิ่มไฟล์ใน commands/
# แล้วเติมชื่อ module ลงลิสต์นี้
COMMAND_MODULES = [
    list_items,    # US-01
    add_item,      # US-02
    update_item,   # US-03
    search_items,  # US-04
    export_items,  # US-05
]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="main.py",
        description="ระบบสต็อกร้านเขียนดี — จัดการสินค้าผ่าน command line",
    )
    parser.add_argument(
        "--data",
        default=str(DEFAULT_DATA_FILE),
        help=f"path ของไฟล์ข้อมูลสินค้า (default: {DEFAULT_DATA_FILE})",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # ให้แต่ละไฟล์คำสั่งลงทะเบียนตัวเองผ่าน register()
    for module in COMMAND_MODULES:
        module.register(subparsers)

    return parser


def main(argv: Optional[list[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        args.func(args)  # เรียกฟังก์ชันคำสั่งที่ register ไว้ (คุมจาก main.py จุดเดียว)
    except SystemExit as e:
        print(str(e), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
