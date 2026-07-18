# TEAM_CHARTER.md

## สมาชิกและบทบาท

| ชื่อ | GitHub Username | บทบาท |
|---|---|---|
| ชนวีร์ แย้มขยาย  | chonnawee yaemkhayai                | Product Owner |
| กณิศ สิงห์คำ  | Kansi Singkham             | Scrum Master / Developer |
| ภัทรภณ ตันนารัตน์  | Yoru006           | Scrum Master / Developer |
| วิชชากร เดชสุพา | ...             | Developer |
| ปรัชญากร นาสา | pratchaykornnasa            | Developer |
| สุพิชญา จันทร์น้ำคำ | Supitchaya Channamkham             | Developer |

## Branching Strategy

ทีมใช้ GitHub Flow:
- main branch ต้อง deploy ได้เสมอ ห้าม commit โดยตรง
- ทุก feature ใหม่ต้องสร้าง branch ชื่อ feat/<issue-number>-<short-name>
- ทุก PR ต้องมีคนอื่นในทีมอย่างน้อย 1 คน review และ approve ก่อน merge

## Sprint Goal (Sprint 1)
- Task 1: เตรียมไฟล์ฐานข้อมูลจำลอง (Database Setup):
  เป้าหมาย (Goal): มีโครงสร้างข้อมูลจำลอง (Mock Data) ที่ถูกต้องและพร้อมใช้งาน
- Task 2: เขียนฟังก์ชันดึงข้อมูลมาแสดงผล (สำหรับ US-01):
  เป้าหมาย (Goal): พนักงานสามารถรับรู้สถานะสต็อกทั้งหมดได้ในหน้าจอเดียวอย่างถูกต้อง
- Task 3: เขียนฟังก์ชันรับค่าและค้นหาสินค้า (สำหรับ US-04):
  เป้าหมาย (Goal): ผู้ใช้สามารถเข้าถึงข้อมูลสินค้าที่ต้องการเจาะจงได้อย่างแม่นยำและรวดเร็ว  
-Task 4: รวมฟังก์ชันเข้ากับเมนูหลักและการทดสอบ (Main Menu & Testing):
  เป้าหมาย (Goal): ระบบทั้งหมดเชื่อมต่อกันอย่างไร้รอยต่อ และพร้อมส่งมอบงานที่มีคุณภาพ  

## AI Usage Policy

- ใช้ AI ช่วยเขียน draft code และ draft commit message ได้
- ทุก commit message ที่ AI generate ต้องอ่านและแก้ให้ตรงกับ diff จริงก่อน commit
- ห้าม copy code จาก AI โดยไม่อ่านและทำความเข้าใจก่อน
- ใช้เฉพาะ AI ที่ไม่มีค่าใช้จ่าย ไม่บังคับซื้อ subscription
