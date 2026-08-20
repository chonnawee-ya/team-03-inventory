"""
commands/update_item.py — US-03: แก้ไขจำนวนสินค้าเมื่อรับหรือจ่ายของ
"""

from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path

from storage import InventoryStore


def cmd_update(args: argparse.Namespace) -> None:
    """delta บวก = รับเข้า, ลบ = จ่ายออก — กันยอดคงเหลือติดลบ"""
    store = InventoryStore(Path(args.data))
    items = store.load_items()

    item = store.find_by_code(items, args.code)
    if item is None:
        raise SystemExit(f"เกิดข้อผิดพลาด: ไม่พบสินค้ารหัส '{args.code}' ในระบบ")

    new_qty = item.quantity + args.delta
    if new_qty < 0:
        raise SystemExit(
            f"เกิดข้อผิดพลาด: จำนวนคงเหลือของ '{item.name}' จะติดลบ "
            f"(ปัจจุบัน {item.quantity}, ต้องการปรับ {args.delta:+d})"
        )

    old_qty = item.quantity
    item.quantity = new_qty
    item.updated_at = datetime.now().isoformat(timespec="seconds")
    store.save_items(items)

    action = "รับเข้า" if args.delta >= 0 else "จ่ายออก"
    reason = f" เหตุผล: {args.reason}" if args.reason else ""
    print(
        f"{action} '{item.name}' (รหัส {item.code}) {abs(args.delta)} ชิ้น "
        f"({old_qty} -> {new_qty}){reason}"
    )


def register(subparsers: argparse._SubParsersAction) -> None:
    """เพิ่มคำสั่ง update เข้า argparse subparsers"""
    p = subparsers.add_parser("update", help="US-03: แก้ไขจำนวนสินค้า (รับเข้า/จ่ายออก)")
    p.add_argument("--code", required=True, help="รหัสสินค้าที่จะแก้ไข")
    p.add_argument(
        "--delta",
        type=int,
        required=True,
        help="จำนวนที่เปลี่ยนแปลง (บวก = รับเข้า, ลบ = จ่ายออก) เช่น -5 หรือ 20",
    )
    p.add_argument("--reason", default="", help="เหตุผลของการปรับจำนวน (ไม่บังคับ)")
    p.set_defaults(func=cmd_update)
