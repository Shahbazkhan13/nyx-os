"""Timeline renderer for events."""


def render_events(db, limit=100):
    rows = db.fetchall(
        "SELECT * FROM events ORDER BY id DESC LIMIT ?", (limit,))
    items = []
    for r in rows:
        items.append(
            f'<tr><td>{r["id"]}</td><td>{r["created_at"][:19]}</td>'
            f'<td><code>{r["topic"]}</code></td>'
            f'<td><code>{r["payload"][:120]}</code></td></tr>')
    body = "".join(items) or '<tr><td colspan="4">No events yet.</td></tr>'
    return f"""
    <div class="card">
      <h2>Event Timeline</h2>
      <table>
        <tr><th>ID</th><th>Time</th><th>Topic</th><th>Payload</th></tr>
        {body}
      </table>
    </div>
    """
