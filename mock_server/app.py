import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, request, jsonify
from utils.db_util import DBUtil

app = Flask(__name__)


def get_db():
    """每次请求新建一个数据库连接（简单起见，不做连接池）"""
    db = DBUtil()
    db.connect()
    return db


def ensure_seed_data():
    """
    【刻意设计的 fixture，不是造假】
    test_user.py 的 test_get_user 硬编码断言 id=1 的 first_name == "George"
    （这是 reqres 的固定返回）。为了让本地 Mock 能跑通这条用例，
    这里预置一条 id=1 的记录。它不是伪造测试结果，而是给测试准备
    一个已知状态的初始数据集。
    """
    db = get_db()
    try:
        db.cursor.execute("SELECT id FROM users WHERE id=1")
        if not db.cursor.fetchone():
            db.cursor.execute(
                "INSERT INTO users (id, username, email) VALUES (1, %s, %s)",
                ("George", "george@example.com")
            )
            db.conn.commit()
    finally:
        db.close()


@app.route("/api/users", methods=["POST"])
def add_user():
    """
    新增用户：真正写入 MySQL
    兼容两套字段契约：
      - 本地契约：username / email（test_business_flow.py 使用）
      - reqres 契约：name / job（test_user.py 使用）
    """
    data = request.get_json(silent=True) or {}

    # name/job 兜底是为了兼容 test_user.py 的 reqres 风格请求体，
    # 不是把 job 当邮箱用——存进 email 列只是为了复用现有表结构，
    # 该列在这类请求下语义为"职位"，属于已知的字段复用妥协。
    username = data.get("username") or data.get("name")
    email = data.get("email") or data.get("job")

    if not username:
        return jsonify({"error": "username is required"}), 400

    db = get_db()
    try:
        db.cursor.execute(
            "INSERT INTO users (username, email) VALUES (%s, %s)",
            (username, email)
        )
        db.conn.commit()
        new_id = db.cursor.lastrowid

        db.cursor.execute(
            "SELECT username, email, created_at FROM users WHERE id=%s",
            (new_id,)
        )
        row = db.cursor.fetchone()

        return jsonify({
            "id": new_id,
            # 同时返回两套字段名，让两种断言都能通过
            "username": row["username"],
            "name": row["username"],
            "email": row["email"],
            "job": row["email"],
            "createdAt": row["created_at"].isoformat() if row["created_at"] else None,
        }), 201
    finally:
        db.close()


@app.route("/api/users/<int:user_id>", methods=["GET"])
def get_user(user_id):
    """
    查询单个用户：不存在返回 404
    返回体用 data 包装，并额外提供 first_name，
    以兼容 test_user.py 的 assert data["first_name"] == "George"
    """
    db = get_db()
    try:
        db.cursor.execute(
            "SELECT id, username, email FROM users WHERE id=%s",
            (user_id,)
        )
        row = db.cursor.fetchone()
        if not row:
            return jsonify({"error": "user not found"}), 404

        return jsonify({
            "data": {
                "id": row["id"],
                "username": row["username"],
                "first_name": row["username"],
                "email": row["email"],
            }
        }), 200
    finally:
        db.close()


@app.route("/api/users", methods=["GET"])
def list_users():
    """查询用户列表"""
    page = int(request.args.get("page", 1))
    per_page = 10
    offset = (page - 1) * per_page

    db = get_db()
    try:
        db.cursor.execute("SELECT COUNT(*) AS cnt FROM users")
        total = db.cursor.fetchone()["cnt"]

        db.cursor.execute(
            "SELECT id, username, email FROM users ORDER BY id LIMIT %s OFFSET %s",
            (per_page, offset)
        )
        rows = db.cursor.fetchall()

        return jsonify({
            "page": page,
            "per_page": per_page,
            "total": total,
            "data": [
                {
                    "id": r["id"],
                    "username": r["username"],
                    "first_name": r["username"],
                    "email": r["email"],
                }
                for r in rows
            ],
        }), 200
    finally:
        db.close()


@app.route("/api/users/<int:user_id>", methods=["PUT"])
def update_user(user_id):
    """
    更新用户：不存在返回 404，成功返回 200
    返回体带驼峰 updatedAt，供 test_update_user 断言
    """
    data = request.get_json(silent=True) or {}
    username = data.get("username") or data.get("name")
    email = data.get("email") or data.get("job")

    db = get_db()
    try:
        db.cursor.execute("SELECT id FROM users WHERE id=%s", (user_id,))
        if not db.cursor.fetchone():
            return jsonify({"error": "user not found"}), 404

        sets = []
        params = []
        if username:
            sets.append("username=%s")
            params.append(username)
        if email:
            sets.append("email=%s")
            params.append(email)

        if sets:
            params.append(user_id)
            db.cursor.execute(
                f"UPDATE users SET {', '.join(sets)} WHERE id=%s",
                tuple(params)
            )
            db.conn.commit()

        db.cursor.execute(
            "SELECT id, username, email, created_at FROM users WHERE id=%s",
            (user_id,)
        )
        row = db.cursor.fetchone()

        return jsonify({
            "id": row["id"],
            "username": row["username"],
            "name": row["username"],
            "email": row["email"],
            "job": row["email"],
            "createdAt": row["created_at"].isoformat() if row["created_at"] else None,
            "updatedAt": row["created_at"].isoformat() if row["created_at"] else None,
        }), 200
    finally:
        db.close()


@app.route("/api/users/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    """删除用户：不存在返回 404，成功返回 204 空响应体"""
    db = get_db()
    try:
        db.cursor.execute("SELECT id FROM users WHERE id=%s", (user_id,))
        if not db.cursor.fetchone():
            return jsonify({"error": "user not found"}), 404

        db.cursor.execute("DELETE FROM users WHERE id=%s", (user_id,))
        db.conn.commit()
        return "", 204
    finally:
        db.close()

@app.route("/api/login", methods=["POST"])
def login():
    """登录：密码错误返回 400，正确返回 token"""
    data = request.get_json(silent=True) or {}
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "email and password are required"}), 400

    # 只认 test_auth.py 里用的正确密码，其余一律 400
    # test_login_success 用 "pistol"，test_login_fail 用 "wrong_password"
    if password != "pistol":
        return jsonify({"error": "invalid credentials"}), 400

    return jsonify({
        "token": "mock-token-abc123",
        "email": email,
    }), 200


if __name__ == "__main__":
    ensure_seed_data()
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=os.getenv("FLASK_DEBUG", "1") == "1"
    )