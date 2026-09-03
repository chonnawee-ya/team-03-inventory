"""
commands/add_item.py — US-02: เพิ่มสินค้าใหม่เข้าระบบ
"""

from __future__ import annotations

import argparse
from pathlib import Path

from storage import InventoryStore
from service import (
    InventoryService,
    DuplicateSKUError,
    NegativeValueError,
    InvalidInputTypeError,
    MissingRequiredFieldError,
)


def cmd_add(args: argparse.Namespace) -> None:
    """เพิ่มสินค้าใหม่โดยผ่าน InventoryService"""
    service: InventoryService | None = getattr(args, "service", None)
    if service is None:
        from events import EventPublisher
        service = InventoryService(EventPublisher())
        store = getattr(args, "store", None) or InventoryStore(Path(args.data))
        store.load_into_service(service)

    try:
        service.add_product(
            sku=args.code,
            name=args.name,
            category=args.category,
            cost_price=args.cost,
            sell_price=args.price,
            unit=args.unit,
            quantity=args.qty,
            threshold=args.threshold,
        )
    except DuplicateSKUError:
        raise SystemExit(
            f"เกิดข้อผิดพลาด: รหัสสินค้า '{args.code}' มีอยู่ในระบบแล้ว "
            f"(ใช้คำสั่ง update เพื่อแก้ไขจำนวนแทน)"
        )
    except NegativeValueError as e:
        raise SystemExit(f"เกิดข้อผิดพลาด: ค่าต้องไม่ติดลบ และราคาต้องมากกว่า 0 ({e})")
    except (InvalidInputTypeError, MissingRequiredFieldError) as e:
        raise SystemExit(f"เกิดข้อผิดพลาด: {e}")

    # แสดงผลข้อความสำเร็จ
    qty_str = f"{int(args.qty)}" if args.qty == int(args.qty) else f"{args.qty}"
    print(f"เพิ่มสินค้า '{args.name}' (รหัส {args.code.upper()}) จำนวน {qty_str} เรียบร้อยแล้ว")


def register(subparsers: argparse._SubParsersAction) -> None:
    """เพิ่มคำสั่ง add เข้า argparse subparsers"""
    p = subparsers.add_parser("add", help="US-02: เพิ่มสินค้าใหม่")
    p.add_argument("--code", required=True, help="รหัสสินค้า เช่น A001")
    p.add_argument("--name", required=True, help="ชื่อสินค้า")
    p.add_argument("--qty", type=float, required=True, help="จำนวนเริ่มต้น")
    p.add_argument("--category", default="เครื่องเขียน", help="หมวดหมู่สินค้า (default: เครื่องเขียน)")
    p.add_argument("--cost", type=float, default=10.0, help="ราคาทุน (>0, default: 10.0)")
    p.add_argument("--price", type=float, default=20.0, help="ราคาขาย (>0, default: 20.0)")
    p.add_argument("--unit", default="ชิ้น", help="หน่วยนับ เช่น ชิ้น, กล่อง (default: ชิ้น)")
    p.add_argument("--threshold", type=float, default=5.0, help="จุดสั่งซื้อเพื่อแจ้งเตือนสต็อกต่ำ (default: 5.0)")
    p.set_defaults(func=cmd_add)

