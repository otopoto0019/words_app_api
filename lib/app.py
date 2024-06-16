import random
import string
from datetime import datetime, timedelta

import openai
from flask import Flask, request, jsonify
from flask_argon2 import Argon2
from flask_cors import CORS

from lib.constants import UPPER_LIMIT, OPENAI_API_KEY, MODEL_NAME, MAX_TOKEN, TEMPERATURE, EXCEPTION_MESSAGE, \
    API_KEY_HEADER_NAME
from lib.sqlite.SqliteHandller import init_sqlite, insert_user, is_existed_uuid, is_valid_api_key, \
    insert_usage, get_usages

app = Flask(__name__)
argon2 = Argon2(app)
CORS(app)

app.config["JWT_SECRET_KEY"] = "".join(random.choice("0123456789abcdefghijklmnopqrstuvwxyz") for _ in range(64))
openai_client = openai.OpenAI(api_key=OPENAI_API_KEY)


def generate_api_key():
    return "".join(random.choices(string.ascii_letters + string.digits, k=64))


def require_api_key(func):
    def wrapper(*args, **kwargs):
        api_key = request.headers.get(API_KEY_HEADER_NAME)
        if not api_key or not is_valid_api_key(api_key, argon2) or is_over_limit(api_key):
            return jsonify({"status": "error", "message": "this api key is empty or invalid or over limit"}), 401
        return func(*args, **kwargs)

    return wrapper


def is_over_limit(api_key):
    counts = 0
    current_timestamp = datetime.now()
    usages = get_usages(api_key, argon2)
    for usage in usages:
        timestamp = datetime.strptime(usage[3], "%Y-%m-%d %H:%M:%S")
        counts += (current_timestamp - timestamp < timedelta(hours=24))

    print(counts)
    return counts >= UPPER_LIMIT


@app.route("/register", methods=["post"])
def register():
    data = request.get_json()
    uuid = data["uuid"]

    if is_existed_uuid(uuid):
        return jsonify({"status": "error", "message": "this uuid has already registered"}), 400

    api_key = generate_api_key()
    hashed_api_key = argon2.generate_password_hash(api_key)
    insert_user(uuid, hashed_api_key)
    return jsonify({"status": "success", "api_key": api_key}), 201


@app.route("/generate_response", methods=["POST"])
@require_api_key
def generate_response():
    data = request.json
    prompt = data.get("prompt", "")

    if prompt == "":
        return jsonify({"status": "error", "message": "prompt should not be empty"}), 400

    try:
        response = openai_client.completions.create(
            model=MODEL_NAME,
            prompt=prompt,
            max_tokens=MAX_TOKEN,
            temperature=TEMPERATURE
        )
        response_text = response.choices[0].text.replace("\n", "")
        insert_usage(response_text, request.headers.get(API_KEY_HEADER_NAME), argon2)
        return jsonify({"status": "success", "text": response_text}), 201

    except:
        return jsonify({"status": "error", "message": EXCEPTION_MESSAGE}), 400


@app.before_request
def init():
    init_sqlite()


if __name__ == "__main__":
    app.run()
