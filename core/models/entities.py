"""NyxOS Universal Data Model — canonical entity definitions.

Every tool output MUST be normalized into these entities.
"""
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Optional, List, Dict, Any


@dataclass
class User:
    id: Optional[int] = None
    username: str = ""
    role: str = "analyst"
    created_at: str = ""


@dataclass
class Case:
    id: Optional[int] = None
    name: str = ""
    description: str = ""
    status: str = "open"
    created_at: str = ""
    updated_at: str = ""


@dataclass
class Target:
    """A target the user explicitly authorizes to test."""
    id: Optional[int] = None
    case_id: Optional[int] = None
    identifier: str = ""
    scope: str = ""
    authorized: bool = False


@dataclass
class Asset:
    """Any discovered thing: host, domain, IP, service, endpoint, db."""
    id: Optional[int] = None
    case_id: Optional[int] = None
    type: str = "host"       # host | domain | ip | service | endpoint | db | cloud | container
    identifier: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = ""


@dataclass
class Host:
    id: Optional[int] = None
    asset_id: Optional[int] = None
    hostname: str = ""
    ip: str = ""
    os: str = ""
    open_ports: List[int] = field(default_factory=list)


@dataclass
class Service:
    id: Optional[int] = None
    asset_id: Optional[int] = None
    port: int = 0
    protocol: str = "tcp"
    name: str = ""
    version: str = ""
    banner: str = ""


@dataclass
class Domain:
    id: Optional[int] = None
    asset_id: Optional[int] = None
    name: str = ""
    registrar: str = ""
    resolved_ip: str = ""
    subdomains: List[str] = field(default_factory=list)


@dataclass
class Endpoint:
    id: Optional[int] = None
    asset_id: Optional[int] = None
    url: str = ""
    method: str = "GET"
    status_code: Optional[int] = None
    parameters: List[str] = field(default_factory=list)


@dataclass
class Database:
    id: Optional[int] = None
    asset_id: Optional[int] = None
    engine: str = ""
    host: str = ""
    port: int = 0
    name: str = ""


@dataclass
class Credential:
    """Sensitive — stored securely, never logged in plain form."""
    id: Optional[int] = None
    case_id: Optional[int] = None
    username: str = ""
    secret_ref: str = ""     # reference to secure store, not raw
    service: str = ""
    valid: bool = False


@dataclass
class Finding:
    id: Optional[int] = None
    case_id: Optional[int] = None
    asset_id: Optional[int] = None
    title: str = ""
    severity: str = "info"
    risk_score: float = 0.0
    details: Dict[str, Any] = field(default_factory=dict)
    created_at: str = ""


@dataclass
class Vulnerability:
    """A known CVE / weakness mapped to a finding."""
    id: Optional[int] = None
    cve_id: str = ""
    title: str = ""
    cvss: float = 0.0
    description: str = ""
    references: List[str] = field(default_factory=list)


@dataclass
class Evidence:
    id: Optional[int] = None
    finding_id: Optional[int] = None
    type: str = "command"     # command | request | response | screenshot | log | file
    content: str = ""
    hash: str = ""
    created_at: str = ""


@dataclass
class Event:
    id: Optional[int] = None
    topic: str = ""
    payload: Dict[str, Any] = field(default_factory=dict)
    created_at: str = ""


@dataclass
class Task:
    id: Optional[int] = None
    case_id: Optional[int] = None
    title: str = ""
    status: str = "pending"
    assignee: str = ""


@dataclass
class Report:
    id: Optional[int] = None
    case_id: Optional[int] = None
    format: str = "markdown"   # markdown | html | pdf | json | csv
    path: str = ""
    created_at: str = ""


@dataclass
class Lab:
    id: Optional[int] = None
    name: str = ""
    domain: str = ""
    isolated: bool = True
    description: str = ""


@dataclass
class Tool:
    id: Optional[int] = None
    name: str = ""
    version: str = ""
    category: str = ""
    enabled: bool = True


@dataclass
class Plugin:
    name: str = ""
    version: str = ""
    author: str = ""
    license: str = ""
    capabilities: List[str] = field(default_factory=list)
    permissions: List[str] = field(default_factory=list)


def to_dict(entity) -> Dict[str, Any]:
    return asdict(entity)


# ---------- Relationship helpers ----------

def link_asset_to_service(asset: Asset, service: Service) -> Service:
    service.asset_id = asset.id
    return service


def link_asset_to_domain(asset: Asset, domain: Domain) -> Domain:
    domain.asset_id = asset.id
    return domain


def link_asset_to_endpoint(asset: Asset, endpoint: Endpoint) -> Endpoint:
    endpoint.asset_id = asset.id
    return endpoint


def link_finding_to_asset(finding: Finding, asset: Asset) -> Finding:
    finding.asset_id = asset.id
    return finding


def link_evidence_to_finding(evidence: Evidence, finding: Finding) -> Evidence:
    evidence.finding_id = finding.id
    return evidence
