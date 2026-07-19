#!/usr/bin/env python3
"""
test_inventory.py — unit test สำหรับ inventory.py
รัน: python -m unittest test_inventory.py -v
"""

import json
import os
import subprocess
import sys
import unittest
from pathlib import Path
import tempfile
import shutil


class InventoryCLITestCase(unittest.TestCase):
    def setUp(self):
        self.tmpdir = Path(tempfile.mkdtemp())
        self.data_file = self.tmpdir / "items.json"
        self.script = Path(__file__).parent / "main.py"

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def run_cli(self, *args):
        # บังคับ UTF-8 ทั้งฝั่งเขียน (child process) และฝั่งอ่าน (subprocess.run)
        # กันข้อความไทยเพี้ยนหรือ crash บน Windows ที่ console ไม่ใช่ UTF-8
        env = os.environ.copy()
        env["PYTHONUTF8"] = "1"
        return subprocess.run(
            [sys.executable, str(self.script), "--data", str(self.data_file), *args],
            capture_output=True,
            text=True,
            encoding="utf-8",
            env=env,
        )

    # ---- US-01: list ----
    def test_list_empty_shows_message(self):
        # AC-2: ระบบยังไม่มีสินค้าบันทึกอยู่เลย -> แสดง "ยังไม่มีสินค้าในระบบ"
        result = self.run_cli("list")
        self.assertIn("ยังไม่มีสินค้าในระบบ", result.stdout)

    def test_list_shows_all_items(self):
        # AC-1: มีสินค้าอยู่แล้ว -> list ต้องแสดงชื่อ รหัส จำนวน ครบทุกรายการ
        self.run_cli("add", "--code", "A001", "--name", "ปากกา", "--qty", "10")
        self.run_cli("add", "--code", "A002", "--name", "ดินสอ", "--qty", "20")
        result = self.run_cli("list")
        self.assertIn("A001", result.stdout)
        self.assertIn("A002", result.stdout)
        self.assertIn("ปากกา", result.stdout)
        self.assertIn("ดินสอ", result.stdout)

    # ---- US-02: add ----
    def test_add_new_item(self):
        result = self.run_cli("add", "--code", "A001", "--name", "ปากกา", "--qty", "10")
        self.assertEqual(result.returncode, 0)
        data = json.loads(self.data_file.read_text(encoding="utf-8"))
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["code"], "A001")
        self.assertEqual(data[0]["quantity"], 10)

    def test_add_duplicate_code_fails(self):
        self.run_cli("add", "--code", "A001", "--name", "ปากกา", "--qty", "10")
        result = self.run_cli("add", "--code", "A001", "--name", "ปากกาอีกด้าม", "--qty", "5")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("มีอยู่ในระบบแล้ว", result.stdout + result.stderr)

    def test_add_negative_quantity_fails(self):
        result = self.run_cli("add", "--code", "A001", "--name", "ปากกา", "--qty", "-5")
        self.assertNotEqual(result.returncode, 0)

    # ---- US-03: update ----
    def test_update_increases_quantity(self):
        self.run_cli("add", "--code", "A001", "--name", "ปากกา", "--qty", "10")
        result = self.run_cli("update", "--code", "A001", "--delta", "5")
        self.assertEqual(result.returncode, 0)
        data = json.loads(self.data_file.read_text(encoding="utf-8"))
        self.assertEqual(data[0]["quantity"], 15)

    def test_update_decreases_quantity(self):
        self.run_cli("add", "--code", "A001", "--name", "ปากกา", "--qty", "10")
        result = self.run_cli("update", "--code", "A001", "--delta", "-4")
        self.assertEqual(result.returncode, 0)
        data = json.loads(self.data_file.read_text(encoding="utf-8"))
        self.assertEqual(data[0]["quantity"], 6)

    def test_update_below_zero_fails(self):
        self.run_cli("add", "--code", "A001", "--name", "ปากกา", "--qty", "3")
        result = self.run_cli("update", "--code", "A001", "--delta", "-10")
        self.assertNotEqual(result.returncode, 0)
        data = json.loads(self.data_file.read_text(encoding="utf-8"))
        self.assertEqual(data[0]["quantity"], 3)  # ไม่เปลี่ยนแปลง

    def test_update_missing_code_fails(self):
        result = self.run_cli("update", "--code", "ZZZ", "--delta", "5")
        self.assertNotEqual(result.returncode, 0)

    # ---- US-04: search ----
    def test_search_by_name(self):
        self.run_cli("add", "--code", "A001", "--name", "ปากกาลูกลื่น", "--qty", "10")
        self.run_cli("add", "--code", "A002", "--name", "ดินสอ 2B", "--qty", "20")
        result = self.run_cli("search", "--query", "ปากกา")
        self.assertIn("A001", result.stdout)
        self.assertNotIn("A002", result.stdout)

    def test_search_by_code(self):
        self.run_cli("add", "--code", "A001", "--name", "ปากกาลูกลื่น", "--qty", "10")
        result = self.run_cli("search", "--query", "A001")
        self.assertIn("ปากกาลูกลื่น", result.stdout)

    def test_search_no_match(self):
        self.run_cli("add", "--code", "A001", "--name", "ปากกา", "--qty", "10")
        result = self.run_cli("search", "--query", "ไม้บรรทัด")
        self.assertIn("ไม่พบสินค้า", result.stdout)

    # ---- US-05: export ----
    def test_export_creates_csv(self):
        self.run_cli("add", "--code", "A001", "--name", "ปากกา", "--qty", "10")
        out_file = self.tmpdir / "report.csv"
        result = self.run_cli("export", "--output", str(out_file))
        self.assertEqual(result.returncode, 0)
        self.assertTrue(out_file.exists())
        content = out_file.read_text(encoding="utf-8-sig")
        self.assertIn("A001", content)
        self.assertIn("code,name,quantity,updated_at", content)


if __name__ == "__main__":
    unittest.main()
