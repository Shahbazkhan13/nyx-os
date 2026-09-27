"""NyxOS Plugin System — plugin manifest + loader."""
import json
import os
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import List, Dict, Any

REQUIRED_FIELDS = ["name", "version", "author", "license", "capabilities"]
PLUGIN_DIRS = [
    "/opt/nyxos/plugins",
    os.path.expanduser("~/.nyxos/plugins"),
    os.path.join(os.path.dirname(__file__), "../../plugins"),
]


@dataclass
class PluginManifest:
    name: str = ""
    version: str = ""
    author: str = ""
    license: str = ""
    description: str = ""
    binary: str = ""
    entrypoint: str = ""
    dependencies: List[str] = field(default_factory=list)
    capabilities: List[str] = field(default_factory=list)
    permissions: List[str] = field(default_factory=list)
    input_schema: Dict[str, Any] = field(default_factory=dict)
    output_schema: Dict[str, Any] = field(default_factory=dict)

    def validate(self):
        missing = [f for f in REQUIRED_FIELDS if not getattr(self, f)]
        if missing:
            raise ValueError(f"Plugin missing required fields: {missing}")
        return True

    def to_dict(self):
        return asdict(self)


@dataclass
class Plugin:
    manifest: PluginManifest
    path: str
    loaded: bool = False


class PluginLoader:
    def __init__(self, extra_dirs=None):
        self.dirs = list(PLUGIN_DIRS)
        if extra_dirs:
            self.dirs.extend(extra_dirs)
        self.plugins: Dict[str, Plugin] = {}

    def discover(self):
        found = []
        for d in self.dirs:
            if not os.path.isdir(d):
                continue
            for name in os.listdir(d):
                mpath = os.path.join(d, name, "manifest.json")
                if os.path.isfile(mpath):
                    found.append(mpath)
        return found

    def load_manifest(self, manifest_path):
        with open(manifest_path) as f:
            data = json.load(f)
        m = PluginManifest(**{k: v for k, v in data.items() if k in PluginManifest().__dict__})
        m.validate()
        return m

    def load_all(self):
        for mpath in self.discover():
            try:
                m = self.load_manifest(mpath)
                p = Plugin(manifest=m, path=os.path.dirname(mpath), loaded=True)
                self.plugins[m.name] = p
            except Exception as e:
                print(f"[PluginLoader] failed {mpath}: {e}")
        return self.plugins

    def get(self, name):
        return self.plugins.get(name)

    def list(self):
        return list(self.plugins.values())
