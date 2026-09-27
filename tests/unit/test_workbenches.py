import sys, os, tempfile
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from core.database.db import Database
from core.events.bus import EventBus
from security.network.network_workbench import NetworkWorkbench
from security.web.web_workbench import WebWorkbench
from security.vulnerability.vuln_workbench import VulnerabilityWorkbench
from security.credentials.credentials_workbench import CredentialsWorkbench


def _setup():
    f = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
    f.close()
    db = Database(f.name)
    bus = EventBus(db=db)
    cur = db.execute("INSERT INTO cases(name) VALUES (?)", ("WB Test",))
    return db, bus, cur.lastrowid


def test_credentials_detects_md5():
    db, bus, cid = _setup()
    wb = CredentialsWorkbench(db, bus)
    r = wb.discover("5d41402abc4b2a76b9719d911017c592", {"case_id": cid})
    assert r.raw["hash_type"] == "md5"
    assert r.raw["strength"] == "weak"


def test_credentials_detects_sha256_as_ok():
    db, bus, cid = _setup()
    wb = CredentialsWorkbench(db, bus)
    r = wb.discover("a" * 64, {"case_id": cid})
    assert r.raw["hash_type"] == "sha256"
    assert r.raw["strength"] == "ok"


def test_network_workbench_runs():
    db, bus, cid = _setup()
    wb = NetworkWorkbench(db, bus)
    r = wb.discover("127.0.0.1", {"case_id": cid, "nmap_args": ["-F", "-T4"]})
    assert r.workbench == "network"


def test_web_workbench_runs():
    db, bus, cid = _setup()
    wb = WebWorkbench(db, bus)
    r = wb.discover("example.com", {"case_id": cid})
    assert r.workbench == "web"


def test_vuln_workbench_scans_assets():
    db, bus, cid = _setup()
    # Add a fake SMB service asset
    from core.assets.asset_engine import AssetEngine
    ae = AssetEngine(db, bus)
    ae.add(cid, "service", "10.0.0.1:445", {"service": "smb", "state": "open"})
    wb = VulnerabilityWorkbench(db, bus)
    r = wb.discover("10.0.0.1", {"case_id": cid})
    assert len(r.findings) >= 1
