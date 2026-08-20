# AI Iteration Log

**ช่องทาง AI ที่ใช้:** Antigravity IDE (Gemini)

ตารางเปรียบเทียบความแตกต่างของการเขียนโค้ดก่อนและหลังมี Context (กฎจาก `.ai-rules.md`):

| ประเด็น | ก่อนมี context (ขั้นที่ 4) | หลังมี context (ขั้นที่ 6) |
| --- | --- | --- |
| **แยกไฟล์/ความรับผิดชอบ** | รวมทุกอย่าง (Models, Logic, Notifiers) ไว้ในไฟล์เดียวกันทั้งหมด (`inventory_no_context.py`) | แยกไฟล์และหน้าที่ความรับผิดชอบชัดเจน (`models.py`, `notifiers.py`, `service.py`) ตามหลัก SRP |
| **type hint + docstring** | มี type hint และ docstring บางส่วน แต่ไม่ได้บังคับเข้มงวด | บังคับใส่ครบถ้วนทุก function signature และมี docstring อธิบายทุก public method |
| **service ผูกกับ notifier ตรง ๆ หรือไม่** | ผูกตรง (Tight Coupling) โดย Service เรียกใช้ `NotificationService` ตรงๆ | ไม่ผูกตรง (Loose Coupling) โดยใช้ Dependency Injection รับ `Notifier` interface ผ่าน Constructor |
| **hardcode config หรือไม่** | มีการ hardcode ค่าต่างๆ ไว้ในส่วนของ Business Logic | ไม่มีการ hardcode การตั้งค่าถูกส่งผ่านจากภายนอกหรือจัดการผ่าน Factory Pattern |

## Iteration: Test AC Compliance (spec.md vs service.py)

**จุดประสงค์:** ทดสอบการทำงานของระบบให้ตรงตาม Acceptance Criteria (AC) ทั้งหมดใน `spec.md`

| รายการทดสอบ | ผลที่ผิด / ไม่ตรง | สาเหตุ (Spec หรือ Context) | การแก้ไขที่ต้นทาง | ผลหลังแก้ |
| --- | --- | --- | --- | --- |
| **AC-02** แสดงรายการสินค้าสถานะ low-stock ด้วย CSS class | ฝั่ง Backend ขาด property หรือ method ให้ฝั่ง UI นำไปตรวจสอบเงื่อนไขแบบง่ายๆ โดยไม่ต้องเขียน logic ซ้ำซ้อน | **Context ขาดหาย** (Backend ไม่ซัพพอร์ต UI rendering logic) | เพิ่ม `@property def is_low_stock` ใน `Product` (`models.py`) | Product สามารถเรียกใช้ `.is_low_stock` เพื่อ return True/False ไปทำสี CSS ต่อได้ทันที |
| **AC-03** เพิ่มสินค้า ราคาทุน > 0, ราคาขาย > 0 | ระบบเก่าปัดตกเฉพาะค่าที่ `< 0` (ติดลบ) ทำให้ยอมรับราคาเป็น 0 ได้ ขัดกับ AC-03 | **Spec กำกวม** (ตาราง Error Schema จำกัดความ NEGATIVE_VALUE ไว้ที่ "ค่าติดลบ" ซึ่ง 0 ไม่ใช่ค่าติดลบ) | แก้ Validation ใน `service.py` ให้เป็น `<= 0` สำหรับราคา และอัปเดต Error Schema ใน `spec.md` ให้ครอบคลุม "ราคา <= 0" | ระบบปฏิเสธการกรอกราคาเป็น 0 พร้อมขึ้น Error ตรงตามที่ควรจะเป็น และเทส `test_ac_compliance.py` ผ่าน 100% |

## Prompt ที่ใช้จริง
- **Prompt 1 (สร้างไฟล์/โครงสร้างเริ่มแรก):** "สร้าง ไฟล์ AI_ITERATION_LOG.md โดยอิงจากภาพที่ส่งไป"
- **Prompt 2 (รันเทสเทียบ Requirement):** "ทดสอบโปรแกรมตาม acceptance criteria จาก inventory-sdd/specs/spec.md ทุกข้อ ถ้าผลไม่ตรง ให้แสดงผลว่าเป็นเพราะ spec กำกวม หรือ context ไม่ครอบคลุม แล้วแก้ที่ต้นทาง ทุกรอบ iterate บันทึกลง AI_ITERATION_LOG.md"
- **Prompt 3 (สร้าง/แก้ Diagram):** "จากโค้ดใน invertory-sdd/src/models.py, invertory-sdd/src/notifiers.py, invertory-sdd/src/service.py สร้าง Class Diagram เป็น Mermaid และ Sequence Diagram... บันทึกลง diagrams/class.md และ diagrams/sequence.md"
- **Prompt 4 (วิเคราะห์และ refactor โครงสร้าง SOLID):** "ตรวจสอบไฟล์ design_review.md และสร้าง Factory + Observer ออกมา"
