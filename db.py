import sqlite3
DB_FILE = "tasks.db"

SEED_TASKS=[
    ("Train", 0),
    ("Buy groceries", 0),
    ("Finish assignments", 1),
    #SQLite doesnt have True-False
]

def get_connection():
    conn = sqlite3.connect(DB_FILE)
    #creates tasks.db
    conn.row_factory=sqlite3.Row
    #gives rows back as plain tuples

    return conn

def init_db():
    conn = get_connection()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS tasks(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            -- title is the row index
            done BOOLEAN NOT NULL DEFAULT 0
        )
        """
    )
    row = conn.execute("SELECT COUNT(*) FROM tasks").fetchone()
    if row[0]==0:
        conn.executemany(
            "INSERT INTO tasks (title, done) VALUES (?, ?)", SEED_TASKS
        )
    conn.commit()
    conn.close()