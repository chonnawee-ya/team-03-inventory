"""
commands/add_item.py — US-02: เพิ่มสินค้าใหม่เข้าระบบ
"""

from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path

from models import Item
from storage import InventoryStore


def cmd_add(args: argparse.Namespace) -> None:
    """กันรหัสซ้ำ และกันจำนวนเริ่มต้นติดลบ"""
    if args.qty < 0:
        raise SystemExit("เกิดข้อผิดพลาด: จำนวนสินค้าเริ่มต้นต้องไม่ติดลบ")

    store = InventoryStore(Path(args.data))
    items = store.load_items()

    if store.find_by_code(items, args.code):
        raise SystemExit(
            f"เกิดข้อผิดพลาด: รหัสสินค้า '{args.code}' มีอยู่ในระบบแล้ว "
            f"(ใช้คำสั่ง update เพื่อแก้ไขจำนวนแทน)"
        )

    new_item = Item(
        code=args.code,
        name=args.name,
        quantity=args.qty,
        updated_at=datetime.now().isoformat(timespec="seconds"),
    )
    items.append(new_item)
    store.save_items(items)
    print(f"เพิ่มสินค้า '{args.name}' (รหัส {args.code}) จำนวน {args.qty} เรียบร้อยแล้ว")


def register(subparsers: argparse._SubParsersAction) -> None:
    """เพิ่มคำสั่ง add เข้า argparse subparsers"""
    p = subparsers.add_parser("add", help="US-02: เพิ่มสินค้าใหม่")
    p.add_argument("--code", required=True, help="รหัสสินค้า เช่น A001")
    p.add_argument("--name", required=True, help="ชื่อสินค้า")
    p.add_argument("--qty", type=int, required=True, help="จำนวนเริ่มต้น")
    p.set_defaults(func=cmd_add)
