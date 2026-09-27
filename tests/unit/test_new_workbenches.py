import sys, os, tempfile
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from core.database.db import Database
from core.events.bus import EventBus
from security.wireless.wireless_workbench import WirelessWorkbench
from security.forensics.forensics_workbench import ForensicsWorkbench
from security.redteam.redteam_workbench import RedTeamWorkbench
from core.assets.asset_engine import AssetEngine


def _setup():
    f = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
    f.close()
    db = Database(f.name)
    bus = EventBus(db=db)
    cur = db.execute("INSERT INTO cases(name) VALUES (?)", ("WB New",))
    return db, bus, cur.lastrowid


def test_forensics_hash_file():
    db, bus, cid = _setup()
    tf = tempfile.NamedTemporaryFile(mode="w", delete=False)
    tf.write("hello nyxos")
    tf.close()
    wb = ForensicsWorkbench(db, bus)
    r = wb.discover(tf.name, {"case_id": cid})
    assert r.raw["sha256"]
    assert len(r.raw["sha256"]) == 64


def test_redteam_requires_authorized():
    db, bus, cid = _setup()
    wb = RedTeamWorkbench(db, bus)
    r = wb.discover("x", {"case_id": cid})
    assert len(r.findings) == 0


def test_redteam_suggests_for_smb():
    db, bus, cid = _setup()
    ae = AssetEngine(db, bus)
    ae.add(cid, "service", "10.0.0.1:445", {"service": "smb", "state": "open"})
    wb = RedTeamWorkbench(db, bus)
    r = wb.discover("10.0.0.1", {"case_id": cid, "authorized": True})
    assert len(r.findings) >= 1


def test_wireless_runs():
    db, bus, cid = _setup()
    wb = WirelessWorkbench(db, bus)
    r = wb.discover(None, {"case_id": cid})
    assert r.workbench == "wireless"
