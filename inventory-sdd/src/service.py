import os
from typing import List, Dict, Optional
from models import Product, StockTransaction, TransactionType
from events import EventPublisher
from exporters import ExporterFactory

class InventoryError(Exception):
    pass

class DuplicateSKUError(InventoryError):
    pass

class InsufficientStockError(InventoryError):
    pass

class InvalidInputTypeError(InventoryError):
    pass

class NegativeValueError(InventoryError):
    pass

class MissingRequiredFieldError(InventoryError):
    pass

class ProductNotFoundError(InventoryError):
    pass

class InventoryService:
    """บริการจัดการสินค้าและสต็อก (Business Logic)"""
    def __init__(self, event_publisher: EventPublisher):
        """กำหนดค่าเริ่มต้นและรับ Dependency สำหรับ Event Publisher"""
        self.products: Dict[str, Product] = {}
        self.transactions: List[StockTransaction] = []
        self.event_publisher = event_publisher

    def add_product(self, sku: str, name: str, category: str, cost_price: float, sell_price: float, unit: str, quantity: float, threshold: float) -> Product:
        """เพิ่มสินค้าใหม่เข้าระบบ (US-02, FR-02)"""
        if not sku or not name or not category or not unit:
            raise MissingRequiredFieldError("กรุณาระบุข้อมูลให้ครบถ้วน")
            
        if threshold is None:
            raise MissingRequiredFieldError("กรุณาระบุ threshold")

        try:
            cost_price = float(cost_price)
            sell_price = float(sell_price)
            quantity = float(quantity)
            threshold = float(threshold)
        except ValueError:
            raise InvalidInputTypeError("ค่าต้องเป็นตัวเลข")

        if cost_price <= 0 or sell_price <= 0 or quantity < 0 or threshold < 0:
            raise NegativeValueError("ค่าต้องไม่ติดลบ และราคาต้องมากกว่า 0")
        
        sku_upper = sku.upper()
        if sku_upper in self.products:
            raise DuplicateSKUError("รหัสสินค้านี้มีอยู่ในระบบแล้ว")
            
        product = Product(sku, name, category, cost_price, sell_price, unit, quantity, threshold)
        self.products[sku_upper] = product
        return product

    def list_products(self) -> List[Product]:
        """ดึงรายการสินค้าทั้งหมด (US-01, FR-01)"""
        return list(self.products.values())

    def stock_in(self, sku: str, amount: float, note: str = "") -> None:
        """รับสินค้าเข้า (US-03, FR-03)"""
        sku_upper = sku.upper()
        if sku_upper not in self.products:
            raise ProductNotFoundError("ไม่พบข้อมูลสินค้าที่ค้นหา")
            
        try:
            amount = float(amount)
        except ValueError:
            raise InvalidInputTypeError("จำนวนต้องเป็นตัวเลขที่มากกว่า 0")
            
        if amount <= 0:
            raise InvalidInputTypeError("จำนวนต้องเป็นตัวเลขที่มากกว่า 0")
            
        product = self.products[sku_upper]
        product.quantity += amount
        
        transaction = StockTransaction(sku=sku_upper, type=TransactionType.STOCK_IN, quantity=amount, note=note)
        self.transactions.append(transaction)
        
        self.event_publisher.publish("STOCK_IN_SUCCESS", {
            "sku": sku_upper,
            "amount": amount,
            "quantity": product.quantity
        })

    def stock_out(self, sku: str, amount: float, note: str = "") -> None:
        """จ่ายสินค้าออก (US-03, FR-04, FR-05, FR-06)"""
        sku_upper = sku.upper()
        if sku_upper not in self.products:
            raise ProductNotFoundError("ไม่พบข้อมูลสินค้าที่ค้นหา")
            
        try:
            amount = float(amount)
        except ValueError:
            raise InvalidInputTypeError("จำนวนต้องเป็นตัวเลขที่มากกว่า 0")
            
        if amount <= 0:
            raise InvalidInputTypeError("จำนวนต้องเป็นตัวเลขที่มากกว่า 0")
            
        product = self.products[sku_upper]
        
        if product.quantity < amount:
            raise InsufficientStockError("จำนวนคงเหลือไม่เพียงพอสำหรับการตัดจ่าย")
            
        product.quantity -= amount
        
        transaction = StockTransaction(sku=sku_upper, type=TransactionType.STOCK_OUT, quantity=amount, note=note)
        self.transactions.append(transaction)
        
        # ส่งแจ้งเตือนยืนยันการทำรายการ (SMS) ทุกครั้ง
        self.event_publisher.publish("STOCK_OUT_SUCCESS", {
            "sku": sku_upper,
            "amount": amount,
            "quantity": product.quantity
        })
        
        # ส่งแจ้งเตือนสต็อกต่ำ (Email) ถ้ายอดคงเหลือ <= จุดสั่งซื้อ
        if product.quantity <= product.threshold:
            self.event_publisher.publish("LOW_STOCK_ALERT", {
                "sku": sku_upper,
                "quantity": product.quantity,
                "threshold": product.threshold
            })

    def search_products(self, query: str) -> List[Product]:
        """ค้นหาสินค้าด้วยรหัสหรือชื่อ (US-04, FR-07)"""
        if not query or query.strip() == "":
            return self.list_products()
            
        query_lower = query.lower()
        results = []
        for p in self.products.values():
            if query_lower in p.sku.lower() or query_lower in p.name.lower():
                results.append(p)
        return results

    def get_stock_valuation_report(self) -> List[Dict]:
        """รายงานมูลค่าสต็อกแยกตามหมวดหมู่ (US-06, FR-08)"""
        report = {}
        for p in self.products.values():
            cat = p.category
            if cat not in report:
                report[cat] = {"category": cat, "total_items": 0.0, "total_valuation": 0.0}
            report[cat]["total_items"] += p.quantity
            report[cat]["total_valuation"] += p.quantity * p.cost_price
            
        # ปัดเศษ
        for v in report.values():
            v["total_items"] = round(v["total_items"], 2)
            v["total_valuation"] = round(v["total_valuation"], 2)
            
        return list(report.values())

    def export_csv(self, filename: str, products: Optional[List[Product]] = None) -> None:
        """ส่งออกรายการสินค้าเป็น CSV (US-05, FR-09)"""
        if products is None:
            products = self.list_products()
            
        exporter = ExporterFactory.create("csv")
        exporter.export(filename, products)
