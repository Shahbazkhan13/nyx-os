"""NyxOS Web Server — desktop environment + JSON APIs."""
import os, sys, json, traceback
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from core.database.db import Database
from core.events.bus import EventBus
from core.api.api import CoreAPI
from reporting.reporter import Reporter
from reporting.pdf_reporter import build_pdf_html
from ai.assistant.assistant import Assistant
from security.registry.all_workbenches import list_domains, get_workbench
from desktop.web.desktop import render_desktop


PORT = 8080


def _db():
    return Database()


def _json(obj):
    return json.dumps(obj, default=str).encode("utf-8")


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass

    def _send(self, body, status=200, content_type="text/html; charset=utf-8"):
        if isinstance(body, str):
            body = body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _json(self, obj, status=200):
        self._send(_json(obj), status, "application/json")

    def _read_json(self):
        length = int(self.headers.get("Content-Length", 0))
        if not length:
            return {}
        try:
            return json.loads(self.rfile.read(length).decode() or "{}")
        except Exception:
            return {}

    # ---------------- GET ----------------
    def do_GET(self):
        u = urlparse(self.path)
        p = u.path
        try:
            # Desktop
            if p == "/" or p == "/desktop":
                return self._send(render_desktop())

            # --- JSON APIs ---
            if p == "/api/cases":
                db = _db()
                rows = db.fetchall("SELECT * FROM cases ORDER BY id DESC LIMIT 200")
                return self._json({"cases": [dict(r) for r in rows]})

            if p == "/api/case":
                cid = int(parse_qs(u.query).get("id", [0])[0])
                if not cid:
                    return self._json({"error": "id required"}, 400)
                return self._json(CoreAPI(_db()).case_get({"id": cid}))

            if p == "/api/workbenches":
                return self._json({"workbenches": list_domains()})

            if p == "/api/findings":
                db = _db()
                rows = db.fetchall(
                    "SELECT f.*, c.name AS case_name FROM findings f "
                    "LEFT JOIN cases c ON c.id=f.case_id "
                    "ORDER BY f.risk_score DESC LIMIT 500")
                return self._json({"findings": [dict(r) for r in rows]})

            if p == "/api/assets":
                db = _db()
                rows = db.fetchall(
                    "SELECT a.*, c.name AS case_name FROM assets a "
                    "LEFT JOIN cases c ON c.id=a.case_id "
                    "ORDER BY a.id DESC LIMIT 500")
                return self._json({"assets": [dict(r) for r in rows]})

            if p == "/api/events":
                db = _db()
                rows = db.fetchall("SELECT * FROM events ORDER BY id DESC LIMIT 200")
                return self._json({"events": [dict(r) for r in rows]})

            if p == "/api/ai":
                q = parse_qs(u.query).get("q", [""])[0]
                return self._json(_ai_answer(q))

            if p == "/api/stats":
                db = _db()
                return self._json({
                    "cases": db.fetchall("SELECT COUNT(*) AS n FROM cases")[0]["n"],
                    "assets": db.fetchall("SELECT COUNT(*) AS n FROM assets")[0]["n"],
                    "findings": db.fetchall("SELECT COUNT(*) AS n FROM findings")[0]["n"],
                    "evidence": db.fetchall("SELECT COUNT(*) AS n FROM evidence")[0]["n"],
                    "events": db.fetchall("SELECT COUNT(*) AS n FROM events")[0]["n"],
                })

            # --- Report exports ---
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
                return self._send(build_pdf_html(_db(), cid))

            return self._send("Not found", 404)
        except Exception:
            tb = traceback.format_exc()
            return self._send(f"<pre>{tb}</pre>", 500)

    # ---------------- POST ----------------
    def do_POST(self):
        u = urlparse(self.path)
        p = u.path
        try:
            data = self._read_json()

            if p == "/api/case":
                name = (data.get("name") or "").strip()
                if not name:
                    return self._json({"error": "name required"}, 400)
                r = CoreAPI(_db()).case_create({"name": name})
                return self._json(r)

            if p.startswith("/api/workbench/"):
                name = p.split("/")[-1]
                cls = get_workbench(name)
                if not cls:
                    return self._json({"error": "workbench not found"}, 404)
                case_id = int(data.get("case_id") or 0)
                if not case_id:
                    return self._json({"error": "case_id required"}, 400)
                target = data.get("target", "")
                opts = {"case_id": case_id}
                if data.get("authorized"):
                    opts["authorized"] = True
                db = _db()
                bus = EventBus(db=db)
                try:
                    wb = cls(db, bus)
                    res = wb.discover(target, opts)
                    return self._json(res.to_dict())
                except Exception:
                    return self._json({"error": traceback.format_exc()}, 500)

            return self._send("Not found", 404)
        except Exception:
            tb = traceback.format_exc()
            return self._json({"error": tb}, 500)


def _ai_answer(q):
    a = Assistant()
    lq = (q or "").lower()
    for tool in ["nmap", "dig", "whois", "sqlmap", "hashcat", "nuclei",
                 "subfinder", "gobuster", "whatweb", "nikto"]:
        if tool in lq:
            return a.explain_tool(tool)
    if "next" in lq or "suggest" in lq:
        return a.suggest_next({"domain": "recon"})
    if "help" in lq or not lq:
        return {"hint": "Ask about a tool (nmap, sqlmap, nuclei, subfinder...), "
                        "or say 'next steps'."}
    return {"response": "Try: nmap / sqlmap / nuclei / next steps"}


def serve():
    print("=" * 60)
    print(f"  NyxOS Desktop  →  http://localhost:{PORT}")
    print(f"  Workbenches: {len(list_domains())}")
    print("=" * 60)
    HTTPServer(("0.0.0.0", PORT), Handler).serve_forever()


if __name__ == "__main__":
    serve()
