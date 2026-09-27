"""NyxOS Web Dashboard — auto-generates UI for all registered workbenches."""
import os, sys, json, io, traceback
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs, urlencode
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from core.database.db import Database
from core.events.bus import EventBus
from core.api.api import CoreAPI
from reporting.reporter import Reporter
from security.registry.all_workbenches import ALL, list_domains, get_workbench


PORT = 8080


def _db():
    return Database()


STYLE = """
body { font-family: 'Segoe UI', system-ui, sans-serif; background:#0d1117; color:#c9d1d9; margin:0; }
header { background:#161b22; border-bottom:1px solid #30363d; padding:15px 30px; display:flex; align-items:center; gap:30px; }
header h1 { color:#58a6ff; margin:0; font-size:22px; }
nav a { color:#8b949e; margin-right:18px; text-decoration:none; font-size:14px; }
nav a:hover, nav a.active { color:#58a6ff; }
main { padding:25px 30px; max-width:1200px; }
h2 { color:#58a6ff; border-bottom:1px solid #30363d; padding-bottom:8px; margin-top:0; }
.card { background:#161b22; border:1px solid #30363d; padding:20px; margin:15px 0; border-radius:8px; }
.btn { background:#238636; color:white; padding:8px 16px; border:none; border-radius:6px; cursor:pointer; font-size:14px; }
.btn:hover { background:#2ea043; }
.btn-danger { background:#da3633; }
input, select, textarea { background:#0d1117; color:#c9d1d9; border:1px solid #30363d; padding:8px; border-radius:6px; font-size:14px; font-family:inherit; }
input:focus, select:focus, textarea:focus { outline:none; border-color:#58a6ff; }
table { width:100%; border-collapse:collapse; margin-top:10px; }
th,td { text-align:left; padding:10px; border-bottom:1px solid #30363d; }
th { color:#8b949e; font-weight:600; font-size:13px; text-transform:uppercase; }
tr:hover { background:#1c2128; }
.badge { padding:3px 8px; border-radius:4px; font-size:11px; font-weight:bold; }
.critical{background:#7d0c0c;color:#fff;} .high{background:#a33;color:#fff;}
.medium{background:#a70;color:#fff;} .low{background:#365314;color:#fff;}
.info{background:#1f4f8b;color:#fff;}
pre { background:#0d1117; padding:15px; border-radius:6px; overflow:auto; max-height:500px; border:1px solid #30363d; font-size:13px; }
.grid { display:grid; grid-template-columns:repeat(auto-fill, minmax(220px,1fr)); gap:15px; }
.tile { background:#161b22; border:1px solid #30363d; padding:18px; border-radius:8px; text-decoration:none; color:#c9d1d9; transition:0.15s; }
.tile:hover { border-color:#58a6ff; transform:translateY(-2px); }
.tile h3 { color:#58a6ff; margin:0 0 8px 0; font-size:16px; }
.tile p { margin:0; color:#8b949e; font-size:12px; }
.stat { font-size:32px; font-weight:bold; color:#58a6ff; }
.stat-label { color:#8b949e; font-size:12px; text-transform:uppercase; }
.row { display:flex; gap:10px; align-items:center; flex-wrap:wrap; }
"""


def page(content, active=""):
    nav_items = [
        ("/", "Dashboard"),
        ("/cases", "Cases"),
        ("/workbenches", "Workbenches"),
        ("/findings", "Findings"),
        ("/assets", "Assets"),
        ("/reports", "Reports"),
    ]
    nav = "".join(
        f'<a href="{url}" class="{"active" if url == active else ""}">{label}</a>'
        for url, label in nav_items
    )
    return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>NyxOS</title>
<style>{STYLE}</style></head>
<body>
<header>
  <h1>&#x1F6E1;&#xFE0F; NyxOS</h1>
  <nav>{nav}</nav>
</header>
<main>{content}</main>
</body></html>"""


# ---------------- Pages ----------------

def render_home():
    db = _db()
    cases = db.fetchall("SELECT COUNT(*) AS n FROM cases")[0]["n"]
    assets = db.fetchall("SELECT COUNT(*) AS n FROM assets")[0]["n"]
    findings = db.fetchall("SELECT COUNT(*) AS n FROM findings")[0]["n"]
    evidence = db.fetchall("SELECT COUNT(*) AS n FROM evidence")[0]["n"]
    events = db.fetchall("SELECT COUNT(*) AS n FROM events")[0]["n"]

    domains = list_domains()
    tiles = "".join(
        f'<a class="tile" href="/workbench/{d["name"]}">'
        f'<h3>{d["name"]}</h3><p>{d["description"][:60]}</p></a>'
        for d in domains
    )

    return page(f"""
    <h2>Overview</h2>
    <div class="card">
      <div class="row" style="justify-content:space-around;">
        <div><div class="stat">{cases}</div><div class="stat-label">Cases</div></div>
        <div><div class="stat">{assets}</div><div class="stat-label">Assets</div></div>
        <div><div class="stat">{findings}</div><div class="stat-label">Findings</div></div>
        <div><div class="stat">{evidence}</div><div class="stat-label">Evidence</div></div>
        <div><div class="stat">{events}</div><div class="stat-label">Events</div></div>
      </div>
    </div>

    <h2>All Workbenches ({len(domains)})</h2>
    <div class="grid">{tiles}</div>
    """, active="/")


def render_cases():
    db = _db()
    rows = db.fetchall("SELECT * FROM cases ORDER BY id DESC LIMIT 100")
    trs = "".join(
        f'<tr><td>{r["id"]}</td><td>{r["name"]}</td>'
        f'<td>{r["status"]}</td><td>{r["created_at"][:19]}</td></tr>'
        for r in rows
    )
    return page(f"""
    <h2>Cases</h2>
    <div class="card">
      <form method="POST" action="/case-create" class="row">
        <input name="name" placeholder="Case name" required style="flex:1; min-width:300px;">
        <button class="btn" type="submit">Create Case</button>
      </form>
    </div>
    <div class="card">
      <table>
        <tr><th>ID</th><th>Name</th><th>Status</th><th>Created</th></tr>
        {trs or '<tr><td colspan="4">No cases yet.</td></tr>'}
      </table>
    </div>
    """, active="/cases")


def render_workbenches():
    domains = list_domains()
    tiles = "".join(
        f'<a class="tile" href="/workbench/{d["name"]}">'
        f'<h3>{d["name"]}</h3><p>{d["domain"]}</p></a>'
        for d in domains
    )
    return page(f"""
    <h2>Workbenches ({len(domains)} domains)</h2>
    <div class="grid">{tiles}</div>
    """, active="/workbenches")


def render_workbench(name):
    cls = get_workbench(name)
    if not cls:
        return page('<div class="card"><h2>Workbench not found</h2></div>')

    db = _db()
    cases = db.fetchall("SELECT id, name FROM cases ORDER BY id DESC")
    opts = "".join(f'<option value="{c["id"]}">{c["id"]}: {c["name"]}</option>'
                   for c in cases) or '<option value="">-- create a case first --</option>'

    # Domain-specific form fields
    extra = ""
    if name == "forensics":
        extra = '<input name="target" placeholder="/path/to/file" required style="flex:1;">'
    elif name == "credentials":
        extra = '<input name="target" placeholder="paste hash" required style="flex:1;">'
    elif name == "redteam":
        extra = '<input type="hidden" name="authorized" value="yes">'
        extra += '<input name="target" placeholder="note (optional)" style="flex:1;">'
    else:
        extra = '<input name="target" placeholder="target (IP, domain, URL, hash)" required style="flex:1;">'

    # Recent findings for this workbench's domain
    findings_rows = db.fetchall(
        "SELECT id, title, severity, risk_score FROM findings "
        "WHERE title LIKE ? OR details LIKE ? ORDER BY id DESC LIMIT 15",
        (f"%{name}%", f"%{name}%"),
    )
    trs = "".join(
        f'<tr><td>{r["id"]}</td><td>{r["title"]}</td>'
        f'<td><span class="badge {r["severity"]}">{r["severity"]}</span></td>'
        f'<td>{r["risk_score"]}</td></tr>'
        for r in findings_rows
    )

    return page(f"""
    <h2>{name}</h2>
    <div class="card">
      <p style="color:#8b949e;">{cls.description}</p>
      <form method="POST" action="/workbench-run/{name}" class="row">
        <select name="case_id" required>{opts}</select>
        {extra}
        <button class="btn" type="submit">Run</button>
      </form>
    </div>
    <div class="card">
      <h3 style="color:#8b949e; margin-top:0;">Recent Findings</h3>
      <table>
        <tr><th>ID</th><th>Title</th><th>Severity</th><th>Risk</th></tr>
        {trs or '<tr><td colspan="4">No findings yet.</td></tr>'}
      </table>
    </div>
    """, active="/workbenches")


def render_findings():
    db = _db()
    rows = db.fetchall(
        "SELECT f.*, c.name AS case_name FROM findings f "
        "LEFT JOIN cases c ON c.id=f.case_id ORDER BY f.risk_score DESC LIMIT 200"
    )
    trs = "".join(
        f'<tr><td>{r["id"]}</td><td>{r["case_name"] or "-"}</td>'
        f'<td>{r["title"]}</td>'
        f'<td><span class="badge {r["severity"]}">{r["severity"]}</span></td>'
        f'<td>{r["risk_score"]}</td></tr>'
        for r in rows
    )
    return page(f"""
    <h2>All Findings</h2>
    <div class="card">
      <table>
        <tr><th>ID</th><th>Case</th><th>Title</th><th>Severity</th><th>Risk</th></tr>
        {trs or '<tr><td colspan="5">No findings yet.</td></tr>'}
      </table>
    </div>
    """, active="/findings")


def render_assets():
    db = _db()
    rows = db.fetchall(
        "SELECT a.*, c.name AS case_name FROM assets a "
        "LEFT JOIN cases c ON c.id=a.case_id ORDER BY a.id DESC LIMIT 200"
    )
    trs = "".join(
        f'<tr><td>{r["id"]}</td><td>{r["case_name"] or "-"}</td>'
        f'<td>{r["type"]}</td><td>{r["identifier"]}</td></tr>'
        for r in rows
    )
    return page(f"""
    <h2>All Assets</h2>
    <div class="card">
      <table>
        <tr><th>ID</th><th>Case</th><th>Type</th><th>Identifier</th></tr>
        {trs or '<tr><td colspan="4">No assets yet.</td></tr>'}
      </table>
    </div>
    """, active="/assets")


def render_reports():
    db = _db()
    rows = db.fetchall("SELECT * FROM cases ORDER BY id DESC LIMIT 100")
    trs = "".join(
        f'<tr><td>{r["id"]}</td><td>{r["name"]}</td>'
        f'<td><a href="/report-md?case={r["id"]}" style="color:#58a6ff;">markdown</a> | '
        f'<a href="/report-json?case={r["id"]}" style="color:#58a6ff;">json</a> | '
        f'<a href="/report-html?case={r["id"]}" style="color:#58a6ff;">html</a></td></tr>'
        for r in rows
    )
    return page(f"""
    <h2>Reports</h2>
    <div class="card">
      <table>
        <tr><th>ID</th><th>Case</th><th>Export</th></tr>
        {trs or '<tr><td colspan="3">No cases yet.</td></tr>'}
      </table>
    </div>
    """, active="/reports")


def render_run_result(workbench_name, result_dict, error=None):
    if error:
        body = f'<div class="card"><h2 style="color:#da3633;">Error</h2><pre>{error}</pre></div>'
    else:
        body = f'<div class="card"><h2>{workbench_name} — Result</h2><pre>{json.dumps(result_dict, indent=2, default=str)}</pre></div>'
    body += f'<a href="/workbench/{workbench_name}" style="color:#58a6ff;">&larr; back to workbench</a>'
    return page(body, active="/workbenches")


# ---------------- HTTP Handler ----------------

class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass  # quiet

    def _send(self, body, status=200, content_type="text/html; charset=utf-8"):
        if isinstance(body, str):
            body = body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_form(self):
        length = int(self.headers.get("Content-Length", 0))
        if not length:
            return {}
        body = self.rfile.read(length).decode()
        return {k: v[0] for k, v in parse_qs(body).items()}

    def do_GET(self):
        u = urlparse(self.path)
        p = u.path
        try:
            if p == "/":
                return self._send(render_home())
            if p == "/cases":
                return self._send(render_cases())
            if p == "/workbenches":
                return self._send(render_workbenches())
            if p.startswith("/workbench/"):
                name = p.split("/")[-1]
                return self._send(render_workbench(name))
            if p == "/findings":
                return self._send(render_findings())
            if p == "/assets":
                return self._send(render_assets())
            if p == "/reports":
                return self._send(render_reports())
            if p == "/report-md":
                cid = int(parse_qs(u.query).get("case", [1])[0])
                return self._send(Reporter(_db()).to_markdown(cid),
                                  content_type="text/plain; charset=utf-8")
            if p == "/report-json":
                cid = int(parse_qs(u.query).get("case", [1])[0])
                return self._send(Reporter(_db()).to_json(cid),
                                  content_type="application/json")
            if p == "/report-html":
                cid = int(parse_qs(u.query).get("case", [1])[0])
                md = Reporter(_db()).to_markdown(cid)
                html = "<pre>" + md.replace("<", "&lt;") + "</pre>"
                return self._send(page(f'<div class="card"><h2>Report #{cid}</h2>{html}</div>'))
            return self._send(page('<div class="card"><h2>Not found</h2></div>'), 404)
        except Exception as e:
            tb = traceback.format_exc()
            return self._send(page(f'<div class="card"><h2>Server Error</h2><pre>{tb}</pre></div>'), 500)

    def do_POST(self):
        try:
            data = self._read_form()
            if self.path == "/case-create":
                CoreAPI(_db()).case_create({"name": data["name"]})
                self.send_response(303)
                self.send_header("Location", "/cases")
                self.end_headers()
                return

            if self.path.startswith("/workbench-run/"):
                name = self.path.split("/")[-1]
                cls = get_workbench(name)
                if not cls:
                    return self._send(render_run_result(name, None, "Workbench not found"))
                case_id = int(data.get("case_id") or 0)
                if not case_id:
                    return self._send(render_run_result(name, None, "No case selected."))
                target = data.get("target", "")
                opts = {"case_id": case_id}
                if data.get("authorized"):
                    opts["authorized"] = True
                db = _db()
                bus = EventBus(db=db)
                try:
                    wb = cls(db, bus)
                    res = wb.discover(target, opts)
                    return self._send(render_run_result(name, res.to_dict()))
                except Exception as e:
                    tb = traceback.format_exc()
                    return self._send(render_run_result(name, None, tb))

            return self._send("Not found", 404)
        except Exception as e:
            tb = traceback.format_exc()
            return self._send(f"<pre>{tb}</pre>", 500)


def serve():
    print(f"NyxOS Web Dashboard: http://localhost:{PORT}")
    print(f"Workbenches registered: {len(ALL)}")
    HTTPServer(("0.0.0.0", PORT), Handler).serve_forever()


if __name__ == "__main__":
    serve()
