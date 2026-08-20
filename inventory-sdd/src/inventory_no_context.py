import datetime
import sys

# บังคับให้ stdout/stderr เป็น UTF-8 กันปัญหา UnicodeEncodeError บน Windows (สำหรับพิมพ์ภาษาไทย)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

class Product:
    """ข้อมูลสินค้าพื้นฐานตาม Schema"""
    def __init__(self, sku: str, name: str, quantity: float, threshold: float):
        self.sku = sku.upper()
        self.name = name
        self.quantity = float(quantity)
        self.threshold = float(threshold)

class NotificationService:
    """จำลองการส่งการแจ้งเตือน (Mock Notifications) ตาม NFR-04"""
    
    @staticmethod
    def send_sms(message: str):
        """ส่ง SMS ยืนยันการทำรายการสำเร็จ (FR-06)"""
        print(f"\n[SMS] 📱 ยืนยันการทำรายการ:")
        print(f"> {message}")

    @staticmethod
    def send_email(sku: str, product_name: str, current_qty: float, threshold: float):
        """ส่ง Email แจ้งเตือนเมื่อสต็อกต่ำกว่าหรือเท่ากับ threshold (FR-05)"""
        print(f"\n[EMAIL] 📧 แจ้งเตือนสต็อกต่ำ (Low-Stock Alert)!")
        print(f"Subject: ⚠️ สินค้าใกล้หมด: {sku} - {product_name}")
        print(f"Body: ")
        print(f"  แจ้งเตือน: สินค้า {sku} ({product_name}) มีจำนวนคงเหลือน้อยกว่าหรือเท่ากับจุดสั่งซื้อ")
        print(f"  - คงเหลือปัจจุบัน: {current_qty}")
        print(f"  - จุดสั่งซื้อ (Threshold): {threshold}")
        print(f"  กรุณาดำเนินการสั่งซื้อเพิ่มเติม")

class InventorySystem:
    def __init__(self):
        self.products = {}

    def add_product(self, product: Product):
        self.products[product.sku] = product

    def stock_out(self, sku: str, amount: float):
        """บันทึกตัดจ่ายสินค้าออก (US-03, FR-04)"""
        sku = sku.upper()
        
        if sku not in self.products:
            raise ValueError("PRODUCT_NOT_FOUND")
            
        product = self.products[sku]
        
        if amount <= 0:
            raise ValueError("INVALID_INPUT_TYPE: จำนวนต้องเป็นตัวเลขที่มากกว่า 0")
            
        if product.quantity < amount:
            raise ValueError("INSUFFICIENT_STOCK: จำนวนคงเหลือไม่เพียงพอสำหรับการตัดจ่าย")
            
        # หักยอดสต็อก
        product.quantity -= amount
        
        # 1. ส่ง SMS ยืนยันการทำรายการสำเร็จเสมอ (FR-06)
        NotificationService.send_sms(
            f"จ่ายสินค้า {sku} จำนวน {amount} หน่วย (คงเหลือ {product.quantity})"
        )
        
        # 2. ตรวจสอบ threshold เพื่อส่ง Email แจ้งเตือนสต็อกต่ำ (FR-05, AC-01)
        if product.quantity <= product.threshold:
            NotificationService.send_email(
                sku=product.sku,
                product_name=product.name,
                current_qty=product.quantity,
                threshold=product.threshold
            )

# ==========================================
# ส่วนทดสอบการทำงานตาม Acceptance Criteria (AC-01)
# ==========================================
if __name__ == "__main__":
    inventory = InventorySystem()
    
    # จำลองสินค้า
    inventory.add_product(Product("SKU-WIRE-01", "สายไฟ VAF", 50, 15))
    
    print("--- Scenario 3: จ่ายสินค้าโดยสต็อกยังสูงกว่า threshold ---")
    try:
        inventory.stock_out("SKU-WIRE-01", 10) # 50 - 10 = 40 (> 15) -> SMS อย่างเดียว
    except Exception as e:
        print(e)
        
    print("\n" + "="*50 + "\n")
        
    print("--- Scenario 1: จ่ายสินค้าจนสต็อกต่ำกว่าหรือเท่ากับ threshold ---")
    try:
        # สต็อกปัจจุบันคือ 40, จ่าย 28 เหลือ 12 (<= 15) -> SMS + Email
        inventory.stock_out("SKU-WIRE-01", 28) 
    except Exception as e:
        print(e)
        
    print("\n" + "="*50 + "\n")
    
    inventory.add_product(Product("SKU-CABLE-02", "สายเคเบิล", 20, 15))
    print("--- Scenario 2: จ่ายสินค้าจนสต็อกเท่ากับ threshold พอดี (boundary case) ---")
    try:
        inventory.stock_out("SKU-CABLE-02", 5) # 20 - 5 = 15 (== 15) -> SMS + Email
    except Exception as e:
        print(e)
