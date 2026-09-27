"""NyxOS Event Bus — publish/subscribe system."""
import json
import threading
from datetime import datetime
from collections import defaultdict


class EventBus:
    def __init__(self, db=None):
        self.db = db
        self.subscribers = defaultdict(list)
        self._lock = threading.Lock()

    def subscribe(self, topic, callback):
        with self._lock:
            self.subscribers[topic].append(callback)

    def unsubscribe(self, topic, callback):
        with self._lock:
            if callback in self.subscribers[topic]:
                self.subscribers[topic].remove(callback)

    def publish(self, topic, payload=None):
        payload = payload or {}
        payload["_topic"] = topic
        payload["_ts"] = datetime.utcnow().isoformat()

        if self.db:
            self.db.execute(
                "INSERT INTO events(topic, payload) VALUES (?, ?)",
                (topic, json.dumps(payload)),
            )

        with self._lock:
            handlers = list(self.subscribers.get(topic, []))
            handlers += list(self.subscribers.get("*", []))

        for handler in handlers:
            try:
                handler(payload)
            except Exception as e:
                print(f"[EventBus] handler error on {topic}: {e}")

        return payload
