"""
commands/search_items.py -- US-04: ค้นหาสินค้าด้วยชื่อหรือรหัส
"""

from __future__ import annotations

import argparse
from pathlib import Path

from storage import InventoryStore
from service import InventoryService


def cmd_search(args: argparse.Namespace) -> None:
    """ค้นแบบ partial match ผ่าน InventoryService"""
    service: InventoryService | None = getattr(args, "service", None)
    if service is None:
        from events import EventPublisher
        service = InventoryService(EventPublisher())
        store = getattr(args, "store", None) or InventoryStore(Path(args.data))
        store.load_into_service(service)

    results = service.search_products(args.query)

    if not results:
        print(f"ไม่พบสินค้าที่ตรงกับคำค้นหา '{args.query}' (ไม่พบข้อมูลสินค้าที่ค้นหา)")
        return

    results.sort(key=lambda i: getattr(i, "sku", getattr(i, "code", "")))
    name_w = max(len(i.name) for i in results) + 2
    name_w = max(name_w, 14)
    print(f"{'รหัส':<12}{'ชื่อสินค้า':<{name_w}}{'หมวดหมู่':<14}{'คงเหลือ':>10}  {'สถานะ'}")
    print("-" * (12 + name_w + 14 + 10 + 15))
    for item in results:
        code = getattr(item, "sku", getattr(item, "code", ""))
        cat = getattr(item, "category", "-")
        status = "[LOW STOCK]" if getattr(item, "is_low_stock", False) else "ปกติ"
        qty_str = f"{int(item.quantity)}" if item.quantity == int(item.quantity) else f"{item.quantity:.2f}"
        print(f"{code:<12}{item.name:<{name_w}}{cat:<14}{qty_str:>10}  {status}")
    print(f"\nพบ {len(results)} รายการ")


def register(subparsers: argparse._SubParsersAction) -> None:
    """เพิ่มคำสั่ง search เข้า argparse subparsers"""
    p = subparsers.add_parser("search", help="US-04: ค้นหาสินค้าด้วยชื่อหรือรหัส")
    p.add_argument("--query", required=True, help="คำค้นหา (ชื่อหรือรหัสสินค้า)")
    p.set_defaults(func=cmd_search)


