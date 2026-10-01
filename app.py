"""Recipe Box API — BE104 course skeleton.

A working Flask + SQLite CRUD API for recipes. It stores data perfectly —
and it trusts everyone. There is no authentication and no authorization yet.
That is the point: you will add both, lesson by lesson, in Units 2 and 3.
"""

import sqlite3
from flask import Flask, request, jsonify, g
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

DATABASE = "recipes.db"  # change if your DB file has a different name


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(exception):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def user_to_dict(row):
    return {
        "id": row["id"],
        "username": row["username"],
        "email": row["email"],
    }


@app.post("/users")
def register_user():
    data = request.get_json(silent=True)

    # 1. Validate input
    if (
        not data
        or not data.get("username")
        or not data.get("email")
        or not data.get("password")
    ):
        return jsonify({"error": "username, email, and password are required"}), 400

    # 2. Hash the password
    password_hash = generate_password_hash(
        data["password"],
        method="pbkdf2:sha256",
    )

    db = get_db()

    try:
        # 3. Insert user with hash ONLY
        cur = db.execute(
            """
            INSERT INTO users (username, email, password_hash)
            VALUES (?, ?, ?)
            """,
            (data["username"], data["email"], password_hash),
        )
        db.commit()
    except sqlite3.IntegrityError:
        # 4. Duplicate username or email → 409
        return jsonify({"error": "username or email already in use"}), 409

    # 5. Fetch created user and return safe JSON
    row = db.execute(
        "SELECT id, username, email FROM users WHERE id = ?", (cur.lastrowid,)
    ).fetchone()

    return jsonify(user_to_dict(row)), 201


@app.post("/login")
def login():
    data = request.get_json(silent=True)

    # 1. Validate input
    if (
        not data
        or not data.get("username")
        or not data.get("password")
    ):
        return jsonify({"error": "username and password are required"}), 400

    db = get_db()

    # 2. Look up user by username (parameterized)
    row = db.execute(
        """
        SELECT id, username, email, password_hash
        FROM users
        WHERE username = ?
        """,
        (data["username"],),
    ).fetchone()

    # Prepare a single generic failure response
    generic_error = jsonify({"error": "Invalid username or password"}), 401

    # 3. If no such user, fail generically
    if row is None:
        return generic_error

    # 4. Verify password against stored hash
    if not check_password_hash(row["password_hash"], data["password"]):
        return generic_error

    # 5. On success, return safe identity (no password_hash)
    user = {
        "id": row["id"],
        "username": row["username"],
        "email": row["email"],
    }

    return jsonify(user), 200


if __name__ == "__main__":
    app.run(debug=True)

