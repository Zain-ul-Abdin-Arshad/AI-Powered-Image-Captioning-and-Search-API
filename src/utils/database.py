import sqlite3
import os

def connection():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    src_dir = os.path.dirname(current_dir)
    db_path = os.path.join(src_dir, 'images.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def initialize_db():
    conn = connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS images (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            caption TEXT NOT NULL,
            embedding BLOB NOT NULL
        )
    """)
    columns = [row[1] for row in cursor.execute("PRAGMA table_info(images)").fetchall()]
    if 'caption' not in columns:
        cursor.execute("ALTER TABLE images ADD COLUMN caption TEXT NOT NULL DEFAULT ''")
    if 'embedding' not in columns:
        cursor.execute("ALTER TABLE images ADD COLUMN embedding BLOB NOT NULL DEFAULT ''")
    conn.commit()
    conn.close()
