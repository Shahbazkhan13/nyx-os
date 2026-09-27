import sys, os, tempfile
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from core.database.db import Database
from core.events.bus import EventBus
from core.assets.asset_engine import AssetEngine
from core.evidence.evidence_engine import EvidenceEngine
from core.findings.finding_engine import FindingEngine
from desktop.dashboard.dashboard import render


def _setup():
    f = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
    f.close()
    db = Database(f.name)
    bus = EventBus(db=db)
    # Create a case so foreign keys resolve
    cur = db.execute("INSERT INTO cases(name) VALUES (?)", ("Test Case",))
    case_id = cur.lastrowid
    return db, bus, case_id


def test_asset_engine_crud():
    db, bus, case_id = _setup()
    ae = AssetEngine(db, bus)
    aid = ae.add(case_id, "host", "10.0.0.1", {"os": "linux"})
    assert aid == 1
    a = ae.get(aid)
    assert a["identifier"] == "10.0.0.1"
    assert a["metadata"]["os"] == "linux"
    assert len(ae.list(case_id)) == 1
    ae.delete(aid)
    assert ae.get(aid) is None


def test_evidence_hash_chain():
    db, bus, case_id = _setup()
    fe = FindingEngine(db, bus)
    f = fe.add(case_id, "Test finding", "low")
    ee = EvidenceEngine(db, bus)
    r = ee.add(f["id"], "command", "nmap -sV 10.0.0.1")
    assert r["id"] == 1
    v = ee.verify(1)
    assert v["valid"] is True


def test_finding_engine_auto_risk():
    db, bus, case_id = _setup()
    fe = FindingEngine(db, bus)
    r = fe.add(case_id, "Open SSH", "high")
    assert r["risk_score"] > 0
    lst = fe.list(case_id)
    assert lst[0]["title"] == "Open SSH"


def test_dashboard_render():
    db, bus, case_id = _setup()
    out = render(db)
    assert "NyxOS Dashboard" in out
    assert "Cases:" in out
