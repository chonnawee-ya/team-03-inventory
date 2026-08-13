"""
storage.py — อ่าน/เขียนข้อมูลสินค้าในไฟล์ JSON
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from models import Item

DEFAULT_DATA_FILE = Path("items.json")


class InventoryStore:
    """อ่าน/เขียนข้อมูลสินค้าในไฟล์ JSON"""

    def __init__(self, path: Path = DEFAULT_DATA_FILE):
        self.path = path

    def load_items(self) -> list[Item]:
        """AC-1/AC-2 ของ US-01: อ่านไฟล์ ถ้าไม่มีไฟล์หรือว่าง ให้คืน list ว่าง"""
        if not self.path.exists():
            return []
        try:
            raw = json.loads(self.path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            raise SystemExit(f"เกิดข้อผิดพลาด: ไฟล์ {self.path} ไม่ใช่ JSON ที่ถูกต้อง")
        return [Item(**entry) for entry in raw]

    def save_items(self, items: list[Item]) -> None:
        data = [item.to_dict() for item in items]
        self.path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    def find_by_code(self, items: list[Item], code: str) -> Optional[Item]:
        for item in items:
            if item.code.lower() == code.lower():
                return item
        return None
