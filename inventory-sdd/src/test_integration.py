import unittest
import sys
import os
import tempfile
import csv

# เพื่อให้รองรับภาษาไทยใน Windows Console
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

# เพิ่ม path ให้สามารถ import module จาก src ได้สะดวก
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from models import Product, TransactionType
from service import InventoryService
from events import EventPublisher
from notifiers import NotifierFactory

class MockEmailNotifier:
    """Mock สำหรับเก็บประวัติการส่ง Email เพื่อใช้ในการทดสอบ"""
    def __init__(self):
        self.sent_messages = []
        
    def handle_event(self, event_type: str, data: dict) -> None:
        if event_type == "LOW_STOCK_ALERT":
            msg = f"แจ้งเตือนสต็อกต่ำ: {data['sku']} คงเหลือ {data['quantity']}"
            self.sent_messages.append(msg)

class MockSMSNotifier:
    """Mock สำหรับเก็บประวัติการส่ง SMS เพื่อใช้ในการทดสอบ"""
    def __init__(self):
        self.sent_messages = []
        
    def handle_event(self, event_type: str, data: dict) -> None:
        if event_type == "STOCK_IN_SUCCESS":
            msg = f"รับเข้า {data['sku']}"
            self.sent_messages.append(msg)
        elif event_type == "STOCK_OUT_SUCCESS":
            msg = f"ตัดจ่าย {data['sku']}"
            self.sent_messages.append(msg)


class TestInventoryIntegration(unittest.TestCase):
    def setUp(self):
        # 1. Setup Architecture: Event Publisher + Notifiers
        self.event_publisher = EventPublisher()
        
        self.email_mock = MockEmailNotifier()
        self.sms_mock = MockSMSNotifier()
        
        self.event_publisher.subscribe("LOW_STOCK_ALERT", self.email_mock)
        self.event_publisher.subscribe("STOCK_IN_SUCCESS", self.sms_mock)
        self.event_publisher.subscribe("STOCK_OUT_SUCCESS", self.sms_mock)
        
        # 2. Setup Service
        self.service = InventoryService(self.event_publisher)

    def test_full_business_flow(self):
        """ทดสอบ Flow การทำงานหลักตั้งแต่ต้นจนจบ (Integration Test)"""
        
        # 1. การเพิ่มสินค้า (Add Products)
        p1 = self.service.add_product("P-001", "สินค้า A", "หมวด 1", 100, 150, "ชิ้น", 10, 5)
        p2 = self.service.add_product("P-002", "สินค้า B", "หมวด 2", 200, 250, "ชิ้น", 20, 10)
        
        self.assertEqual(len(self.service.list_products()), 2)
        self.assertFalse(p1.is_low_stock)
        self.assertFalse(p2.is_low_stock)
        
        # 2. การรับสินค้าเข้า (Stock In)
        self.service.stock_in("P-001", 15, "เติมของ")
        self.assertEqual(self.service.products["P-001"].quantity, 25)
        self.assertEqual(len(self.sms_mock.sent_messages), 1)
        self.assertIn("รับเข้า P-001", self.sms_mock.sent_messages[-1])
        
        # 3. การจ่ายสินค้าออกจนสต็อกต่ำ (Stock Out -> Low Stock Alert)
        # P-001 เดิมมี 25, threshold = 5, จ่ายออก 20 เหลือ 5 (พอดี threshold)
        self.service.stock_out("P-001", 20, "ขาย")
        
        self.assertEqual(self.service.products["P-001"].quantity, 5)
        self.assertTrue(self.service.products["P-001"].is_low_stock)
        
        # ตรวจสอบว่ามี SMS ส่งออกจากการตัดจ่าย
        self.assertEqual(len(self.sms_mock.sent_messages), 2)
        self.assertIn("ตัดจ่าย P-001", self.sms_mock.sent_messages[-1])
        
        # ตรวจสอบว่ามี Email แจ้งเตือน Low Stock ส่งออก
        self.assertEqual(len(self.email_mock.sent_messages), 1)
        self.assertIn("แจ้งเตือนสต็อกต่ำ: P-001 คงเหลือ 5.0", self.email_mock.sent_messages[-1])
        
        # 4. ทดสอบรายงาน (Report)
        report = self.service.get_stock_valuation_report()
        # หมวด 1 มี P-001: จำนวน 5 * ทุน 100 = 500
        # หมวด 2 มี P-002: จำนวน 20 * ทุน 200 = 4000
        self.assertEqual(len(report), 2)
        for cat_report in report:
            if cat_report["category"] == "หมวด 1":
                self.assertEqual(cat_report["total_items"], 5)
                self.assertEqual(cat_report["total_valuation"], 500)
            elif cat_report["category"] == "หมวด 2":
                self.assertEqual(cat_report["total_items"], 20)
                self.assertEqual(cat_report["total_valuation"], 4000)
                
        # 5. ทดสอบการ Export CSV (Integration กับ ExporterFactory)
        with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as tmp:
            tmp_name = tmp.name
            
        try:
            self.service.export_csv(tmp_name)
            
            # ตรวจสอบไฟล์ CSV
            with open(tmp_name, 'r', encoding='utf-8-sig') as f:
                reader = csv.reader(f)
                rows = list(reader)
                self.assertEqual(len(rows), 3) # Header + 2 สินค้า
                self.assertEqual(rows[0], ['SKU', 'Name', 'Category', 'Cost Price', 'Sell Price', 'Unit', 'Quantity', 'Threshold'])
                self.assertEqual(rows[1][0], "P-001")
                self.assertEqual(rows[2][0], "P-002")
        finally:
            if os.path.exists(tmp_name):
                os.remove(tmp_name)

if __name__ == '__main__':
    unittest.main()
