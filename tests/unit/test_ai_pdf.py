import sys, os, tempfile
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from core.database.db import Database
from core.events.bus import EventBus
from core.assets.asset_engine import AssetEngine
from core.findings.finding_engine import FindingEngine
from core.evidence.evidence_engine import EvidenceEngine
from ai.assistant.assistant import Assistant
from reporting.pdf_reporter import build_pdf_html
from desktop.web.timeline import render_events


def _setup():
    f = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
    f.close()
    db = Database(f.name)
    bus = EventBus(db=db)
    cid = db.execute("INSERT INTO cases(name) VALUES (?)", ("AI Test",)).lastrowid
    return db, bus, cid


def test_assistant_explains_nmap():
    a = Assistant()
    r = a.explain_tool("nmap")
    assert "port" in r["what"].lower()


def test_assistant_next_steps():
    a = Assistant()
    r = a.suggest_next({"domain": "recon"})
    assert len(r["suggestions"]) >= 1


def test_assistant_explains_finding():
    a = Assistant()
    r = a.explain_finding({"title": "Test", "severity": "critical"})
    assert "immediately" in r["advice"].lower() or "fix" in r["advice"].lower()


def test_pdf_report_renders():
    db, bus, cid = _setup()
    ae = AssetEngine(db, bus)
    fe = FindingEngine(db, bus)
    ae.add(cid, "host", "10.0.0.1")
    fe.add(cid, "Open port", "high")
    html = build_pdf_html(db, cid)
    assert "NyxOS Security Report" in html
    assert "10.0.0.1" in html


def test_timeline_render():
    db, bus, cid = _setup()
    bus.publish("test.event", {"x": 1})
    out = render_events(db)
    assert "Event Timeline" in out
    assert "test.event" in out
