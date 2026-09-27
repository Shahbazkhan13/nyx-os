"""NyxOS IPC protocol — JSON messages over Unix sockets."""
import json
from datetime import datetime

MSG_REQUEST = "request"
MSG_RESPONSE = "response"
MSG_EVENT = "event"
MSG_ERROR = "error"


def make_message(msg_type, method=None, params=None, result=None, error=None, msg_id=None):
    return {
        "type": msg_type,
        "id": msg_id or datetime.utcnow().timestamp(),
        "method": method,
        "params": params or {},
        "result": result,
        "error": error,
        "ts": datetime.utcnow().isoformat(),
    }


def encode(msg):
    return (json.dumps(msg) + "\n").encode("utf-8")


def decode(data):
    return json.loads(data.decode("utf-8").strip())
