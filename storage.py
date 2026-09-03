"""
storage.py — อ่าน/เขียนข้อมูลสินค้าในไฟล์ JSON
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Optional, List, TYPE_CHECKING

src_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "inventory-sdd", "src")
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from models import Product, Item

if TYPE_CHECKING:
    from service import InventoryService

DEFAULT_DATA_FILE = Path("items.json")


class InventoryStore:
    """อ่าน/เขียนข้อมูลสินค้าในไฟล์ JSON"""

    def __init__(self, path: Path | str = DEFAULT_DATA_FILE):
        self.path = Path(path)

    def _dict_to_product(self, entry: dict) -> Product:
        sku = entry.get("sku") or entry.get("code") or ""
        name = entry.get("name", "")
        category = entry.get("category", "เครื่องเขียน")
        cost_price = float(entry.get("cost_price", 10.0))
        sell_price = float(entry.get("sell_price", 20.0))
        unit = entry.get("unit", "ชิ้น")
        quantity = float(entry.get("quantity", 0.0))
        threshold = float(entry.get("threshold", 5.0))
        return Product(
            sku=sku,
            name=name,
            category=category,
            cost_price=cost_price,
            sell_price=sell_price,
            unit=unit,
            quantity=quantity,
            threshold=threshold,
        )

    def load_products(self) -> list[Product]:
        """อ่านไฟล์และคืน list ของ Product"""
        if not self.path.exists():
            return []
        try:
            raw = json.loads(self.path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            raise SystemExit(f"เกิดข้อผิดพลาด: ไฟล์ {self.path} ไม่ใช่ JSON ที่ถูกต้อง")
        return [self._dict_to_product(entry) for entry in raw]

    def save_products(self, products: list[Product]) -> None:
        """บันทึก list ของ Product ลงไฟล์ JSON"""
        data = [p.to_dict() for p in products]
        self.path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    def load_into_service(self, service: InventoryService) -> None:
        """โหลดสินค้าจากไฟล์ JSON เข้าสู่ InventoryService"""
        products = self.load_products()
        for p in products:
            service.products[p.sku.upper()] = p

    def save_from_service(self, service: InventoryService) -> None:
        """บันทึกสินค้าจาก InventoryService ลงไฟล์ JSON"""
        self.save_products(service.list_products())

    def load_items(self) -> list[Item]:
        """เข้ากันได้ย้อนหลัง: คืน list ของ Item"""
        if not self.path.exists():
            return []
        try:
            raw = json.loads(self.path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            raise SystemExit(f"เกิดข้อผิดพลาด: ไฟล์ {self.path} ไม่ใช่ JSON ที่ถูกต้อง")
        items = []
        for entry in raw:
            p = self._dict_to_product(entry)
            item = Item(
                code=p.sku,
                name=p.name,
                quantity=p.quantity,
                updated_at=entry.get("updated_at", ""),
                category=p.category,
                cost_price=p.cost_price,
                sell_price=p.sell_price,
                unit=p.unit,
                threshold=p.threshold,
            )
            items.append(item)
        return items

    def save_items(self, items: list[Item]) -> None:
        """เข้ากันได้ย้อนหลัง: บันทึก Item"""
        data = [item.to_dict() for item in items]
        self.path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    def find_by_code(self, items: list[Item] | list[Product], code: str) -> Optional[Item | Product]:
        for item in items:
            item_code = getattr(item, "code", None) or getattr(item, "sku", None)
            if item_code and item_code.lower() == code.lower():
                return item
        return None
