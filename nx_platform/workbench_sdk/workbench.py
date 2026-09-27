"""NyxOS Workbench SDK — base class + registry.

Every security domain implements a Workbench.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List
from dataclasses import dataclass, field, asdict


@dataclass
class WorkbenchResult:
    workbench: str = ""
    domain: str = ""
    assets: List[Dict[str, Any]] = field(default_factory=list)
    findings: List[Dict[str, Any]] = field(default_factory=list)
    evidence: List[Dict[str, Any]] = field(default_factory=list)
    raw: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self):
        return asdict(self)


class Workbench(ABC):
    name = "unnamed"
    domain = "generic"
    description = ""

    def __init__(self, ctx=None):
        self.ctx = ctx or {}
        self._results = WorkbenchResult(workbench=self.name, domain=self.domain)

    @abstractmethod
    def discover(self, target, options=None) -> WorkbenchResult:
        """Run the initial discovery step."""
        pass

    @abstractmethod
    def analyze(self, asset) -> WorkbenchResult:
        """Analyze a specific asset."""
        pass

    def report(self) -> Dict[str, Any]:
        return self._results.to_dict()


class WorkbenchRegistry:
    def __init__(self):
        self._workbenches: Dict[str, Workbench] = {}

    def register(self, workbench: Workbench):
        self._workbenches[workbench.name] = workbench
        return workbench

    def get(self, name):
        return self._workbenches.get(name)

    def list(self):
        return [
            {"name": w.name, "domain": w.domain, "description": w.description}
            for w in self._workbenches.values()
        ]
