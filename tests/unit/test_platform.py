"""Tests for STEP 07-09 — Plugin, Workbench, CLI."""
import sys, os, json, tempfile, subprocess
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from platform.plugin_sdk.plugin import PluginLoader, PluginManifest
from platform.workbench_sdk.workbench import Workbench, WorkbenchRegistry, WorkbenchResult


def test_plugin_manifest_validation():
    m = PluginManifest(name="nmap", version="1.0", author="nyx",
                       license="MIT", capabilities=["port_scan"])
    assert m.validate() is True


def test_plugin_manifest_missing_field():
    m = PluginManifest(name="x")
    try:
        m.validate()
        assert False, "should have raised"
    except ValueError:
        assert True


def test_plugin_loader_with_temp_plugin():
    tmpdir = tempfile.mkdtemp()
    pdir = os.path.join(tmpdir, "testplugin")
    os.makedirs(pdir)
    manifest = {
        "name": "testplugin", "version": "0.1", "author": "nyx",
        "license": "MIT", "capabilities": ["demo"],
    }
    with open(os.path.join(pdir, "manifest.json"), "w") as f:
        json.dump(manifest, f)
    loader = PluginLoader(extra_dirs=[tmpdir])
    loader.load_all()
    assert loader.get("testplugin") is not None


class DummyWorkbench(Workbench):
    name = "dummy"
    domain = "test"

    def discover(self, target, options=None):
        self._results.assets.append({"id": target, "type": "host"})
        return self._results

    def analyze(self, asset):
        return self._results


def test_workbench_registry():
    reg = WorkbenchRegistry()
    w = DummyWorkbench()
    reg.register(w)
    assert reg.get("dummy") is w
    assert len(reg.list()) == 1


def test_workbench_discover():
    w = DummyWorkbench()
    r = w.discover("10.0.0.1")
    assert r.workbench == "dummy"
    assert len(r.assets) == 1


def test_cli_ping():
    root = os.path.join(os.path.dirname(__file__), "../..")
    cli = os.path.join(root, "desktop/shell/nyxctl.py")
    out = subprocess.run([sys.executable, cli, "ping"],
                         capture_output=True, text=True)
    assert out.returncode == 0
    assert '"status": "ok"' in out.stdout
