import random

import openai
from flask import Flask, request, jsonify
from flask_argon2 import Argon2
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity

from lib.sqlite.SqliteHandller import init_sqlite, insert_user, getIdFromHashedUuid

app = Flask(__name__)
argon2 = Argon2(app)

app.config["JWT_SECRET_KEY"] = "".join(random.choice("0123456789abcdefghijklmnopqrstuvwxyz") for _ in range(16))
jwt = JWTManager(app)


@app.route('/')
def hello_world():
    return "hello world!"


@app.route("/register", methods=["post"])
def register():
    data = request.get_data()
    uuid = data.decode("utf8")
    hashed_uuid = argon2.generate_password_hash(uuid)
    insert_user(hashed_uuid)
    id = getIdFromHashedUuid(hashed_uuid)
    access_token = create_access_token(identity=id)
    return jsonify(access_token=access_token)


@app.route("/generate_response", methods=["POST"])
@jwt_required()
def generate_response():
    data = request.json
    prompt = data.get("prompt", "")

    response = openai.OpenAI().chat.completions.create(
        model="gpt-3.5-turbo-instruct",
        prompt=prompt,
        max_tokens=50,
        temperature=0.5
    )

    return jsonify({"response": response.choices[0].message})


@app.before_request
def init():
    init_sqlite()


if __name__ == '__main__':
    app.run()
