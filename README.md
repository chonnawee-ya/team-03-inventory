# Team 03 Inventory System (Refactored Version)

ระบบจัดการสต็อกสินค้าร้านเครื่องเขียนที่ได้รับการปรับปรุงโครงสร้าง (Refactoring) ให้สอดคล้องกับหลักการ **SOLID Principles** เพื่อเพิ่มความยืดหยุ่นในการดูแลและขยายระบบในอนาคต (Scalability)

โปรเจกต์นี้เป็นส่วนหนึ่งของ **Lab 2: Software Engineering in AI Era**

## 🏗️ โครงสร้างสถาปัตยกรรมใหม่ (New Architecture)

ระบบได้ถูกรื้อโครงสร้างจากเดิมที่รวมทุกอย่างไว้ที่เดียว หรือแบ่งยิบย่อยเกินไป มาเป็นโครงสร้างที่เน้น **Domain-Driven Design (DDD)** และ **SOLID** ดังนี้:

- `inventory-sdd/src/models.py` : รับผิดชอบด้านโครงสร้างข้อมูล (Product, StockTransaction)
- `inventory-sdd/src/service.py` : รับผิดชอบเฉพาะ Business Logic หลัก (InventoryService)
- `inventory-sdd/src/events.py` : ระบบ Event Publisher / Subscriber (**Observer Pattern**) แจ้งเตือนเมื่อสต็อกเปลี่ยนหรือต่ำกว่าเกณฑ์
- `inventory-sdd/src/notifiers.py` : ระบบแจ้งเตือน (Email, SMS) ที่ทำงานเชื่อมกับ Event
- `inventory-sdd/src/exporters.py` : ระบบ Export CSV แยกตัวออกมาเพื่อลดภาระ Service (**Factory Pattern**)

## 💡 Design Patterns ที่ใช้งาน

1. **Observer Pattern**: เราใช้ `EventPublisher` ใน `service.py` แทนการเรียกใช้ Notifier โดยตรง ทำให้เราสามารถขยายช่องทางการแจ้งเตือนใหม่ๆ ได้โดยไม่ต้องแก้ไข Service (ตอบโจทย์ OCP)
2. **Factory Pattern**: การแยก `ExporterFactory` และ `NotifierFactory` ทำให้กระบวนการสร้าง Object ไม่ไปปะปนกับ Business Logic (ตอบโจทย์ SRP)

## 💻 คำสั่งในการใช้งาน (CLI Commands)

ระบบรองรับการทำงานผ่าน Command Line ด้วยคำสั่งต่างๆ ที่เชื่อมต่อกับ `InventoryService`, `EventPublisher` และระบบแจ้งเตือนแบบเรียลไทม์ ดังนี้:

### 1. ดูรายการสินค้าทั้งหมด (List Items - US-01)
แสดงรายการสินค้าทั้งหมด พร้อมรหัสสินค้า ชื่อสินค้า หมวดหมู่ จำนวนคงเหลือ และสถานะแจ้งเตือนสต็อกต่ำ (`[LOW STOCK]`)
```bash
python main.py list
```

### 2. เพิ่มสินค้าใหม่เข้าระบบ (Add Item - US-02)
เพิ่มรายการสินค้าใหม่โดยระบุรหัส ชื่อ และจำนวนเริ่มต้น (พร้อมตัวเลือกหมวดหมู่, ราคาทุน, ราคาขาย, หน่วยนับ และจุดสั่งซื้อ threshold)
```bash
python main.py add --code <รหัสสินค้า> --name "<ชื่อสินค้า>" --qty <จำนวน> [options]
```
*ตัวเลือกเสริม (Options):*
- `--category`: หมวดหมู่สินค้า (ค่าเริ่มต้น: "เครื่องเขียน")
- `--cost`: ราคาทุน > 0 (ค่าเริ่มต้น: 10.0)
- `--price`: ราคาขาย > 0 (ค่าเริ่มต้น: 20.0)
- `--unit`: หน่วยนับ เช่น ชิ้น, เล่ม, ม้วน (ค่าเริ่มต้น: "ชิ้น")
- `--threshold`: จุดสั่งซื้อเพื่อแจ้งเตือนสต็อกต่ำ (ค่าเริ่มต้น: 5.0)

*ตัวอย่าง:*
```bash
python main.py add --code A001 --name "ปากกาลูกลื่นสีน้ำเงิน" --qty 50 --category "เครื่องเขียน" --cost 8.0 --price 15.0 --threshold 10
```

### 3. ปรับปรุงจำนวนสินค้า รับเข้า/จ่ายออก (Update Item - US-03)
แก้ไขจำนวนสินค้าในสต็อก โดยระบุค่าบวกสำหรับการรับเข้า และค่าลบสำหรับการจ่ายออก (ระบบจะยิงแจ้งเตือน SMS ยืนยันทุกครั้ง และยิงแจ้งเตือน Email เมื่อสต็อกลดลงจนต่ำกว่าหรือเท่ากับจุดสั่งซื้อ threshold ตาม AC-01)
```bash
python main.py update --code <รหัสสินค้า> --delta <จำนวนที่เปลี่ยนแปลง> [--reason "<เหตุผล>"]
```
*ตัวอย่าง (จ่ายออก/ขายสินค้า):*
```bash
python main.py update --code A001 --delta -45 --reason "ขายให้ลูกค้า"
```
*(เมื่อสต็อกเหลือ 5 ชิ้น ซึ่งต่ำกว่า threshold 10 จะมีการแสดงแจ้งเตือน `[Email] แจ้งเตือนสต็อกต่ำ` บนหน้าจอทันที)*

*ตัวอย่าง (รับสินค้าเข้าสต็อก):*
```bash
python main.py update --code A001 --delta 30 --reason "สั่งของมาเติมสต็อก"
```

### 4. ค้นหาสินค้า (Search Items - US-04)
ค้นหาสินค้าด้วยชื่อหรือรหัสสินค้า (ค้นหาแบบ Partial Match ไม่แยกตัวพิมพ์เล็ก-ใหญ่)
```bash
python main.py search --query <คำค้นหา>
```
*ตัวอย่าง:*
```bash
python main.py search --query ปากกา
```

### 5. ส่งออกรายงานสต็อกเป็นไฟล์ CSV (Export Items - US-05)
ส่งออกข้อมูลสินค้าทั้งหมดออกเป็นไฟล์ `.csv` (เข้ารหัสแบบ UTF-8 with BOM เพื่อให้เปิดภาษาไทยบน Excel ได้อย่างถูกต้อง)
```bash
python main.py export [--output <ชื่อไฟล์.csv>]
```
*ตัวอย่าง:*
```bash
python main.py export --output stock_report.csv
```

### 6. รายงานสรุปมูลค่าสต็อกคงเหลือ (Stock Valuation Report - US-06)
แสดงรายงานสรุปภาพรวมมูลค่าสต็อกคงคลัง จัดกลุ่มตามหมวดหมู่ พร้อมยอดรวมจำนวนสินค้าและมูลค่ารวมทั้งหมด
```bash
python main.py report
```

*(หมายเหตุ: สามารถใช้พารามิเตอร์เสริม `--data <path_to_json>` ก่อนหน้าคำสั่งย่อยเพื่อระบุตำแหน่งไฟล์ฐานข้อมูลได้ เช่น `python main.py --data custom_data.json list`)*

## 🚀 การรันชุดทดสอบ (Testing)

โปรเจกต์นี้มีชุดทดสอบครอบคลุมทุก User Story (US-01 ถึง US-06) และทุก Acceptance Criteria (AC-01 ถึง AC-07):

1. **รันชุดทดสอบรวมครอบคลุมทุกฟังก์ชัน (Comprehensive Test Suite)**:
   ทดสอบครบทั้ง Logic ภายใน Service, การยิง Event/Notification และการรันคำสั่ง CLI End-to-End ผ่าน `main.py`
   ```bash
   python test_all_features.py
   ```

2. **รัน Unit Test ของ InventoryService**:
   ```bash
   python inventory-sdd/src/test_inventory_service.py
   ```

3. **รัน Integration Test** (ทดสอบการไหลของข้อมูลตั้งแต่ Service, Event, Notification ไปจนถึง Export):
   ```bash
   python inventory-sdd/src/test_integration.py
   ```

4. **รันตรวจสอบ AC Compliance** (เทียบ Requirement ตาม Spec):
   ```bash
   python test_ac_compliance.py
   ```

5. **รันตรวจสอบความถูกต้องของสถาปัตยกรรม (Architecture Verification)**:
   ```bash
   python verify_architecture.py
   ```

## 📁 ไฟล์เอกสารที่สำคัญ (Documentation)

- `inventory-sdd/specs/spec.md` : Requirement ฉบับสมบูรณ์ (User Stories, AC, Scope, Schema)
- `inventory-sdd/.ai-rules.md` : กฎและบริบทสำหรับ AI Agent 
- `inventory-sdd/design_review.md` : การทบทวนและวิเคราะห์โค้ดตามหลัก SOLID
- `inventory-sdd/AI_ITERATION_LOG.md` : บันทึกประวัติการทำงานร่วมกับ AI Agent
- `inventory-sdd/diagrams/` : แผนภาพ Class Diagram และ Sequence Diagram (Mermaid)

---
*Developed with 💙 by Team 03*
