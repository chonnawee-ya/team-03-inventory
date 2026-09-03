"""
commands/update_item.py — US-03: แก้ไขจำนวนสินค้าเมื่อรับหรือจ่ายของ
"""

from __future__ import annotations

import argparse
from pathlib import Path

from storage import InventoryStore
from service import (
    InventoryService,
    ProductNotFoundError,
    InsufficientStockError,
    InvalidInputTypeError,
)


def cmd_update(args: argparse.Namespace) -> None:
    """delta บวก = รับเข้า, ลบ = จ่ายออก — ผ่าน InventoryService และส่ง Notification"""
    service: InventoryService | None = getattr(args, "service", None)
    if service is None:
        from events import EventPublisher
        from notifiers import NotifierFactory
        ep = EventPublisher()
        ep.subscribe("LOW_STOCK_ALERT", NotifierFactory.create("email"))
        ep.subscribe("STOCK_IN_SUCCESS", NotifierFactory.create("sms"))
        ep.subscribe("STOCK_OUT_SUCCESS", NotifierFactory.create("sms"))
        service = InventoryService(ep)
        store = getattr(args, "store", None) or InventoryStore(Path(args.data))
        store.load_into_service(service)

    code_upper = args.code.upper()
    if code_upper not in service.products:
        raise SystemExit(f"เกิดข้อผิดพลาด: ไม่พบสินค้ารหัส '{args.code}' ในระบบ (ไม่พบข้อมูลสินค้าที่ค้นหา)")

    product = service.products[code_upper]
    old_qty = product.quantity
    delta = args.delta

    try:
        if delta >= 0:
            service.stock_in(sku=args.code, amount=delta, note=args.reason)
        else:
            service.stock_out(sku=args.code, amount=abs(delta), note=args.reason)
    except InsufficientStockError:
        raise SystemExit(
            f"เกิดข้อผิดพลาด: จำนวนคงเหลือของ '{product.name}' จะติดลบ "
            f"(จำนวนคงเหลือไม่เพียงพอสำหรับการตัดจ่าย, ปัจจุบัน {old_qty}, ต้องการตัด {abs(delta)})"
        )
    except ProductNotFoundError as e:
        raise SystemExit(f"เกิดข้อผิดพลาด: ไม่พบสินค้ารหัส '{args.code}' ในระบบ ({e})")
    except InvalidInputTypeError as e:
        raise SystemExit(f"เกิดข้อผิดพลาด: {e}")

    new_qty = product.quantity
    action = "รับเข้า" if delta >= 0 else "จ่ายออก"
    reason = f" เหตุผล: {args.reason}" if args.reason else ""
    delta_str = f"{int(abs(delta))}" if abs(delta) == int(abs(delta)) else f"{abs(delta)}"
    old_str = f"{int(old_qty)}" if old_qty == int(old_qty) else f"{old_qty}"
    new_str = f"{int(new_qty)}" if new_qty == int(new_qty) else f"{new_qty}"
    print(
        f"{action} '{product.name}' (รหัส {product.sku}) {delta_str} {product.unit} "
        f"({old_str} -> {new_str}){reason}"
    )


def register(subparsers: argparse._SubParsersAction) -> None:
    """เพิ่มคำสั่ง update เข้า argparse subparsers"""
    p = subparsers.add_parser("update", help="US-03: แก้ไขจำนวนสินค้า (รับเข้า/จ่ายออก)")
    p.add_argument("--code", required=True, help="รหัสสินค้าที่จะแก้ไข")
    p.add_argument(
        "--delta",
        type=float,
        required=True,
        help="จำนวนที่เปลี่ยนแปลง (บวก = รับเข้า, ลบ = จ่ายออก) เช่น -5 หรือ 20",
    )
    p.add_argument("--reason", default="", help="เหตุผลของการปรับจำนวน (ไม่บังคับ)")
    p.set_defaults(func=cmd_update)

