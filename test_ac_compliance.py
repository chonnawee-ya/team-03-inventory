import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'inventory-sdd', 'src')))

import unittest
from models import Product
from service import InventoryService, NegativeValueError
from notifiers import NotifierFactory
from events import EventPublisher

class TestACCompliance(unittest.TestCase):
    def setUp(self):
        self.event_publisher = EventPublisher()
        self.email_notifier = NotifierFactory.create("email")
        self.sms_notifier = NotifierFactory.create("sms")
        self.event_publisher.subscribe("LOW_STOCK_ALERT", self.email_notifier)
        self.event_publisher.subscribe("STOCK_IN_SUCCESS", self.sms_notifier)
        self.event_publisher.subscribe("STOCK_OUT_SUCCESS", self.sms_notifier)
        self.service = InventoryService(self.event_publisher)

    def test_ac02_is_low_stock_property(self):
        p = Product("SKU-1", "A", "Cat", 10, 20, "pcs", 10, 15)
        self.assertTrue(hasattr(p, 'is_low_stock'), "Context gap: Product doesn't have is_low_stock property for UI")
        self.assertTrue(p.is_low_stock)
        
        p.quantity = 20
        self.assertFalse(p.is_low_stock)

    def test_ac03_price_validation(self):
        # 0 price should be rejected based on AC "ราคาทุน > 0, ราคาขาย > 0"
        with self.assertRaises(NegativeValueError, msg="Spec ambiguity/Context gap: 0 price was allowed"):
            self.service.add_product("SKU-2", "B", "Cat", 0, 20, "pcs", 10, 5)

if __name__ == '__main__':
    unittest.main()
