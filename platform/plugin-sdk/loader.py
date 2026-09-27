"""NyxOS Plugin Loader (skeleton)"""
import json, os, sys

PLUGIN_DIRS = ["/opt/nyxos/plugins", os.path.expanduser("~/.nyxos/plugins")]

class Plugin:
    def __init__(self, manifest, path):
        self.manifest = manifest
        self.path = path

def validate_manifest(m):
    required = ["name", "version", "author", "license", "capabilities"]
    return all(k in m for k in required)

def load_plugins():
    plugins = []
    for d in PLUGIN_DIRS:
        if not os.path.isdir(d): continue
        for name in os.listdir(d):
            mpath = os.path.join(d, name, "manifest.json")
            if not os.path.isfile(mpath): continue
            with open(mpath) as f:
                m = json.load(f)
            if validate_manifest(m):
                plugins.append(Plugin(m, os.path.join(d, name)))
    return plugins

if __name__ == "__main__":
    for p in load_plugins():
        print(p.manifest["name"], p.manifest["version"])
