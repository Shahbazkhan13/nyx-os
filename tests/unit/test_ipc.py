"""Tests for STEP 05 — IPC + Core API."""
import sys, os, tempfile, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from core.database.db import Database
from core.events.bus import EventBus
from core.api.api import CoreAPI
from core.ipc.server import IPCServer
from core.ipc.client import IPCClient


def _setup():
    f = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
    f.close()
    db = Database(f.name)
    bus = EventBus(db=db)
    api = CoreAPI(db, bus)
    return db, bus, api


def test_api_case_create_and_list():
    db, bus, api = _setup()
    c = api.case_create({"name": "Test Case"})
    assert c["id"] == 1
    lst = api.case_list()
    assert len(lst["cases"]) == 1


def test_api_asset_and_finding():
    db, bus, api = _setup()
    c = api.case_create({"name": "C1"})
    a = api.asset_add({"case_id": c["id"], "type": "host", "identifier": "10.0.0.1"})
    f = api.finding_add({"case_id": c["id"], "asset_id": a["id"],
                         "title": "Open port", "severity": "low"})
    assert f["id"] == 1
    findings = api.finding_list({"case_id": c["id"]})["findings"]
    assert len(findings) == 1


def test_ipc_server_client_roundtrip():
    db, bus, api = _setup()
    sock_path = tempfile.mktemp(suffix=".sock")
    server = IPCServer(path=sock_path, bus=bus)
    server.register("ping", api.ping)
    server.register("case_create", api.case_create)
    server.register("case_list", api.case_list)
    server.start()
    time.sleep(0.1)

    try:
        client = IPCClient(path=sock_path)
        assert client.call("ping")["status"] == "ok"
        client.call("case_create", {"name": "IPC Case"})
        cases = client.call("case_list")
        assert len(cases["cases"]) == 1
    finally:
        server.stop()
