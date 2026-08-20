from typing import Protocol, Dict, List, Any
from collections import defaultdict

class EventSubscriber(Protocol):
    """โปรโตคอลสำหรับผู้ที่ต้องการรับการแจ้งเตือน (Observer)"""
    def handle_event(self, event_type: str, data: Dict[str, Any]) -> None:
        ...

class EventPublisher:
    """ตัวจัดการการกระจายเหตุการณ์ (Subject)"""
    def __init__(self):
        # เก็บรายชื่อ subscribers แยกตามประเภทของ event
        self._subscribers: Dict[str, List[EventSubscriber]] = defaultdict(list)

    def subscribe(self, event_type: str, subscriber: EventSubscriber) -> None:
        """ลงทะเบียนรับข่าวสารตามประเภท event_type"""
        if subscriber not in self._subscribers[event_type]:
            self._subscribers[event_type].append(subscriber)

    def unsubscribe(self, event_type: str, subscriber: EventSubscriber) -> None:
        """ยกเลิกการลงทะเบียน"""
        if subscriber in self._subscribers[event_type]:
            self._subscribers[event_type].remove(subscriber)

    def publish(self, event_type: str, data: Dict[str, Any]) -> None:
        """กระจายข่าวสารไปยัง subscribers ทุกตัวที่ลงทะเบียนไว้"""
        for subscriber in self._subscribers.get(event_type, []):
            subscriber.handle_event(event_type, data)
