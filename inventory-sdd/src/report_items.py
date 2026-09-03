"""
commands/report_items.py — US-06: รายงานสรุปมูลค่าสต็อกคงเหลือแยกตามหมวดหมู่
"""

from __future__ import annotations

import argparse
from pathlib import Path

from storage import InventoryStore
from service import InventoryService


def cmd_report(args: argparse.Namespace) -> None:
    """แสดงรายงานสรุปมูลค่าสต็อกแยกตามหมวดหมู่ (US-06 / FR-08 / AC-07)"""
    service: InventoryService | None = getattr(args, "service", None)
    if service is None:
        from events import EventPublisher
        service = InventoryService(EventPublisher())
        store = getattr(args, "store", None) or InventoryStore(Path(args.data))
        store.load_into_service(service)

    report = service.get_stock_valuation_report()

    if not report:
        print("ไม่มีข้อมูลสำหรับสร้างรายงาน")
        return

    report.sort(key=lambda r: r["category"])
    cat_w = max(len(r["category"]) for r in report) + 4
    cat_w = max(cat_w, 16)

    print(f"{'หมวดหมู่':<{cat_w}}{'จำนวนคงเหลือรวม':>18}{'มูลค่าสต็อกรวม (บาท)':>24}")
    print("-" * (cat_w + 18 + 24))

    total_items = 0.0
    total_val = 0.0

    for r in report:
        cat = r["category"]
        items_cnt = r["total_items"]
        val = r["total_valuation"]
        total_items += items_cnt
        total_val += val

        items_str = f"{int(items_cnt)}" if items_cnt == int(items_cnt) else f"{items_cnt:.2f}"
        print(f"{cat:<{cat_w}}{items_str:>18}{val:>24,.2f}")

    print("-" * (cat_w + 18 + 24))
    total_items_str = f"{int(total_items)}" if total_items == int(total_items) else f"{total_items:.2f}"
    print(f"{'รวมทั้งหมด':<{cat_w}}{total_items_str:>18}{total_val:>24,.2f}")


def register(subparsers: argparse._SubParsersAction) -> None:
    """เพิ่มคำสั่ง report เข้า argparse subparsers"""
    p = subparsers.add_parser("report", help="US-06: รายงานสรุปมูลค่าสต็อกแยกตามหมวดหมู่")
    p.set_defaults(func=cmd_report)
