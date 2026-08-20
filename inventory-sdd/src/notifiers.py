from typing import Protocol, Dict, Any

class Notifier(Protocol):
    """โปรโตคอลสำหรับส่งการแจ้งเตือน (Observer)"""
    def handle_event(self, event_type: str, data: Dict[str, Any]) -> None:
        ...

class EmailNotifier:
    """จำลองการส่งการแจ้งเตือนผ่าน Email"""
    def handle_event(self, event_type: str, data: Dict[str, Any]) -> None:
        if event_type == "LOW_STOCK_ALERT":
            message = f"แจ้งเตือนสต็อกต่ำ: {data['sku']} คงเหลือ {data['quantity']} (Threshold: {data['threshold']})"
            self._send(message)

    def _send(self, message: str) -> None:
        print(f"[Email] {message}")

class SMSNotifier:
    """จำลองการส่งการแจ้งเตือนผ่าน SMS"""
    def handle_event(self, event_type: str, data: Dict[str, Any]) -> None:
        if event_type == "STOCK_IN_SUCCESS":
            message = f"รับเข้า {data['sku']} จำนวน {data['amount']} สำเร็จ (คงเหลือ {data['quantity']})"
            self._send(message)
        elif event_type == "STOCK_OUT_SUCCESS":
            message = f"ตัดจ่าย {data['sku']} จำนวน {data['amount']} สำเร็จ (คงเหลือ {data['quantity']})"
            self._send(message)

    def _send(self, message: str) -> None:
        print(f"[SMS] {message}")

class NotifierFactory:
    """Factory สำหรับสร้าง Notifier ตามประเภท"""
    @staticmethod
    def create(notifier_type: str) -> Notifier:
        if notifier_type.lower() == "email":
            return EmailNotifier()
        elif notifier_type.lower() == "sms":
            return SMSNotifier()
        else:
            raise ValueError(f"Unknown notifier type: {notifier_type}")
