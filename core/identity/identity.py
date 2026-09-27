"""NyxOS Identity — users, roles, permissions."""
ROLES = {
    "admin":   {"read", "write", "delete", "execute", "manage_users"},
    "analyst": {"read", "write", "execute"},
    "viewer":  {"read"},
}


class Identity:
    def __init__(self, db):
        self.db = db

    def create_user(self, username, role="analyst"):
        if role not in ROLES:
            raise ValueError(f"Unknown role: {role}")
        cur = self.db.execute(
            "INSERT INTO users(username, role) VALUES (?, ?)",
            (username, role),
        )
        return cur.lastrowid

    def get_user(self, username):
        row = self.db.fetchone("SELECT * FROM users WHERE username=?", (username,))
        return dict(row) if row else None

    def has_permission(self, username, permission):
        user = self.get_user(username)
        if not user:
            return False
        return permission in ROLES.get(user["role"], set())

    def list_users(self):
        return [dict(r) for r in self.db.fetchall("SELECT * FROM users")]
