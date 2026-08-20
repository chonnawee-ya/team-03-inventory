import csv
from typing import Protocol, List
from models import Product

class Exporter(Protocol):
    """โปรโตคอลสำหรับการส่งออกข้อมูล (SRP)"""
    def export(self, filename: str, products: List[Product]) -> None:
        ...

class CSVExporter:
    """คลาสสำหรับการส่งออกข้อมูลในรูปแบบ CSV"""
    def export(self, filename: str, products: List[Product]) -> None:
        # เข้ารหัสแบบ utf-8-sig เพื่อให้ได้ BOM
        with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            writer.writerow(['SKU', 'Name', 'Category', 'Cost Price', 'Sell Price', 'Unit', 'Quantity', 'Threshold'])
            for p in products:
                writer.writerow([p.sku, p.name, p.category, p.cost_price, p.sell_price, p.unit, p.quantity, p.threshold])

class ExporterFactory:
    """Factory Pattern สำหรับสร้าง Exporter แบบต่างๆ"""
    @staticmethod
    def create(exporter_type: str) -> Exporter:
        if exporter_type.lower() == "csv":
            return CSVExporter()
        raise ValueError(f"ไม่รู้จักประเภทการส่งออก: {exporter_type}")
