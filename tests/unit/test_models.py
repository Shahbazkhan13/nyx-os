"""Tests for STEP 06 — Universal Data Model."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from core.models.entities import (
    Case, Asset, Service, Domain, Endpoint, Finding, Evidence,
    Vulnerability, Credential, Tool, Plugin, User,
    to_dict, link_asset_to_service, link_finding_to_asset,
    link_evidence_to_finding,
)


def test_case_and_user():
    c = Case(name="Test", description="desc")
    u = User(username="alice", role="admin")
    assert c.name == "Test"
    assert u.role == "admin"


def test_asset_and_service_linking():
    a = Asset(id=1, case_id=1, type="host", identifier="10.0.0.1")
    s = Service(id=1, port=22, protocol="tcp", name="ssh")
    s = link_asset_to_service(a, s)
    assert s.asset_id == 1


def test_finding_evidence_chain():
    a = Asset(id=5, case_id=1, type="host", identifier="10.0.0.5")
    f = Finding(id=1, case_id=1, title="Open SSH", severity="low")
    f = link_finding_to_asset(f, a)
    assert f.asset_id == 5

    e = Evidence(id=1, type="command", content="nmap -sV 10.0.0.5", hash="abc123")
    e = link_evidence_to_finding(e, f)
    assert e.finding_id == 1


def test_domain_endpoint():
    a = Asset(id=2, case_id=1, type="domain", identifier="example.com")
    d = Domain(id=1, name="example.com", resolved_ip="1.2.3.4")
    d.asset_id = a.id
    e = Endpoint(id=1, url="https://example.com/login", method="POST")
    e.asset_id = a.id
    assert d.asset_id == 2
    assert e.asset_id == 2


def test_credential_never_plain():
    c = Credential(case_id=1, username="admin", secret_ref="vault://abc", service="ssh")
    assert c.secret_ref.startswith("vault://")
    assert "password" not in to_dict(c)


def test_plugin_and_tool():
    t = Tool(name="nmap", version="7.94", category="network")
    p = Plugin(name="nmap-adapter", version="0.1",
               author="nyx", license="MIT",
               capabilities=["port_scan"], permissions=["network"])
    assert t.enabled is True
    assert "port_scan" in p.capabilities


def test_vulnerability():
    v = Vulnerability(cve_id="CVE-2024-0001", title="Sample", cvss=7.5)
    assert v.cvss == 7.5


def test_to_dict_roundtrip():
    a = Asset(id=1, case_id=1, type="host", identifier="10.0.0.1",
              metadata={"os": "linux"})
    d = to_dict(a)
    assert d["identifier"] == "10.0.0.1"
    assert d["metadata"]["os"] == "linux"
