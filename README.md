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

## 🚀 การรันชุดทดสอบ (Testing)

โปรเจกต์นี้มาพร้อมกับ Unit Tests, Integration Tests และสคริปต์ตรวจวัด Acceptance Criteria (AC) ที่ครอบคลุมทุก User Story ตามที่ระบุไว้ใน `inventory-sdd/specs/spec.md`

1. **รัน Unit Test หลัก**:
   ```bash
   python inventory-sdd/src/test_inventory_service.py
   ```

2. **รัน Integration Test** (ทดสอบการไหลของข้อมูลตั้งแต่เพิ่มสินค้า ยันแจ้งเตือนและ Export):
   ```bash
   python inventory-sdd/src/test_integration.py
   ```

3. **รันตรวจสอบ AC Compliance** (เทียบ Requirement):
   ```bash
   python test_ac_compliance.py
   ```

## 📁 ไฟล์เอกสารที่สำคัญ (Documentation)

- `inventory-sdd/specs/spec.md` : Requirement ฉบับสมบูรณ์ (User Stories, AC, Scope, Schema)
- `inventory-sdd/.ai-rules.md` : กฎและบริบทสำหรับ AI Agent 
- `inventory-sdd/design_review.md` : การทบทวนและวิเคราะห์โค้ดตามหลัก SOLID
- `inventory-sdd/AI_ITERATION_LOG.md` : บันทึกประวัติการทำงานร่วมกับ AI Agent
- `inventory-sdd/diagrams/` : แผนภาพ Class Diagram และ Sequence Diagram (Mermaid)

---
*Developed with 💙 by Team 03*
