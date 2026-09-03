"""
models.py — โครงสร้างข้อมูลสินค้า (เชื่อมโยงกับ inventory-sdd/src/models.py)
"""

from __future__ import annotations
import sys
import os

src_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "inventory-sdd", "src")
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from models import Product, StockTransaction, TransactionType


class Item(Product):
    """Alias สำหรับความเข้ากันได้ย้อนหลัง (Item <-> Product)"""
    def __init__(self, code: str, name: str, quantity: float, updated_at: str = "",
                 category: str = "เครื่องเขียน", cost_price: float = 10.0,
                 sell_price: float = 20.0, unit: str = "ชิ้น", threshold: float = 5.0):
        super().__init__(
            sku=code,
            name=name,
            category=category,
            cost_price=cost_price,
            sell_price=sell_price,
            unit=unit,
            quantity=quantity,
            threshold=threshold,
        )
        self.updated_at = updated_at

    @property
    def code(self) -> str:
        return self.sku

    @code.setter
    def code(self, val: str) -> None:
        self.sku = val
