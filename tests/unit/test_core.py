"""Tests for STEP 04 — Core System Services."""
import sys, os, tempfile
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from core.database.db import Database
from core.events.bus import EventBus
from core.identity.identity import Identity
from core.logging.logger import get_logger


def _fresh_db():
    f = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
    path = f.name
    f.close()
    return Database(path)


def test_database_creates_schema():
    db = _fresh_db()
    tables = db.fetchall("SELECT name FROM sqlite_master WHERE type='table'")
    names = {t["name"] for t in tables}
    for t in ["cases", "assets", "findings", "evidence", "events"]:
        assert t in names


def test_event_bus_publish_subscribe():
    db = _fresh_db()
    bus = EventBus(db=db)
    received = []
    bus.subscribe("asset.created", lambda p: received.append(p))
    bus.publish("asset.created", {"id": 1})
    assert len(received) == 1
    assert received[0]["id"] == 1
    rows = db.fetchall("SELECT * FROM events")
    assert len(rows) == 1


def test_identity_permissions():
    db = _fresh_db()
    ident = Identity(db)
    ident.create_user("alice", "admin")
    ident.create_user("bob", "viewer")
    assert ident.has_permission("alice", "manage_users") is True
    assert ident.has_permission("bob", "write") is False
    assert ident.has_permission("nobody", "read") is False


def test_logger_writes():
    log = get_logger("test_nyxos")
    log.info("hello from test")
    assert log is not None
