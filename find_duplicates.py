import ast
import os
import glob
import sys
from collections import defaultdict

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

def find_duplicate_functions():
    # ค้นหาไฟล์ .py ทั้งหมดในโปรเจกต์
    py_files = glob.glob('**/*.py', recursive=True)
    
    # เก็บข้อมูล { function_name: [list of files] }
    func_map = defaultdict(list)
    class_map = defaultdict(list)
    
    # เพื่อไม่ให้สนใจโฟลเดอร์ที่ไม่เกี่ยวกับโค้ดหลัก
    ignore_dirs = ['.git', '__pycache__', 'env', 'venv']
    
    for filepath in py_files:
        if any(d in filepath for d in ignore_dirs):
            continue
            
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                tree = ast.parse(f.read(), filename=filepath)
                
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # ถ้าเป็น method ใน class ให้ใส่ชื่อ class นำหน้า
                    # ast.walk ไม่ได้บอก parent node ทันที ดังนั้นเราทำแบบง่ายๆ
                    pass # จะใช้ logic หา parent ทีหลัง
                    
            # วิธีหา class และ method ที่ดีกว่า:
            for node in tree.body:
                if isinstance(node, ast.FunctionDef):
                    func_map[node.name].append(filepath)
                elif isinstance(node, ast.ClassDef):
                    class_map[node.name].append(filepath)
                    for subnode in node.body:
                        if isinstance(subnode, ast.FunctionDef):
                            method_name = f"{node.name}.{subnode.name}"
                            func_map[method_name].append(filepath)
                            
        except Exception as e:
            pass
            
    print("=== ฟังก์ชันที่ชื่อซ้ำกันในหลายไฟล์ ===")
    found_dup_func = False
    for func, files in func_map.items():
        if len(set(files)) > 1:
            # ซ้ำถ้าอยู่มากกว่า 1 ไฟล์ที่ไม่ใช่ไฟล์เดียวกัน
            # __init__ และ __post_init__ อาจจะซ้ำเป็นเรื่องปกติ
            if func.split('.')[-1] not in ('__init__', '__post_init__', 'setUp'):
                print(f"- {func}: พบใน {', '.join(set(files))}")
                found_dup_func = True
                
    if not found_dup_func:
        print("ไม่พบฟังก์ชันที่ชื่อซ้ำกัน")
        
    print("\n=== คลาสที่ชื่อซ้ำกันในหลายไฟล์ ===")
    found_dup_class = False
    for cls, files in class_map.items():
        if len(set(files)) > 1:
            print(f"- {cls}: พบใน {', '.join(set(files))}")
            found_dup_class = True
            
    if not found_dup_class:
        print("ไม่พบคลาสที่ชื่อซ้ำกัน")

if __name__ == '__main__':
    find_duplicate_functions()
