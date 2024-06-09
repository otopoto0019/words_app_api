import sqlite3

DATABASE = "app.sqlite"


def init_sqlite():
    create_table()


def create_table():
    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS user (id INTEGER PRIMARY KEY, uuid TEXT)")
    conn.commit()
    conn.close()


def insert_user(hashedUuid):
    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()
    cur.execute("INSERT INTO user (uuid) VALUES (?)", (hashedUuid,))
    conn.commit()
    conn.close()
    return


def getIdFromHashedUuid(hashedUuid):
    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()
    cur.execute("SELECT id FROM user WHERE uuid = ?", (hashedUuid,))
    result = cur.fetchall()
    conn.commit()
    conn.close()
    return result[0][0]
