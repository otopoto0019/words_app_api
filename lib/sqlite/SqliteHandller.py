import sqlite3

DATABASE = "app.sqlite"


def init_sqlite():
    create_tables()


def create_tables():
    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()
    cur.execute(
        "CREATE TABLE IF NOT EXISTS user ("
        "id INTEGER PRIMARY KEY,"
        "uuid TEXT NOT NULL,"
        "key TEXT NOT NULL,"
        "created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
        ")"
    )
    cur.execute(
        "CREATE TABLE IF NOT EXISTS usage ("
        "id INTEGER PRIMARY KEY,"
        "user_id INTEGER,"
        "usage_count INTEGER DEFAULT 0,"
        "last_used_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,"
        "FOREIGN KEY (user_id) REFERENCES user (id)"
        ")"
    )
    conn.commit()
    conn.close()


def insert_user(uuid, hashed_key):
    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()
    cur.execute("INSERT INTO user (uuid, key) VALUES (?, ?)", (uuid, hashed_key))
    conn.commit()
    conn.close()
    return


def getIdFromUUID(uuid):
    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()
    cur.execute("SELECT id FROM user WHERE uuid = ?", (uuid,))
    result = cur.fetchall()
    conn.close()
    return result[0][0]


def isExistedUUID(uuid):
    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()
    cur.execute("SELECT * FROM user WHERE uuid = ?", (uuid,))
    result = cur.fetchall()

    return len(result) > 0

