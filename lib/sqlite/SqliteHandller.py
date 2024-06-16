import random
import sqlite3
import string

from flask_argon2 import Argon2

DATABASE: str = "app.sqlite"


def generate_api_key():
    return "".join(random.choices(string.ascii_letters + string.digits, k=64))


def init_sqlite(argon2: Argon2):
    create_tables()
    add_admin(argon2)


def add_admin(argon2: Argon2):
    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()
    cur.execute("SELECT * FROM user WHERE uuid = ?", ("admin",))
    result = cur.fetchall()
    if not result:
        api_key = generate_api_key()
        hashed_api_key = argon2.generate_password_hash(api_key)
        cur.execute("INSERT INTO user(uuid, api_key, is_admin) VALUES(?, ?, ?)", ("admin", hashed_api_key, True))
        conn.commit()
        print(api_key)
    conn.close()
    return


def create_tables():
    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()
    cur.execute(
        "CREATE TABLE IF NOT EXISTS user ("
        "id INTEGER PRIMARY KEY,"
        "uuid TEXT NOT NULL,"
        "api_key TEXT NOT NULL,"
        "is_admin BOOLEAN DEFAULT FALSE,"
        "created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
        ")"
    )
    cur.execute(
        "CREATE TABLE IF NOT EXISTS usage ("
        "id INTEGER PRIMARY KEY,"
        "user_id INTEGER,"
        "response TEXT,"
        "used_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,"
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


def insert_usage(response, api_key, argon2: Argon2):
    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()
    user_id = get_user_id_from_api_key(api_key, argon2)
    cur.execute("INSERT INTO usage (user_id, response) VALUES (?, ?)", (user_id, response))
    conn.commit()
    conn.close()
    return


def get_user_id_from_api_key(api_key, argon2: Argon2):
    if not is_valid_api_key(api_key, argon2):
        return -1

    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()
    cur.execute("SELECT * FROM user")
    result = cur.fetchall()

    for user in result:
        if argon2.check_password_hash(user[2], api_key):
            return user[0]


def is_existed_uuid(uuid):
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


def get_usages(api_key, argon2: Argon2):
    result = []
    user_id = get_user_id_from_api_key(api_key, argon2)
    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()
    cur.execute("SELECT * FROM usage WHERE user_id = ?", (user_id, ))
    usages_result = cur.fetchall()
    for usage in usages_result:
        result.append(usage)

    return result


def is_admin(api_key, argon2: Argon2):
    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()
    user_id = get_user_id_from_api_key(api_key, argon2)
    cur.execute("SELECT is_admin FROM user WHERE id = ?", (user_id,))
    result = cur.fetchall()
    conn.close()
    return len(result) == 1
