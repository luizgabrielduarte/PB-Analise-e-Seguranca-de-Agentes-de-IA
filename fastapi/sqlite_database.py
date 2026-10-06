import sqlite3
from pathlib import Path

DATABASE_PATH = Path(__file__).resolve().parent / "database.db"

conn = sqlite3.connect(DATABASE_PATH)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    role TEXT NOT NULL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS predictions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    text TEXT NOT NULL,
    intent TEXT NOT NULL,
    owner_id INTEGER NOT NULL,
    FOREIGN KEY (owner_id) REFERENCES users(id)
)
""")

cursor.execute("""
INSERT OR IGNORE INTO users (id, username, password, role)
VALUES (1, 'admin', 'admin123', 'admin')
""")

cursor.execute("""
INSERT OR IGNORE INTO users (id, username, password, role)
VALUES (2, 'user', 'user123', 'user')
""")

cursor.execute("""
INSERT OR IGNORE INTO predictions (id, text, intent, owner_id)
VALUES (
    1,
    'Quero cancelar meu pedido',
    'cancellation_request',
    1
)
""")

cursor.execute("""
INSERT OR IGNORE INTO predictions (id, text, intent, owner_id)
VALUES (
    2,
    'Preciso de ajuda com meu produto',
    'technical_issue',
    2
)
""")

conn.commit()
conn.close()

print(f"Banco criado em: {DATABASE_PATH}")