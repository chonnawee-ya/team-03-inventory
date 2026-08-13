# team-XX-inventory — ระบบสต็อกร้านเขียนดี

โปรแกรม command-line จัดการสต็อกสินค้าร้านเครื่องเขียน เก็บข้อมูลในไฟล์ JSON
ทำขึ้นสำหรับ **Lab 2: Software Engineering in AI Era**

> แก้ `team-XX` ในชื่อ repository และหัวข้อนี้เป็นหมายเลขทีมของตัวเอง

## Requirements

- Python 3.9 ขึ้นไป (ไม่ต้องติดตั้ง library เพิ่ม ใช้แต่ standard library)

## เริ่มใช้งาน

```bash
git clone https://github.com/<username>/team-XX-inventory.git
cd team-XX-inventory
python3 main.py list
```

ไฟล์ข้อมูล `items.json` จะถูกสร้างอัตโนมัติเมื่อ `add` สินค้าชิ้นแรก
(ถ้าต้องการใช้ไฟล์คนละที่ ใส่ `--data path/to/file.json` ต่อท้ายทุกคำสั่งได้)

## คำสั่งที่รองรับ

| คำสั่ง   | User Story | ทำอะไร                                      |
| -------- | ---------- | -------------------------------------------- |
| `list`   | US-01      | แสดงรายการสินค้าทั้งหมดพร้อมจำนวนคงเหลือ     |
| `add`    | US-02      | เพิ่มสินค้าใหม่เข้าระบบ                      |
| `update` | US-03      | ปรับจำนวนสินค้าเมื่อรับเข้า / จ่ายออก        |
| `search` | US-04      | ค้นหาสินค้าด้วยชื่อหรือรหัส                  |
| `export` | US-05      | ส่งออกรายงานสต็อกเป็นไฟล์ CSV                |

### ตัวอย่าง

```bash
# US-01: ดูรายการสินค้าทั้งหมด
python3 main.py list

# US-02: เพิ่มสินค้าใหม่
python3 main.py add --code A001 --name "ปากกาลูกลื่นสีน้ำเงิน" --qty 50

# US-03: ปรับจำนวน (delta บวก = รับของเข้า, ลบ = จ่ายของออก)
python3 main.py update --code A001 --delta -5 --reason "ขายให้ลูกค้า"
python3 main.py update --code A001 --delta 20 --reason "รับของเข้าคลัง"

# US-04: ค้นหาด้วยชื่อหรือรหัส
python3 main.py search --query ปากกา
python3 main.py search --query A001

# US-05: ส่งออกเป็น CSV
python3 main.py export --output stock_report.csv
```

ทุกคำสั่งพิมพ์ `--help` เพื่อดูตัวเลือกทั้งหมดได้ เช่น `python3 main.py add --help`

## รัน unit test

```bash
python3 -m unittest test_inventory.py -v
```

Test ครอบคลุม acceptance criteria หลักของทุก user story (list ว่าง/ไม่ว่าง,
add ซ้ำรหัส, update ติดลบไม่ได้, search ไม่พบ, export ได้ไฟล์ CSV ที่ถูกต้อง)

## โครงสร้างไฟล์

```
.
├── main.py                    # entry point — เชื่อมต่อและควบคุมทุกคำสั่ง
├── models.py                   # โครงสร้างข้อมูล Item
├── storage.py                   # อ่าน/เขียนไฟล์ JSON
├── commands/
│   ├── list_items.py               # US-01
│   ├── add_item.py                 # US-02
│   ├── update_item.py              # US-03
│   ├── search_items.py             # US-04
│   └── export_items.py             # US-05
├── test_inventory.py            # unit tests
├── items.json                    # ข้อมูลสินค้า (สร้างอัตโนมัติ ไม่ควร commit)
├── TEAM_CHARTER.md                # บทบาททีม + branching strategy + sprint goal
├── RETRO-SPRINT-1.md              # sprint retrospective
└── README.md
```

**แนวคิดของโครงสร้าง:** แต่ละ user story แยกเป็น 1 ไฟล์ใน `commands/` โดยมี
ฟังก์ชันหลัก (`cmd_xxx`) ที่ทำงานจริง และฟังก์ชัน `register()` ที่ผูกคำสั่งเข้ากับ
argparse `main.py` มีหน้าที่แค่ import ทุก command module แล้วเรียก `register()`
ของแต่ละตัว — ไม่รู้รายละเอียด logic ข้างในเลย ทำให้:
- แต่ละคนในทีมทำงานคนละไฟล์ใน `commands/` ได้พร้อมกันโดยไม่ conflict กัน
- เพิ่มคำสั่งใหม่ในอนาคต แค่สร้างไฟล์ใหม่ใน `commands/` แล้วเติมชื่อ module
  ลงใน `COMMAND_MODULES` ใน `main.py` บรรทัดเดียว

## Workflow ของทีม

ทีมนี้ใช้ **GitHub Flow**: `main` ต้อง deploy ได้เสมอ ทุก feature พัฒนาบน branch
`feat/<issue-number>-<short-name>` แล้วเปิด Pull Request ให้เพื่อนใน team
review และ approve ก่อน merge เสมอ (ห้าม commit ตรงเข้า `main`, ห้าม merge PR
ของตัวเอง) รายละเอียดดู `TEAM_CHARTER.md`
