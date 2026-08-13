"""
models.py — โครงสร้างข้อมูลสินค้า (Item)
"""

from __future__ import annotations

from dataclasses import dataclass, asdict


@dataclass
class Item:
    code: str
    name: str
    quantity: int
    updated_at: str

    def to_dict(self) -> dict:
        return asdict(self)
