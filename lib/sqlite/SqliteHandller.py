import sqlite3
import trace

from flask_argon2 import Argon2

DATABASE: str = "app.sqlite"


def init_sqlite():
    create_tables()


def create_tables():
    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()
    cur.execute(
        "CREATE TABLE IF NOT EXISTS user ("
        "id INTEGER PRIMARY KEY,"
        "uuid TEXT NOT NULL,"
        "api_key TEXT NOT NULL,"
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


def insert_user(uuid, api_key):
    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()
    cur.execute("INSERT INTO user (uuid, api_key) VALUES (?, ?)", (uuid, api_key))
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


def is_valid_api_key(api_key, argon2: Argon2):
    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()
    cur.execute("SELECT api_key FROM user")

    result = cur.fetchall()

    for hashed_api_key in result:
        if argon2.check_password_hash(hashed_api_key[0], api_key):
            return True

    conn.close()
    return False
