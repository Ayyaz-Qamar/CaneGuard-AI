import sqlite3, hashlib, os
from flask_login import UserMixin
from app import login_manager

DB_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "history_db", "sugarcane.db"
)


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = get_db()
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        full_name TEXT,
        profile_pic TEXT,
        created_at TEXT DEFAULT (datetime('now'))
    )""")
    try:
        c.execute("ALTER TABLE users ADD COLUMN profile_pic TEXT")
    except Exception:
        pass
    c.execute("""CREATE TABLE IF NOT EXISTS scans (
        id           INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id      INTEGER,
        scan_date    TEXT DEFAULT (datetime('now')),
        image_path   TEXT,
        input_type   TEXT,
        disease_name TEXT,
        confidence   REAL,
        damage_pct   REAL,
        severity     TEXT,
        weather_risk TEXT,
        city         TEXT,
        pdf_path     TEXT,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )""")
    conn.commit()
    conn.close()


def _hash(pw):
    return hashlib.sha256(pw.encode()).hexdigest()


class User(UserMixin):
    def __init__(self, id, username, full_name, profile_pic=None):
        self.id          = id
        self.username    = username
        self.full_name   = full_name
        self.profile_pic = profile_pic


def _row_to_user(row):
    if not row:
        return None
    pic = None
    try:
        pic = row["profile_pic"]
    except Exception:
        pic = None
    return User(row["id"], row["username"], row["full_name"], pic)


@login_manager.user_loader
def load_user(user_id):
    init_db()
    conn = get_db()
    row  = conn.execute("SELECT * FROM users WHERE id=?", (user_id,)).fetchone()
    conn.close()
    return _row_to_user(row)


def register_user(username, password, full_name):
    init_db()
    conn = get_db()
    try:
        conn.execute(
            "INSERT INTO users (username, password, full_name) VALUES (?,?,?)",
            (username.strip(), _hash(password), full_name.strip())
        )
        conn.commit()
        conn.close()
        return {"success": True}
    except sqlite3.IntegrityError:
        conn.close()
        return {"success": False, "error": "user_exists"}


def verify_user(username, password):
    init_db()
    conn = get_db()
    row  = conn.execute(
        "SELECT * FROM users WHERE username=? AND password=?",
        (username.strip(), _hash(password))
    ).fetchone()
    conn.close()
    return _row_to_user(row)


def update_profile_pic(user_id, pic_path):
    init_db()
    conn = get_db()
    conn.execute("UPDATE users SET profile_pic=? WHERE id=?", (pic_path, user_id))
    conn.commit()
    conn.close()


def save_scan(user_id, image_path, input_type, disease_name,
              confidence, damage_pct, severity,
              weather_risk="", city="", pdf_path=""):
    init_db()
    conn = get_db()
    cur  = conn.execute("""
        INSERT INTO scans
        (user_id,image_path,input_type,disease_name,confidence,
         damage_pct,severity,weather_risk,city,pdf_path)
        VALUES (?,?,?,?,?,?,?,?,?,?)
    """, (user_id, image_path, input_type, disease_name,
          confidence, damage_pct, severity, weather_risk, city, pdf_path))
    conn.commit()
    scan_id = cur.lastrowid
    conn.close()
    return scan_id


def get_scans(user_id):
    init_db()
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM scans WHERE user_id=? ORDER BY scan_date DESC", (user_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def delete_scan_db(scan_id, user_id):
    init_db()
    conn = get_db()
    conn.execute("DELETE FROM scans WHERE id=? AND user_id=?", (scan_id, user_id))
    conn.commit()
    conn.close()


def get_stats(user_id):
    init_db()
    conn       = get_db()
    total      = conn.execute("SELECT COUNT(*) FROM scans WHERE user_id=?", (user_id,)).fetchone()[0]
    by_disease = conn.execute("""
        SELECT disease_name, COUNT(*) as cnt FROM scans
        WHERE user_id=? GROUP BY disease_name ORDER BY cnt DESC
    """, (user_id,)).fetchall()
    avg_row    = conn.execute(
        "SELECT AVG(damage_pct) FROM scans WHERE user_id=?", (user_id,)
    ).fetchone()[0]
    conn.close()
    return {
        "total_scans": total,
        "by_disease":  [dict(r) for r in by_disease],
        "avg_damage":  round(avg_row or 0, 1),
    }


def update_scan_pdf(scan_id, pdf_path):
    init_db()
    conn = get_db()
    conn.execute("UPDATE scans SET pdf_path=? WHERE id=?", (pdf_path, scan_id))
    conn.commit()
    conn.close()


def reset_user_data(user_id):
    init_db()
    conn = get_db()
    conn.execute("DELETE FROM scans WHERE user_id=?", (user_id,))
    conn.commit()
    conn.close()