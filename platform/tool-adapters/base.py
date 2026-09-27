"""NyxOS Tool Adapter base class"""
from abc import ABC, abstractmethod
import subprocess, time, json

class ToolAdapter(ABC):
    name = "unnamed"
    category = "generic"
    binary = None
    version = "0.0.0"

    @abstractmethod
    def run(self, target, options=None): pass

    @abstractmethod
    def parse(self, raw_output): pass

    def execute(self, args, timeout=300):
        if not self.binary:
            raise RuntimeError("No binary set")
        start = time.time()
        proc = subprocess.run(
            [self.binary] + args,
            capture_output=True, text=True, timeout=timeout
        )
        return {
            "stdout": proc.stdout,
            "stderr": proc.stderr,
            "returncode": proc.returncode,
            "duration": round(time.time() - start, 2),
        }
