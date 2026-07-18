# TEAM_CHARTER.md

## สมาชิกและบทบาท

| ชื่อ | GitHub Username | บทบาท |
|---|---|---|
| ชนวีร์ แย้มขยาย  | chonnawee yaemkhayai                | Product Owner |
| กณิศ สิงห์คำ  | Kansi Singkham             | Scrum Master / Developer |
| ภัทรภณ ตันนารัตน์  | Yoru006           | Scrum Master / Developer |
| วิชชากร เดชสุภา | wichakorn4             | Developer |
| ปรัชญากร นาสา | pratchaykornnasa            | Developer |
| สุพิชญา จันทร์น้ำคำ | Supitchaya Channamkham             | Developer |

## Branching Strategy

ทีมใช้ GitHub Flow:
- main branch ต้อง deploy ได้เสมอ ห้าม commit โดยตรง
- ทุก feature ใหม่ต้องสร้าง branch ชื่อ feat/<issue-number>-<short-name>
- ทุก PR ต้องมีคนอื่นในทีมอย่างน้อย 1 คน review และ approve ก่อน merge

## Sprint Goal (Sprint 1)
- 1 list — ทีมจะทำให้พนักงานเรียกดูสต็อกทั้งหมดได้ถูกต้องครบทุกรายการ ภายในคำสั่งเดียว
- 2 add — ทีมจะทำให้พนักงานเพิ่มสินค้าใหม่เข้าระบบได้โดยไม่มีรหัสซ้ำหรือจำนวนติดลบหลุดเข้าไป
- 3 update — ทีมจะทำให้พนักงานปรับยอดรับเข้า/จ่ายออกได้ถูกต้อง โดยยอดคงเหลือต้องไม่ติดลบเด็ดขาด
- 4 search — ทีมจะทำให้ผู้จัดการค้นหาสินค้าด้วยชื่อหรือรหัสแล้วเจอผลลัพธ์ที่ถูกต้องภายในคำสั่งเดียว 
- 5 export — ทีมจะทำให้ผู้จัดการส่งออกรายงานสต็อกเป็น CSV ที่เปิดใช้ทำบัญชีต่อได้ทันที
- test — ทีมจะทำให้ทุก user story มี unit test ครอบ acceptance criteria ทั้งกรณีปกติและ edge case
- 7 docs — ทีมจะทำให้สมาชิกใหม่ clone repo แล้วรันโปรแกรมได้เองโดยไม่ต้องถามใคร

## AI Usage Policy

- ใช้ AI ช่วยเขียน draft code และ draft commit message ได้
- ทุก commit message ที่ AI generate ต้องอ่านและแก้ให้ตรงกับ diff จริงก่อน commit
- ห้าม copy code จาก AI โดยไม่อ่านและทำความเข้าใจก่อน
- ใช้เฉพาะ AI ที่ไม่มีค่าใช้จ่าย ไม่บังคับซื้อ subscription
