#!/usr/bin/env python3
"""NyxOS Native Desktop — GTK4 + Adwaita."""
import sys, os, json, threading, subprocess
import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw, Gio, GLib, Gdk

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from core.database.db import Database
from core.events.bus import EventBus
from core.api.api import CoreAPI
from security.registry.all_workbenches import list_domains, get_workbench


CSS = """
window, .background { background-color: #0d1117; color: #c9d1d9; }
.header-bar { background: #161b22; border-bottom: 1px solid #30363d; }
.sidebar { background: #0d1117; border-right: 1px solid #30363d; }
.sidebar-item {
    padding: 10px 16px; border-radius: 8px; margin: 2px 8px;
    color: #8b949e; font-size: 14px;
}
.sidebar-item:hover { background: #161b22; color: #c9d1d9; }
.sidebar-item.active { background: #1f6feb; color: white; }
.sidebar-title {
    color: #58a6ff; font-size: 11px; font-weight: bold;
    padding: 16px 16px 6px 16px; text-transform: uppercase;
}
.content-title { font-size: 22px; font-weight: bold; color: #58a6ff; margin: 20px; }
.card {
    background: #161b22; border: 1px solid #30363d;
    border-radius: 10px; padding: 20px; margin: 8px 20px;
}
.stat-number { font-size: 32px; font-weight: bold; color: #58a6ff; }
.stat-label { font-size: 11px; color: #8b949e; text-transform: uppercase; }
.terminal {
    background: #000; color: #c9d1d9;
    font-family: "JetBrains Mono", "Courier New", monospace;
    font-size: 13px; padding: 12px;
    border-radius: 8px;
}
.badge { padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: bold; }
.badge-critical { background: #7d0c0c; color: white; }
.badge-high { background: #a33; color: white; }
.badge-medium { background: #a70; color: white; }
.badge-low { background: #365314; color: white; }
.badge-info { background: #1f4f8b; color: white; }
.workbench-tile {
    background: #161b22; border: 1px solid #30363d;
    border-radius: 10px; padding: 16px; margin: 6px;
    min-width: 180px; min-height: 100px;
}
.workbench-tile:hover { border-color: #58a6ff; }
.workbench-name { color: #58a6ff; font-size: 15px; font-weight: bold; }
.workbench-desc { color: #8b949e; font-size: 11px; margin-top: 6px; }
"""


def _db():
    return Database()


class NyxOSWindow(Adw.ApplicationWindow):
    def __init__(self, app):
        super().__init__(application=app, title="NyxOS")
        self.set_default_size(1400, 900)

        css = Gtk.CssProvider()
        css.load_from_data(CSS.encode())
        Gtk.StyleContext.add_provider_for_display(
            Gdk.Display.get_default(), css,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.set_content(root)

        # Header bar
        hb = Adw.HeaderBar()
        hb.add_css_class("header-bar")
        title = Gtk.Label(label="🛡️  NyxOS")
        title.add_css_class("content-title")
        title.set_margin_start(10)
        hb.set_title_widget(title)
        root.append(hb)

        # Main split
        main = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        main.set_vexpand(True)
        root.append(main)

        # Sidebar
        sidebar = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        sidebar.add_css_class("sidebar")
        sidebar.set_size_request(240, -1)
        sidebar_scroll = Gtk.ScrolledWindow()
        sidebar_scroll.set_child(sidebar)
        sidebar_scroll.set_size_request(240, -1)
        main.append(sidebar_scroll)

        self._add_sidebar_title(sidebar, "Overview")
        self._add_sidebar_item(sidebar, "Dashboard", self._view_dashboard)
        self._add_sidebar_item(sidebar, "Findings", self._view_findings)
        self._add_sidebar_item(sidebar, "Assets", self._view_assets)
        self._add_sidebar_item(sidebar, "Timeline", self._view_timeline)

        self._add_sidebar_title(sidebar, "Workbenches")
        for d in list_domains():
            self._add_sidebar_item(sidebar, d["name"], self._make_wb_handler(d["name"]))

        self._add_sidebar_title(sidebar, "System")
        self._add_sidebar_item(sidebar, "Terminal", self._view_terminal)
        self._add_sidebar_item(sidebar, "About", self._view_about)

        # Content area
        self.content_scroll = Gtk.ScrolledWindow()
        self.content_scroll.set_vexpand(True)
        self.content_scroll.set_hexpand(True)
        main.append(self.content_scroll)

        # Status bar
        status = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        status.set_margin_top(6); status.set_margin_bottom(6)
        status.set_margin_start(12); status.set_margin_end(12)
        self.status_label = Gtk.Label(label="Ready")
        self.status_label.set_halign(Gtk.Align.START)
        self.status_label.add_css_class("stat-label")
        status.append(self.status_label)
        root.append(status)

        self._view_dashboard()

    def _add_sidebar_title(self, box, text):
        lbl = Gtk.Label(label=text, xalign=0)
        lbl.add_css_class("sidebar-title")
        box.append(lbl)

    def _add_sidebar_item(self, box, text, cb):
        btn = Gtk.Button(label=text, has_frame=False)
        btn.add_css_class("sidebar-item")
        btn.connect("clicked", lambda *_: cb())
        box.append(btn)

    def _make_wb_handler(self, name):
        def h():
            self._view_workbench(name)
        return h

    def _clear(self):
        self.content_scroll.set_child(None)

    def _set_content(self, widget):
        self.content_scroll.set_child(widget)

    def _status(self, text):
        self.status_label.set_text(text)

    # ---------- Views ----------
    def _view_dashboard(self):
        self._status("Dashboard")
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        title = Gtk.Label(label="Dashboard", xalign=0)
        title.add_css_class("content-title")
        box.append(title)

        db = _db()
        stats = [
            ("Cases",    db.fetchall("SELECT COUNT(*) AS n FROM cases")[0]["n"]),
            ("Assets",   db.fetchall("SELECT COUNT(*) AS n FROM assets")[0]["n"]),
            ("Findings", db.fetchall("SELECT COUNT(*) AS n FROM findings")[0]["n"]),
            ("Evidence", db.fetchall("SELECT COUNT(*) AS n FROM evidence")[0]["n"]),
        ]

        row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=15)
        row.set_margin_start(20); row.set_margin_end(20)
        for label, val in stats:
            card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
            card.add_css_class("card")
            n = Gtk.Label(label=str(val), xalign=0); n.add_css_class("stat-number")
            l = Gtk.Label(label=label.upper(), xalign=0); l.add_css_class("stat-label")
            card.append(n); card.append(l)
            row.append(card)
        box.append(row)

        # Workbench grid
        wb_title = Gtk.Label(label="Workbenches (25)", xalign=0)
        wb_title.add_css_class("content-title")
        wb_title.set_margin_top(20)
        box.append(wb_title)

        flow = Gtk.FlowBox()
        flow.set_margin_start(20); flow.set_margin_end(20)
        flow.set_row_spacing(8); flow.set_column_spacing(8)
        flow.set_selection_mode(Gtk.SelectionMode.NONE)
        for d in list_domains():
            tile = Gtk.Button(has_frame=False)
            tile.add_css_class("workbench-tile")
            inner = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
            n = Gtk.Label(label=d["name"], xalign=0); n.add_css_class("workbench-name")
            ds = Gtk.Label(label=d["description"][:50], xalign=0)
            ds.add_css_class("workbench-desc"); ds.set_wrap(True)
            inner.append(n); inner.append(ds)
            tile.set_child(inner)
            tile.connect("clicked", lambda _, nm=d["name"]: self._view_workbench(nm))
            flow.append(tile)
        box.append(flow)
        self._set_content(box)

    def _view_findings(self):
        self._status("Findings")
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        t = Gtk.Label(label="Findings", xalign=0); t.add_css_class("content-title")
        box.append(t)

        db = _db()
        rows = db.fetchall("SELECT * FROM findings ORDER BY risk_score DESC LIMIT 100")
        list_box = Gtk.ListBox()
        list_box.set_margin_start(20); list_box.set_margin_end(20)
        for r in rows:
            row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
            row.set_margin_top(8); row.set_margin_bottom(8)
            sev = r["severity"].lower()
            b = Gtk.Label(label=f" {sev.upper()} ")
            b.add_css_class("badge"); b.add_css_class(f"badge-{sev}")
            row.append(b)
            row.append(Gtk.Label(label=r["title"], xalign=0, hexpand=True))
            row.append(Gtk.Label(label=f"risk {r['risk_score']}"))
            lb = Gtk.ListBoxRow(); lb.set_child(row); list_box.append(lb)
        if not rows:
            list_box.append(Gtk.Label(label="No findings yet."))
        box.append(list_box)
        self._set_content(box)

    def _view_assets(self):
        self._status("Assets")
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        t = Gtk.Label(label="Assets", xalign=0); t.add_css_class("content-title")
        box.append(t)
        db = _db()
        rows = db.fetchall("SELECT * FROM assets ORDER BY id DESC LIMIT 100")
        lb = Gtk.ListBox(); lb.set_margin_start(20); lb.set_margin_end(20)
        for r in rows:
            row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
            row.append(Gtk.Label(label=r["type"], width_chars=10, xalign=0))
            row.append(Gtk.Label(label=r["identifier"], xalign=0, hexpand=True))
            lbr = Gtk.ListBoxRow(); lbr.set_child(row); lb.append(lbr)
        if not rows:
            lb.append(Gtk.Label(label="No assets yet."))
        box.append(lb)
        self._set_content(box)

    def _view_timeline(self):
        self._status("Timeline")
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        t = Gtk.Label(label="Event Timeline", xalign=0); t.add_css_class("content-title")
        box.append(t)
        db = _db()
        rows = db.fetchall("SELECT * FROM events ORDER BY id DESC LIMIT 100")
        lb = Gtk.ListBox(); lb.set_margin_start(20); lb.set_margin_end(20)
        for r in rows:
            row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
            row.append(Gtk.Label(label=r["created_at"][:19]))
            row.append(Gtk.Label(label=r["topic"], xalign=0, hexpand=True))
            lbr = Gtk.ListBoxRow(); lbr.set_child(row); lb.append(lbr)
        if not rows:
            lb.append(Gtk.Label(label="No events yet."))
        box.append(lb)
        self._set_content(box)

    def _view_workbench(self, name):
        cls = get_workbench(name)
        if not cls:
            self._status("Not found")
            return
        self._status(f"Workbench: {name}")
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        t = Gtk.Label(label=name.title(), xalign=0); t.add_css_class("content-title")
        box.append(t)

        info = Gtk.Label(label=cls.description, xalign=0)
        info.set_margin_start(20); info.add_css_class("workbench-desc")
        box.append(info)

        # Input row
        row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        row.set_margin_start(20); row.set_margin_end(20); row.set_margin_top(15)
        case_entry = Gtk.Entry(); case_entry.set_placeholder_text("Case ID")
        case_entry.set_width_chars(10)
        target_entry = Gtk.Entry(); target_entry.set_placeholder_text("Target")
        target_entry.set_hexpand(True)
        run_btn = Gtk.Button(label="Run")
        run_btn.add_css_class("suggested-action")
        row.append(case_entry); row.append(target_entry); row.append(run_btn)
        box.append(row)

        output = Gtk.Label(label="Ready.", xalign=0)
        output.set_margin_start(20); output.set_margin_end(20); output.set_margin_top(15)
        output.set_wrap(True); output.set_selectable(True)
        output.add_css_class("terminal")
        box.append(output)

        def on_run(_):
            try:
                cid = int(case_entry.get_text().strip() or "0")
            except ValueError:
                output.set_text("Error: Case ID must be a number")
                return
            tgt = target_entry.get_text().strip()
            output.set_text("Running...")
            def worker():
                try:
                    db = _db(); bus = EventBus(db=db)
                    wb = cls(db, bus)
                    res = wb.discover(tgt, {"case_id": cid})
                    txt = json.dumps(res.to_dict(), indent=2, default=str)
                    GLib.idle_add(lambda: output.set_text(txt[:6000]))
                except Exception as e:
                    GLib.idle_add(lambda: output.set_text(f"Error: {e}"))
            threading.Thread(target=worker, daemon=True).start()

        run_btn.connect("clicked", on_run)
        self._set_content(box)

    def _view_terminal(self):
        self._status("Terminal")
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        t = Gtk.Label(label="Terminal", xalign=0); t.add_css_class("content-title")
        box.append(t)
        hint = Gtk.Label(label="nyxctl commands — try: ping, case-list, ls-workbenches",
                         xalign=0)
        hint.set_margin_start(20); hint.add_css_class("workbench-desc")
        box.append(hint)

        entry = Gtk.Entry()
        entry.set_placeholder_text("nyxctl ping")
        entry.set_margin_start(20); entry.set_margin_end(20); entry.set_margin_top(10)
        box.append(entry)

        out = Gtk.Label(label="", xalign=0)
        out.set_margin_start(20); out.set_margin_end(20); out.set_margin_top(15)
        out.set_wrap(True); out.set_selectable(True)
        out.add_css_class("terminal")
        box.append(out)

        def on_enter(_):
            cmd = entry.get_text().strip()
            if not cmd: return
            parts = cmd.split()
            if parts[0] == "nyxctl":
                parts = parts[1:]
            try:
                cli = os.path.join(os.path.dirname(__file__), "../shell/nyxctl.py")
                res = subprocess.run([sys.executable, cli] + parts,
                                     capture_output=True, text=True, timeout=30)
                out.set_text(res.stdout or res.stderr)
            except Exception as e:
                out.set_text(str(e))
            entry.set_text("")
        entry.connect("activate", on_enter)
        self._set_content(box)

    def _view_about(self):
        self._status("About")
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        t = Gtk.Label(label="About NyxOS", xalign=0); t.add_css_class("content-title")
        box.append(t)
        txt = Gtk.Label(xalign=0)
        txt.set_markup(
            "<b>NyxOS 0.1.0</b>\n\n"
            "Installable, Linux-based Cybersecurity Operating Platform.\n"
            "Built on Debian bookworm. Local-first. 25 security domains.\n\n"
            "Not a Kali clone — a unified security platform.")
        txt.set_margin_start(20); txt.set_margin_end(20)
        box.append(txt)
        self._set_content(box)


class NyxApp(Adw.Application):
    def __init__(self):
        super().__init__(application_id="org.nyxos.NyxOS",
                         flags=Gio.ApplicationFlags.DEFAULT_FLAGS)
        self.connect("activate", self._on_activate)

    def _on_activate(self, app):
        win = NyxOSWindow(app)
        win.present()


def main():
    app = NyxApp()
    return app.run(sys.argv)


if __name__ == "__main__":
    sys.exit(main())
