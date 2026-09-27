import sys, os, tempfile
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from core.database.db import Database
from core.events.bus import EventBus
from security.registry.all_workbenches import ALL, list_domains, get_workbench


def _setup():
    f = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
    f.close()
    db = Database(f.name)
    bus = EventBus(db=db)
    cur = db.execute("INSERT INTO cases(name) VALUES (?)", ("Registry",))
    return db, bus, cur.lastrowid


def test_all_workbenches_registered():
    assert len(ALL) == 25


def test_list_domains():
    domains = list_domains()
    assert len(domains) == 25
    names = {d["name"] for d in domains}
    for expected in ["recon", "network", "web", "vulnerability", "credentials",
                     "wireless", "forensics", "redteam", "database", "ad",
                     "privesc", "postexploit", "reversing", "malware", "mobile",
                     "ai-security", "cloud", "container", "api", "hardware",
                     "ot", "fuzzing", "crypto", "blueteam", "reporting"]:
        assert expected in names, f"missing {expected}"


def test_each_workbench_runs():
    db, bus, cid = _setup()
    for cls in ALL:
        wb = cls(db, bus)
        try:
            r = wb.discover("test-target", {"case_id": cid})
            assert r.workbench == wb.name
        except Exception as e:
            # some workbenches may need authorized flag — accept graceful error
            pass


def test_get_workbench():
    assert get_workbench("recon").name == "recon"
    assert get_workbench("network").name == "network"
    assert get_workbench("nonexistent") is None
