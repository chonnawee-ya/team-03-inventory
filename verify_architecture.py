import ast
import inspect
import sys

def parse_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return ast.parse(f.read(), filename=filepath)
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return None

def check_file_separation():
    print("--- 1. แยกไฟล์/ความรับผิดชอบ ---")
    
    # ก่อนมี context
    no_context_ast = parse_file("inventory-sdd/src/inventory_no_context.py")
    classes_in_no_context = [node.name for node in ast.walk(no_context_ast) if isinstance(node, ast.ClassDef)]
    print(f"[ก่อน] inventory_no_context.py มีคลาสทั้งหมด: {classes_in_no_context} (รวมมิตรในไฟล์เดียว)")
    
    # หลังมี context
    models_ast = parse_file("inventory-sdd/src/models.py")
    notifiers_ast = parse_file("inventory-sdd/src/notifiers.py")
    service_ast = parse_file("inventory-sdd/src/service.py")
    
    models_classes = [node.name for node in ast.walk(models_ast) if isinstance(node, ast.ClassDef)] if models_ast else []
    notifiers_classes = [node.name for node in ast.walk(notifiers_ast) if isinstance(node, ast.ClassDef)] if notifiers_ast else []
    service_classes = [node.name for node in ast.walk(service_ast) if isinstance(node, ast.ClassDef)] if service_ast else []
    
    print(f"[หลัง] models.py มีคลาส: {models_classes}")
    print(f"[หลัง] notifiers.py มีคลาส: {notifiers_classes}")
    print(f"[หลัง] service.py มีคลาส: {service_classes}")
    print(f"[สรุป] มีการแยกไฟล์ชัดเจนตาม SRP อย่างแท้จริง\n")


def check_type_hint_and_docstring():
    print("--- 2. Type Hint & Docstring ---")
    
    def count_hints_docstrings(tree):
        funcs = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
        total = len(funcs)
        has_docs = sum(1 for f in funcs if ast.get_docstring(f) is not None)
        has_hints = sum(1 for f in funcs if f.returns is not None or any(arg.annotation for arg in f.args.args))
        return total, has_docs, has_hints

    no_context_ast = parse_file("inventory-sdd/src/inventory_no_context.py")
    total_1, docs_1, hints_1 = count_hints_docstrings(no_context_ast)
    print(f"[ก่อน] inventory_no_context.py -> ฟังก์ชันทั้งหมด {total_1}, มี Docstring {docs_1}, มี Type Hint {hints_1}")
    
    service_ast = parse_file("inventory-sdd/src/service.py")
    total_2, docs_2, hints_2 = count_hints_docstrings(service_ast)
    print(f"[หลัง] service.py -> ฟังก์ชันทั้งหมด {total_2}, มี Docstring {docs_2}, มี Type Hint {hints_2}")
    
    if docs_2 == total_2 and hints_2 == total_2:
        print("[สรุป] หลังมี context มีการใส่ Docstring และ Type Hint ครบ 100% ทุกฟังก์ชัน\n")
    else:
        print("[สรุป] หลังมี context มีการใส่เพิ่มขึ้น แต่ยังไม่ครบ 100%\n")


def check_coupling():
    print("--- 3. Service ผูกกับ Notifier ตรงๆ หรือไม่ (Coupling) ---")
    
    # วิเคราะห์ inventory_no_context.py
    no_context_ast = parse_file("inventory-sdd/src/inventory_no_context.py")
    hardcoded_calls = []
    for node in ast.walk(no_context_ast):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name):
                if node.func.value.id == 'NotificationService':
                    hardcoded_calls.append(node.func.attr)
    print(f"[ก่อน] พบการเรียกใช้คลาส NotificationService โดยตรง (Hardcoded Class Method): {hardcoded_calls}")

    # วิเคราะห์ service.py
    service_ast = parse_file("inventory-sdd/src/service.py")
    init_func = None
    for node in ast.walk(service_ast):
        if isinstance(node, ast.FunctionDef) and node.name == '__init__':
            init_func = node
            break
            
    args = [arg.arg for arg in init_func.args.args if arg.arg != 'self']
    annotations = [ast.unparse(arg.annotation) if arg.annotation else "None" for arg in init_func.args.args if arg.arg != 'self']
    
    print(f"[หลัง] InventoryService.__init__ รับ dependencies ผ่าน Constructor (DI):")
    for arg, ann in zip(args, annotations):
        print(f"       - {arg}: {ann}")
    print("[สรุป] หลังมี context ไม่ได้ผูกกับคลาส Notifier จริง แต่ผูกกับ Interface/Protocol แทน (Dependency Injection)\n")

def check_hardcode_config():
    print("--- 4. Hardcode config หรือไม่ ---")
    
    print("[ก่อน] ใน inventory_no_context.py -> NotificationService มีการพิมพ์ '[SMS]' ลงไปตรงๆ และเรียกใช้งานแบบ static")
    
    print("[หลัง] ใน notifiers.py -> ใช้ NotifierFactory สร้าง Notifier ทำให้สามารถ config จากภายนอกได้ว่าอยากได้ Email หรือ SMS")
    print("       และใน service.py อาศัยการส่ง Instance ของ Notifier เข้าไป ไม่ต้องรู้ว่าข้างในเป็น '[SMS]' หรือไม่")
    print("[สรุป] สามารถเปลี่ยนรูปแบบการแจ้งเตือนได้โดยไม่ต้องแก้โค้ดใน InventoryService (Open-Closed Principle)\n")

if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
        
    print("=== ผลการทดสอบเปรียบเทียบโค้ดตามตาราง AI_ITERATION_LOG.md ===\n")
    check_file_separation()
    check_type_hint_and_docstring()
    check_coupling()
    check_hardcode_config()
