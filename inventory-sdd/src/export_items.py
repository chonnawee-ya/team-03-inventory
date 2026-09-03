"""
commands/export_items.py — US-05: ส่งออกรายงานสต็อกเป็นไฟล์ CSV
"""

from __future__ import annotations

import argparse
from pathlib import Path

from storage import InventoryStore
from service import InventoryService


def cmd_export(args: argparse.Namespace) -> None:
    """ส่งออกรายงานสต็อกเป็น CSV ผ่าน InventoryService และ ExporterFactory"""
    service: InventoryService | None = getattr(args, "service", None)
    if service is None:
        from events import EventPublisher
        service = InventoryService(EventPublisher())
        store = getattr(args, "store", None) or InventoryStore(Path(args.data))
        store.load_into_service(service)

    output_path = Path(args.output)
    service.export_csv(str(output_path))
    products = service.list_products()
    print(f"ส่งออกรายงานสต็อก {len(products)} รายการ ไปที่ '{output_path}' เรียบร้อยแล้ว")


def register(subparsers: argparse._SubParsersAction) -> None:
    """เพิ่มคำสั่ง export เข้า argparse subparsers"""
    p = subparsers.add_parser("export", help="US-05: ส่งออกรายงานสต็อกเป็น CSV")
    p.add_argument("--output", default="stock_report.csv", help="ชื่อไฟล์ CSV ที่จะสร้าง")
    p.set_defaults(func=cmd_export)

