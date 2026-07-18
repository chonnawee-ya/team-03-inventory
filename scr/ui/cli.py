import argparse
import sys
from colorama import Fore, Style, init

# เริ่มต้นใช้งาน colorama (ช่วยให้แสดงสีบน Windows, Mac, Linux ได้เหมือนกัน)
init(autoreset=True)

def validate_and_add_product(args):
    # [ ] Implement Client-side Validation: ตรวจสอบว่า quantity และ price ต้องไม่ติดลบ
    if args.quantity < 0:
        # [ ] Handle Output/Feedback: แสดงสถานะความผิดพลาดเป็นตัวหนังสือสีแดง
        print(f"{Fore.RED}[ERROR] Invalid quantity format. Quantity cannot be negative.")
        sys.exit(1)
        
    if args.price < 0:
        print(f"{Fore.RED}[ERROR] Invalid price format. Price cannot be negative.")
        sys.exit(1)

    # ตรงนี้คือจุดที่คุณสามารถนำข้อมูลไปบันทึกต่อลง Database หรือ JSON ได้
    # [ ] Handle Output/Feedback: แสดงสถานะความสำเร็จเป็นตัวหนังสือสีเขียว
    print(f"{Fore.GREEN}[SUCCESS] Product '{args.name}' (SKU: {args.sku}) added successfully.")
    print(f"Details -> Qty: {args.quantity}, Price: ${args.price:.2f}")

def main():
    # [ ] Setup CLI Framework: ใช้ argparse กำหนดโครงสร้างคำสั่งหลัก
    parser = argparse.ArgumentParser(
        description="Product Management CLI Tool",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    # สร้าง sub-commands สำหรับคำสั่งย่อย (เช่น product)
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # สร้างคำสั่งย่อย 'product'
    product_parser = subparsers.add_parser("product", help="Product management commands")
    product_subparsers = product_parser.add_subparsers(dest="action", required=True)
    
    # สร้างคำสั่งย่อย 'add' ภายใต้ 'product' (กลายเป็น app product add)
    add_parser = product_subparsers.add_parser("add", help="Add a new product")

    # [ ] Define Arguments/Options: กำหนด Options ที่จำเป็น (ใส่ required=True เพื่อเช็กว่าครบถ้วนไหม)
    add_parser.add_dict = add_parser.add_argument(
        "--sku", "-s", 
        type=str, 
        required=True, 
        help="Stock Keeping Unit / Product ID (String)"
    )
    add_parser.add_argument(
        "--name", "-n", 
        type=str, 
        required=True, 
        help="Product Name (String)"
    )
    add_parser.add_argument(
        "--quantity", "-q", 
        type=int, 
        required=True, 
        help="Initial stock quantity (Integer)"
    )
    add_parser.add_argument(
        "--price", "-p", 
        type=float, 
        required=True, 
        help="Product price (Float)"
    )

    # ประมวลผล Arguments จาก Terminal
    # หากผู้ใช้ใส่ Options ไม่ครบถ้วน argparse จะแสดง Usage/Help Text ให้โดยอัตโนมัติ
    args = parser.parse_args()

    # เรียกใช้ฟังก์ชันทำงานเมื่อคำสั่งถูกต้อง
    if args.command == "product" and args.action == "add":
        validate_and_add_product(args)

if __name__ == "__main__":
    main()
