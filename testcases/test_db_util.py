from utils.db_util import DBUtil


def test_query_database_version():
    with DBUtil() as db:
        result = db.query_one("SELECT VERSION() AS version")
        assert result is not None
        print("数据库版本：", result["version"])


def test_insert_and_query_user():
    with DBUtil() as db:
        db.execute(
            "INSERT INTO users (username, email) VALUES (%s, %s)",
            ("test_user_day34", "day34@test.com")
        )

        user = db.query_one(
            "SELECT * FROM users WHERE username = %s",
            ("test_user_day34",)
        )

        assert user is not None
        assert user["username"] == "test_user_day34"
        assert user["email"] == "day34@test.com"

        db.execute("DELETE FROM users WHERE username = %s", ("test_user_day34",))