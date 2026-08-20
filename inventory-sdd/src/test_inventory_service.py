import unittest
import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
import os
import tempfile
from service import (
    InventoryService, 
    DuplicateSKUError, 
    InsufficientStockError, 
    InvalidInputTypeError, 
    NegativeValueError, 
    MissingRequiredFieldError, 
    ProductNotFoundError
)
from notifiers import NotifierFactory
from events import EventPublisher

class TestInventoryService(unittest.TestCase):
    def setUp(self):
        self.event_publisher = EventPublisher()
        self.email_notifier = NotifierFactory.create("email")
        self.sms_notifier = NotifierFactory.create("sms")
        self.event_publisher.subscribe("LOW_STOCK_ALERT", self.email_notifier)
        self.event_publisher.subscribe("STOCK_IN_SUCCESS", self.sms_notifier)
        self.event_publisher.subscribe("STOCK_OUT_SUCCESS", self.sms_notifier)
        self.service = InventoryService(self.event_publisher)

    def test_add_product_happy_path(self):
        p = self.service.add_product("SKU-001", "Test Product", "Cat A", 100, 150, "pcs", 10, 5)
        self.assertEqual(p.sku, "SKU-001")
        self.assertEqual(len(self.service.list_products()), 1)

    def test_add_product_duplicate_sku(self):
        self.service.add_product("SKU-001", "Test Product", "Cat A", 100, 150, "pcs", 10, 5)
        with self.assertRaises(DuplicateSKUError):
            self.service.add_product("sku-001", "Another", "Cat A", 100, 150, "pcs", 10, 5)

    def test_add_product_negative_value(self):
        with self.assertRaises(NegativeValueError):
            self.service.add_product("SKU-001", "Test Product", "Cat A", -10, 150, "pcs", 10, 5)
            
    def test_add_product_missing_field(self):
        with self.assertRaises(MissingRequiredFieldError):
            self.service.add_product("SKU-001", "Test Product", "Cat A", 100, 150, "pcs", 10, None)
            
    def test_stock_in(self):
        self.service.add_product("B-100", "B", "Cat", 10, 20, "pcs", 20, 5)
        self.service.stock_in("B-100", 10)
        self.assertEqual(self.service.products["B-100"].quantity, 30)

    def test_stock_out_insufficient(self):
        self.service.add_product("B-100", "B", "Cat", 10, 20, "pcs", 5, 2)
        with self.assertRaises(InsufficientStockError):
            self.service.stock_out("B-100", 10)

    def test_stock_out_boundary(self):
        self.service.add_product("B-100", "B", "Cat", 10, 20, "pcs", 5, 2)
        self.service.stock_out("B-100", 5)
        self.assertEqual(self.service.products["B-100"].quantity, 0)
        
    def test_stock_out_invalid_input(self):
        self.service.add_product("B-100", "B", "Cat", 10, 20, "pcs", 20, 5)
        with self.assertRaises(InvalidInputTypeError):
            self.service.stock_out("B-100", 0)

    def test_search(self):
        self.service.add_product("SKU-1", "สมุดบันทึกริมลวด A5", "A", 10, 20, "pcs", 10, 5)
        res = self.service.search_products("ริมลวด")
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0].sku, "SKU-1")

        res_none = self.service.search_products("XYZ")
        self.assertEqual(len(res_none), 0)
        
        res_all = self.service.search_products("")
        self.assertEqual(len(res_all), 1)

    def test_export_csv(self):
        self.service.add_product("SKU-1", "Test", "Cat A", 10, 20, "pcs", 10, 5)
        fd, temp_path = tempfile.mkstemp(suffix=".csv")
        os.close(fd)
        try:
            self.service.export_csv(temp_path)
            with open(temp_path, 'r', encoding='utf-8-sig') as f:
                content = f.read()
                self.assertIn("SKU-1", content)
                self.assertIn("Test", content)
        finally:
            os.remove(temp_path)

    def test_valuation_report(self):
        self.service.add_product("S1", "N1", "Cat A", 10, 20, "pcs", 3, 1)
        self.service.add_product("S2", "N2", "Cat B", 5, 10, "pcs", 2, 1)
        self.service.add_product("S3", "N3", "Cat A", 10, 20, "pcs", 2, 1)
        
        report = self.service.get_stock_valuation_report()
        cat_a = next(x for x in report if x["category"] == "Cat A")
        self.assertEqual(cat_a["total_items"], 5)
        self.assertEqual(cat_a["total_valuation"], 50)

if __name__ == '__main__':
    unittest.main()
