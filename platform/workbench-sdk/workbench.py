"""NyxOS Workbench base class"""
from abc import ABC, abstractmethod

class Workbench(ABC):
    name = "unnamed"
    domain = "generic"

    def __init__(self, ctx):
        self.ctx = ctx

    @abstractmethod
    def discover(self, target): pass

    @abstractmethod
    def analyze(self, asset): pass

    def report(self, findings):
        return {"workbench": self.name, "findings": findings}
