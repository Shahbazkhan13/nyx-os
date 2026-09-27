"""NyxOS Web Dashboard — browser GUI served from WSL.

Run: python3 -m desktop.web.server
Open from Windows: http://localhost:8080
"""
import os, sys, json
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from core.database.db import Database
from core.events.bus import EventBus
from core.api.api import CoreAPI
from security.recon.recon_workbench import ReconWorkbench
from security.network.network_workbench import NetworkWorkbench
from security.credentials.credentials_workbench import CredentialsWorkbench
from reporting.reporter import Reporter


PORT = 8080


HTML = """<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>NyxOS</title>
<style>
body { font-family: monospace; background:#0d1117; color:#c9d1d9; margin:0; padding:20px; }
h1 { color:#58a6ff; }
.nav a { color:#58a6ff; margin-right:20px; text-decoration:none; }
.card { background:#161b22; border:1px solid #30363d; padding:15px; margin:10px 0; border-radius:6px; }
.btn { background:#238636; color:white; padding:6px 14px; border:none; border-radius:6px; cursor:pointer; }
input, select { background:#0d1117; color:#c9d1d9; border:1px solid #30363d; padding:6px; border-radius:4px; }
table { width:100%; border-collapse:collapse; }
th,td { text-align:left; padding:6px; border-bottom:1px solid #30363d; }
.badge { padding:2px 6px; border-radius:4px; font-size:11px; }
.critical{background:#7d0c0c;} .high{background:#a33;} .medium{background:#a70;}
.low{background:#365314;} .info{background:#1f4f8b;}
pre { background:#0d1117; padding:10px; border-radius:4px; overflow:auto; max-height:400px; }
</style></head><body>
<h1>&#x1F6E1;&#xFE0F; NyxOS</h1>
<div class="nav">
  <a href="/">Dashboard</a>
  <a href="/cases">Cases</a>
  <a href="/recon">Recon</a>
  <a href="/network">Network</a>
  <a href="/credentials">Credentials</a>
  <a href="/reports">Reports</a>
</div>
<hr style="border-color:#30363d;">
{content}
</body></html>"""


def _db():
    return Database()


def render_home():
    db = _db()
    cases = db.fetchall("SELECT COUNT(*) AS n FROM cases")[0]["n"]
    assets = db.fetchall("SELECT COUNT(*) AS n FROM assets")[0]["n"]
    findings = db.fetchall("SELECT COUNT(*) AS n FROM findings")[0]["n"]
    return HTML.replace("{content}", f"""
    <div class="card">
      <h2>Overview</h2>
      <p>Cases: <b>{cases}</b> &nbsp; Assets: <b>{assets}</b> &nbsp; Findings: <b>{findings}</b></p>
    </div>
    <div class="card">
      <h2>Quick Start</h2>
      <p>Create a case: <a href="/cases">/cases</a></p>
    </div>
    """)


def render_cases():
    db = _db()
    rows = db.fetchall("SELECT * FROM cases ORDER BY id DESC LIMIT 50")
    trs = "".join(f"<tr><td>{r['id']}</td><td>{r['name']}</td><td>{r['status']}</td></tr>" for r in rows)
    return HTML.replace("{content}", f"""
    <div class="card">
      <h2>Cases</h2>
      <form method="POST" action="/case-create">
        <input name="name" placeholder="Case name" required>
        <button class="btn" type="submit">Create</button>
      </form>
      <br>
      <table><tr><th>ID</th><th>Name</th><th>Status</th></tr>{trs}</table>
    </div>
    """)


def render_recon():
    db = _db()
    cases = db.fetchall("SELECT id, name FROM cases ORDER BY id DESC")
    opts = "".join(f'<option value="{c["id"]}">{c["id"]}: {c["name"]}</option>' for c in cases)
    return HTML.replace("{content}", f"""
    <div class="card">
      <h2>Recon Workbench</h2>
      <form method="POST" action="/recon-run">
        <select name="case_id">{opts}</select>
        <input name="target" placeholder="example.com" required>
        <button class="btn" type="submit">Run</button>
      </form>
    </div>
    """)


def render_network():
    db = _db()
    cases = db.fetchall("SELECT id, name FROM cases ORDER BY id DESC")
    opts = "".join(f'<option value="{c["id"]}">{c["id"]}: {c["name"]}</option>' for c in cases)
    return HTML.replace("{content}", f"""
    <div class="card">
      <h2>Network Workbench</h2>
      <form method="POST" action="/network-run">
        <select name="case_id">{opts}</select>
        <input name="target" placeholder="127.0.0.1" required>
        <button class="btn" type="submit">Scan</button>
      </form>
    </div>
    """)


def render_credentials():
    db = _db()
    cases = db.fetchall("SELECT id, name FROM cases ORDER BY id DESC")
    opts = "".join(f'<option value="{c["id"]}">{c["id"]}: {c["name"]}</option>' for c in cases)
    return HTML.replace("{content}", f"""
    <div class="card">
      <h2>Credentials Workbench</h2>
      <form method="POST" action="/credentials-run">
        <select name="case_id">{opts}</select>
        <input name="hash" placeholder="paste hash" required style="width:400px;">
        <button class="btn" type="submit">Analyze</button>
      </form>
    </div>
    """)


def render_reports():
    db = _db()
    rows = db.fetchall("SELECT * FROM cases ORDER BY id DESC LIMIT 50")
    trs = "".join(
        f'<tr><td>{r["id"]}</td><td>{r["name"]}</td>'
        f'<td><a href="/report-md?case={r["id"]}">markdown</a> | '
        f'<a href="/report-json?case={r["id"]}">json</a></td></tr>'
        for r in rows)
    return HTML.replace("{content}", f"""
    <div class="card">
      <h2>Reports</h2>
      <table><tr><th>ID</th><th>Name</th><th>Export</th></tr>{trs}</table>
    </div>
    """)


class Handler(BaseHTTPRequestHandler):
    def _send(self, body, status=200, content_type="text/html"):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body.encode())))
        self.end_headers()
        self.wfile.write(body.encode())

    def _read_form(self):
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length).decode()
        return {k: v[0] for k, v in parse_qs(body).items()}

    def do_GET(self):
        u = urlparse(self.path)
        if u.path == "/":
            return self._send(render_home())
        if u.path == "/cases":
            return self._send(render_cases())
        if u.path == "/recon":
            return self._send(render_recon())
        if u.path == "/network":
            return self._send(render_network())
        if u.path == "/credentials":
            return self._send(render_credentials())
        if u.path == "/reports":
            return self._send(render_reports())
        if u.path == "/report-md":
            qs = parse_qs(u.query)
            cid = int(qs.get("case", [1])[0])
            return self._send(Reporter(_db()).to_markdown(cid), content_type="text/plain")
        if u.path == "/report-json":
            qs = parse_qs(u.query)
            cid = int(qs.get("case", [1])[0])
            return self._send(Reporter(_db()).to_json(cid), content_type="application/json")
        return self._send("Not found", status=404)

    def do_POST(self):
        data = self._read_form()
        if self.path == "/case-create":
            CoreAPI(_db()).case_create({"name": data["name"]})
            return self._send(render_cases())
        if self.path == "/recon-run":
            db = _db()
            rb = ReconWorkbench(db, EventBus(db=db))
            try:
                res = rb.discover(data["target"], {"case_id": int(data["case_id"])})
                body = f"<div class='card'><h2>Recon: {data['target']}</h2><pre>{json.dumps(res.to_dict(), indent=2)}</pre><a href='/recon'>back</a></div>"
            except Exception as e:
                body = f"<div class='card'><h2>Error</h2><pre>{e}</pre><a href='/recon'>back</a></div>"
            return self._send(HTML.replace("{content}", body))
        if self.path == "/network-run":
            db = _db()
            wb = NetworkWorkbench(db, EventBus(db=db))
            try:
                res = wb.discover(data["target"], {"case_id": int(data["case_id"])})
                body = f"<div class='card'><h2>Network: {data['target']}</h2><pre>{json.dumps(res.to_dict(), indent=2)}</pre><a href='/network'>back</a></div>"
            except Exception as e:
                body = f"<div class='card'><h2>Error</h2><pre>{e}</pre><a href='/network'>back</a></div>"
            return self._send(HTML.replace("{content}", body))
        if self.path == "/credentials-run":
            db = _db()
            wb = CredentialsWorkbench(db, EventBus(db=db))
            res = wb.discover(data["hash"], {"case_id": int(data["case_id"])})
            body = f"<div class='card'><h2>Hash Analysis</h2><pre>{json.dumps(res.to_dict(), indent=2)}</pre><a href='/credentials'>back</a></div>"
            return self._send(HTML.replace("{content}", body))
        return self._send("Not found", status=404)


def serve():
    print(f"NyxOS web dashboard running at http://localhost:{PORT}")
    print("Open from Windows browser: http://localhost:8080")
    HTTPServer(("0.0.0.0", PORT), Handler).serve_forever()


if __name__ == "__main__":
    serve()
