from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
import uuid

class TransactionType(Enum):
    """ประเภทการทำธุรกรรมสต็อก"""
    STOCK_IN = "STOCK_IN"
    STOCK_OUT = "STOCK_OUT"

@dataclass
class Product:
    """ข้อมูลสินค้า"""
    sku: str
    name: str
    category: str
    cost_price: float
    sell_price: float
    unit: str
    quantity: float = 0.0
    threshold: float = 0.0

    def __post_init__(self):
        """แปลงรูปแบบข้อมูลหลังจากสร้าง object (case-insensitive SKU, precision)"""
        self.sku = self.sku.upper()
        self.cost_price = round(float(self.cost_price), 2)
        self.sell_price = round(float(self.sell_price), 2)
        self.quantity = round(float(self.quantity), 2)
        self.threshold = round(float(self.threshold), 2)

    @property
    def is_low_stock(self) -> bool:
        """ตรวจสอบว่าสินค้านี้ถึงจุดสั่งซื้อหรือไม่ (quantity <= threshold)"""
        return self.quantity <= self.threshold

@dataclass
class StockTransaction:
    """ข้อมูลประวัติการทำรายการรับ-จ่ายสต็อก"""
    sku: str
    type: TransactionType
    quantity: float
    note: str = ""
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def __post_init__(self):
        """แปลงรูปแบบข้อมูลหลังจากสร้าง object"""
        self.sku = self.sku.upper()
        self.quantity = round(float(self.quantity), 2)
