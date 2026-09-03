#!/usr/bin/env python3
"""
test_all_features.py — ชุดทดสอบครอบคลุมทุกฟังก์ชันของระบบ Inventory
ครอบคลุม User Stories ทั้งหมด (US-01 ถึง US-06) และ Acceptance Criteria (AC-01 ถึง AC-07)
รวมถึงทดสอบทั้งระดับ Service Logic และระดับ CLI End-to-End ผ่าน main.py
"""

from __future__ import annotations

import csv
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

# เพิ่ม path สำหรับ import โมดูล
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "inventory-sdd", "src"))
from events import EventPublisher
from models import Product, StockTransaction, TransactionType
from notifiers import NotifierFactory
from service import (
    InventoryService,
    DuplicateSKUError,
    InsufficientStockError,
    InvalidInputTypeError,
    NegativeValueError,
    ProductNotFoundError,
)


class TestServiceAllFeatures(unittest.TestCase):
    """ทดสอบ Logic ระดับ Service ครบทุกฟังก์ชัน (US-01 ถึง US-06)"""

    def setUp(self):
        self.event_publisher = EventPublisher()
        self.received_events = []

        # สร้าง Mock Subscriber สำหรับดักจับ Event
        class MockHandler:
            def __init__(handler_self, event_list):
                handler_self.event_list = event_list
            def handle_event(handler_self, event_type, data):
                handler_self.event_list.append((event_type, data))

        self.handler = MockHandler(self.received_events)
        self.event_publisher.subscribe("LOW_STOCK_ALERT", self.handler)
        self.event_publisher.subscribe("STOCK_IN_SUCCESS", self.handler)
        self.event_publisher.subscribe("STOCK_OUT_SUCCESS", self.handler)

        self.service = InventoryService(self.event_publisher)

    # === US-01: ดูรายการสินค้า (List Products) ===
    def test_us01_list_empty(self):
        """US-01 / AC-02: เมื่อไม่มีสินค้าในระบบ คืน list ว่าง"""
        self.assertEqual(len(self.service.list_products()), 0)

    def test_us01_list_multiple_items(self):
        """US-01 / AC-02: แสดงรายการสินค้าครบทุกรายการและตรวจสถานะ low_stock"""
        self.service.add_product("A01", "ปากกา", "เครื่องเขียน", 10, 20, "ชิ้น", 3, 5)
        self.service.add_product("A02", "ดินสอ", "เครื่องเขียน", 5, 10, "ชิ้น", 20, 5)
        products = self.service.list_products()
        self.assertEqual(len(products), 2)
        p_a01 = self.service.products["A01"]
        p_a02 = self.service.products["A02"]
        self.assertTrue(p_a01.is_low_stock)   # 3 <= 5
        self.assertFalse(p_a02.is_low_stock)  # 20 > 5

    # === US-02: เพิ่มสินค้าใหม่ (Add Product) ===
    def test_us02_add_product_success(self):
        """US-02 / AC-03: เพิ่มสินค้าใหม่สำเร็จ พร้อมแปลง SKU เป็นตัวพิมพ์ใหญ่"""
        p = self.service.add_product(
            sku="sku-wire-01",
            name="สายไฟ VAF",
            category="อุปกรณ์ไฟฟ้า",
            cost_price=50.0,
            sell_price=75.0,
            unit="ม้วน",
            quantity=100.0,
            threshold=15.0,
        )
        self.assertEqual(p.sku, "SKU-WIRE-01")
        self.assertIn("SKU-WIRE-01", self.service.products)
        self.assertEqual(p.quantity, 100.0)

    def test_us02_duplicate_sku_rejected(self):
        """US-02 / AC-03: ปฏิเสธรหัสสินค้าซ้ำ (case-insensitive)"""
        self.service.add_product("SKU-01", "สมุด", "เครื่องเขียน", 10, 20, "เล่ม", 10, 5)
        with self.assertRaises(DuplicateSKUError):
            self.service.add_product("sku-01", "สมุดอีกเล่ม", "เครื่องเขียน", 10, 20, "เล่ม", 5, 2)

    def test_us02_negative_or_zero_price_rejected(self):
        """US-02 / AC-03: ปฏิเสธราคาทุนหรือราคาขาย <= 0 หรือจำนวนติดลบ"""
        with self.assertRaises(NegativeValueError):
            self.service.add_product("P1", "A", "C", 0, 20, "ชิ้น", 10, 5)
        with self.assertRaises(NegativeValueError):
            self.service.add_product("P2", "B", "C", 10, -5, "ชิ้น", 10, 5)
        with self.assertRaises(NegativeValueError):
            self.service.add_product("P3", "C", "C", 10, 20, "ชิ้น", -1, 5)

    # === US-03: ปรับปรุงสต็อก รับเข้า / ตัดจ่าย (Stock In & Stock Out) ===
    def test_us03_stock_in(self):
        """US-03 / AC-04: รับสินค้าเข้า เพิ่มยอดคงเหลือ และยิง event STOCK_IN_SUCCESS"""
        self.service.add_product("B-100", "ปากกาน้ำเงิน", "เครื่องเขียน", 10, 20, "ชิ้น", 20, 5)
        self.service.stock_in("B-100", 10, note="สั่งซื้อเพิ่ม")
        self.assertEqual(self.service.products["B-100"].quantity, 30)
        self.assertEqual(len(self.received_events), 1)
        self.assertEqual(self.received_events[0][0], "STOCK_IN_SUCCESS")
        self.assertEqual(self.received_events[0][1]["amount"], 10)

    def test_us03_stock_out_notifications_ac01(self):
        """US-03 / AC-01: ตัดจ่ายสินค้าจนต่ำกว่า threshold ยิงทั้ง SMS และ Email"""
        self.service.add_product("SKU-WIRE-01", "สายไฟ VAF", "อุปกรณ์ไฟฟ้า", 50, 75, "ม้วน", 20, 15)
        # ตัดจ่าย 8 -> เหลือ 12 (<= 15)
        self.service.stock_out("SKU-WIRE-01", 8, note="ขายให้ลูกค้า")
        self.assertEqual(self.service.products["SKU-WIRE-01"].quantity, 12)

        event_types = [e[0] for e in self.received_events]
        self.assertIn("STOCK_OUT_SUCCESS", event_types)
        self.assertIn("LOW_STOCK_ALERT", event_types)

    def test_us03_stock_out_boundary_threshold(self):
        """US-03 / AC-01: ตัดจ่ายจนสต็อกเท่ากับ threshold พอดี ยิง LOW_STOCK_ALERT"""
        self.service.add_product("SKU-WIRE-01", "สายไฟ", "อุปกรณ์ไฟฟ้า", 50, 75, "ม้วน", 20, 15)
        # ตัดจ่าย 5 -> เหลือ 15 (== 15)
        self.service.stock_out("SKU-WIRE-01", 5)
        self.assertEqual(self.service.products["SKU-WIRE-01"].quantity, 15)
        event_types = [e[0] for e in self.received_events]
        self.assertIn("LOW_STOCK_ALERT", event_types)

    def test_us03_stock_out_insufficient_stock(self):
        """US-03 / AC-04: ปฏิเสธการตัดจ่ายเมื่อยอดสินค้าไม่เพียงพอ"""
        self.service.add_product("B-100", "ปากกา", "เครื่องเขียน", 10, 20, "ชิ้น", 5, 2)
        with self.assertRaises(InsufficientStockError):
            self.service.stock_out("B-100", 10)
        self.assertEqual(self.service.products["B-100"].quantity, 5)

    def test_us03_stock_out_not_found(self):
        """US-03: ปฏิเสธเมื่อรหัสสินค้าไม่มีในระบบ"""
        with self.assertRaises(ProductNotFoundError):
            self.service.stock_out("NON_EXIST", 5)

    # === US-04: ค้นหาสินค้า (Search Products) ===
    def test_us04_search_partial_match(self):
        """US-04 / AC-05: ค้นหาด้วยชื่อหรือรหัสแบบ partial match, case-insensitive"""
        self.service.add_product("A001", "สมุดบันทึกริมลวด A5", "เครื่องเขียน", 20, 35, "เล่ม", 10, 5)
        self.service.add_product("A002", "ดินสอกด 0.5", "เครื่องเขียน", 15, 25, "ด้าม", 20, 5)

        res_name = self.service.search_products("ริมลวด")
        self.assertEqual(len(res_name), 1)
        self.assertEqual(res_name[0].sku, "A001")

        res_code = self.service.search_products("a002")
        self.assertEqual(len(res_code), 1)
        self.assertEqual(res_code[0].name, "ดินสอกด 0.5")

        res_empty = self.service.search_products("")
        self.assertEqual(len(res_empty), 2)

        res_none = self.service.search_products("XYZ999")
        self.assertEqual(len(res_none), 0)

    # === US-05: ส่งออกรายงาน CSV (Export CSV) ===
    def test_us05_export_csv(self):
        """US-05 / AC-06: ส่งออกข้อมูลสินค้าเป็น CSV พร้อม header ครบถ้วนและ UTF-8 BOM"""
        self.service.add_product("SKU-01", "สินค้าทดสอบ", "เครื่องเขียน", 10, 20, "ชิ้น", 15, 5)
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
            temp_path = f.name
        try:
            self.service.export_csv(temp_path)
            with open(temp_path, "r", encoding="utf-8-sig") as f:
                reader = list(csv.reader(f))
            self.assertEqual(reader[0], ['SKU', 'Name', 'Category', 'Cost Price', 'Sell Price', 'Unit', 'Quantity', 'Threshold'])
            self.assertEqual(reader[1][0], "SKU-01")
            self.assertEqual(reader[1][1], "สินค้าทดสอบ")
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    # === US-06: รายงานมูลค่าสต็อก (Stock Valuation Report) ===
    def test_us06_valuation_report(self):
        """US-06 / AC-07: คำนวณสรุปยอดคงเหลือและมูลค่าสต็อกแยกตามหมวดหมู่"""
        self.service.add_product("P1", "ปากกา", "เครื่องเขียน", 10.0, 20.0, "ด้าม", 5, 2)
        self.service.add_product("P2", "ดินสอ", "เครื่องเขียน", 5.0, 10.0, "แท่ง", 10, 3)
        self.service.add_product("W1", "สายไฟ", "อุปกรณ์ไฟฟ้า", 100.0, 150.0, "ม้วน", 2, 1)

        report = self.service.get_stock_valuation_report()
        rep_map = {r["category"]: r for r in report}

        # เครื่องเขียน: 5 + 10 = 15 ชิ้น, มูลค่า (5*10) + (10*5) = 100.0 บาท
        self.assertIn("เครื่องเขียน", rep_map)
        self.assertEqual(rep_map["เครื่องเขียน"]["total_items"], 15.0)
        self.assertEqual(rep_map["เครื่องเขียน"]["total_valuation"], 100.0)

        # อุปกรณ์ไฟฟ้า: 2 ชิ้น, มูลค่า 2*100 = 200.0 บาท
        self.assertIn("อุปกรณ์ไฟฟ้า", rep_map)
        self.assertEqual(rep_map["อุปกรณ์ไฟฟ้า"]["total_items"], 2.0)
        self.assertEqual(rep_map["อุปกรณ์ไฟฟ้า"]["total_valuation"], 200.0)


class TestCLIAllCommands(unittest.TestCase):
    """ทดสอบการทำงานผ่าน main.py Command Line ครบทุกคำสั่ง (US-01 ถึง US-06)"""

    def setUp(self):
        self.tmpdir = Path(tempfile.mkdtemp())
        self.data_file = self.tmpdir / "items.json"
        self.script = Path(__file__).parent / "main.py"

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def run_cli(self, *args):
        env = os.environ.copy()
        env["PYTHONUTF8"] = "1"
        return subprocess.run(
            [sys.executable, str(self.script), "--data", str(self.data_file), *args],
            capture_output=True,
            text=True,
            encoding="utf-8",
            env=env,
        )

    def test_cli_flow_all_commands(self):
        """ทดสอบ Flow ครบทุกคำสั่ง: add -> list -> update -> search -> report -> export"""
        # 1. ทดสอบ list ตอนคลังว่าง
        res = self.run_cli("list")
        self.assertIn("ยังไม่มีสินค้าในระบบ", res.stdout)

        # 2. ทดสอบ add สินค้า
        res = self.run_cli("add", "--code", "A001", "--name", "ปากกาน้ำเงิน", "--qty", "20", "--cost", "10", "--price", "20", "--threshold", "10")
        self.assertEqual(res.returncode, 0)
        self.assertIn("เพิ่มสินค้า 'ปากกาน้ำเงิน' (รหัส A001)", res.stdout)

        # เพิ่มสินค้าตัวที่ 2
        self.run_cli("add", "--code", "A002", "--name", "สายไฟ VAF", "--category", "อุปกรณ์ไฟฟ้า", "--qty", "5", "--cost", "50", "--price", "80", "--threshold", "2")

        # 3. ทดสอบ list เมื่อมีสินค้า
        res = self.run_cli("list")
        self.assertIn("A001", res.stdout)
        self.assertIn("A002", res.stdout)
        self.assertIn("ปากกาน้ำเงิน", res.stdout)
        self.assertIn("สายไฟ VAF", res.stdout)

        # 4. ทดสอบ update: จ่ายออกจนต่ำกว่า threshold (20 - 15 = 5 <= 10)
        res = self.run_cli("update", "--code", "A001", "--delta", "-15", "--reason", "ขายให้ลูกค้า")
        self.assertEqual(res.returncode, 0)
        self.assertIn("[SMS]", res.stdout)
        self.assertIn("[Email]", res.stdout)  # ยิงแจ้งเตือน low stock alert
        self.assertIn("จ่ายออก", res.stdout)

        # 5. ตรวจสอบ list ว่า A001 ขึ้น [LOW STOCK]
        res = self.run_cli("list")
        self.assertIn("[LOW STOCK]", res.stdout)

        # 6. ทดสอบ search
        res = self.run_cli("search", "--query", "สายไฟ")
        self.assertIn("A002", res.stdout)
        self.assertNotIn("A001", res.stdout)

        # 7. ทดสอบ report (US-06)
        res = self.run_cli("report")
        self.assertEqual(res.returncode, 0)
        self.assertIn("เครื่องเขียน", res.stdout)
        self.assertIn("อุปกรณ์ไฟฟ้า", res.stdout)
        self.assertIn("รวมทั้งหมด", res.stdout)

        # 8. ทดสอบ export (US-05)
        csv_file = self.tmpdir / "exported_stock.csv"
        res = self.run_cli("export", "--output", str(csv_file))
        self.assertEqual(res.returncode, 0)
        self.assertTrue(csv_file.exists())
        csv_content = csv_file.read_text(encoding="utf-8-sig")
        self.assertIn("SKU,Name,Category", csv_content)
        self.assertIn("A001", csv_content)
        self.assertIn("A002", csv_content)


if __name__ == "__main__":
    unittest.main(verbosity=2)
