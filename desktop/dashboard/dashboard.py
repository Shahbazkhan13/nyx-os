"""NyxOS Dashboard — overview of cases, assets, findings."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from core.database.db import Database


def render(db=None):
    db = db or Database()
    lines = []
    lines.append("=" * 60)
    lines.append("  NyxOS Dashboard")
    lines.append("=" * 60)

    cases = db.fetchall("SELECT COUNT(*) AS n FROM cases")[0]["n"]
    assets = db.fetchall("SELECT COUNT(*) AS n FROM assets")[0]["n"]
    findings = db.fetchall("SELECT COUNT(*) AS n FROM findings")[0]["n"]
    evidence = db.fetchall("SELECT COUNT(*) AS n FROM evidence")[0]["n"]
    events = db.fetchall("SELECT COUNT(*) AS n FROM events")[0]["n"]

    lines.append(f"  Cases:     {cases}")
    lines.append(f"  Assets:    {assets}")
    lines.append(f"  Findings:  {findings}")
    lines.append(f"  Evidence:  {evidence}")
    lines.append(f"  Events:    {events}")
    lines.append("=" * 60)

    recent = db.fetchall("SELECT id, name, status FROM cases ORDER BY id DESC LIMIT 5")
    if recent:
        lines.append("  Recent cases:")
        for r in recent:
            lines.append(f"    #{r['id']}  {r['name']}  [{r['status']}]")
        lines.append("=" * 60)

    return "\n".join(lines)


if __name__ == "__main__":
    print(render())
