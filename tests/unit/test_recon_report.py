import sys, os, tempfile
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from core.database.db import Database
from core.events.bus import EventBus
from security.recon.recon_workbench import ReconWorkbench
from reporting.reporter import Reporter
from learning.labs.registry import list_labs
from ai.assistant.assistant import Assistant


def _setup():
    f = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
    f.close()
    db = Database(f.name)
    bus = EventBus(db=db)
    cur = db.execute("INSERT INTO cases(name) VALUES (?)", ("Recon Test",))
    return db, bus, cur.lastrowid


def test_recon_workbench_registers_asset():
    db, bus, case_id = _setup()
    rb = ReconWorkbench(db, bus)
    res = rb.discover("localhost", {"case_id": case_id})
    assert res.workbench == "recon"
    assert len(res.assets) >= 1
    assets = rb.assets.list(case_id)
    assert any(a["identifier"] == "localhost" for a in assets)


def test_reporter_markdown_and_json():
    db, bus, case_id = _setup()
    rep = Reporter(db)
    md = rep.to_markdown(case_id)
    js = rep.to_json(case_id)
    assert "Recon Test" in md
    assert '"case"' in js


def test_reporter_save_file():
    db, bus, case_id = _setup()
    rep = Reporter(db)
    tmp = tempfile.mkdtemp()
    p = os.path.join(tmp, "report.md")
    rep.save(case_id, p, "markdown")
    assert os.path.isfile(p)


def test_labs_registry():
    labs = list_labs()
    assert len(labs) >= 20
    assert all(l["isolated"] for l in labs)


def test_assistant_stub():
    a = Assistant()
    r = a.explain_tool("nmap")
    assert r["tool"] == "nmap"
