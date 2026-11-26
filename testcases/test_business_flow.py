import pytest
import allure
from apis.user_api import UserApi
from utils.db_util import DBUtil
from utils.logger import logger  # 引入 Loguru 的 logger 对象

@allure.feature("用户管理")
class TestBusinessFlow:
    """业务闭环实战：参数化与数据驱动"""

    # 1. 准备多组测试数据（一组数据就是一个测试用例）
    test_data = [
        {"username": "user_001", "email": "user001@test.com"},
        {"username": "user_002", "email": "user002@test.com"},
        {"username": "admin_test", "email": "admin@test.com"}
    ]

    # 2. 使用 pytest.mark.parametrize 装饰器，把数据"喂"给测试方法
    @allure.story("新增用户")
    @allure.title("新增用户并校验返回数据")
    @pytest.mark.parametrize("data", test_data)
    def test_add_user_and_verify_db(self, data):
        """
        测试新增用户，并联合校验返回数据与数据库落库结果
        """
        # 1. 从参数 data 里取出用户名和邮箱
        test_username = data["username"]
        test_email = data["email"]

        logger.info(f"开始执行业务闭环测试，准备注册用户：{test_username}")

        # 2. 接口动作：调用接口新增用户
        api = UserApi()
        response = api.add_user(username=test_username, email=test_email)

        # 3. 接口返回校验（兼容 200 和 201 成功状态）
        assert response.status_code in (200, 201)

        # 4. 接口回显校验：验证接口返回的数据和发送的数据完全一致
        resp_json = response.json()
        assert resp_json.get("username") == test_username, f"用户名校验失败，期望 {test_username}"
        assert resp_json.get("email") == test_email, f"邮箱校验失败，期望 {test_email}"

        # 5. 【核心】真正查库验证：确认数据已落库，而不只是接口回显
        created_id = resp_json.get("id")
        assert created_id is not None, "接口未返回 id，无法进行数据库校验"

        db = DBUtil()
        db.connect()
        try:
            db.cursor.execute(
                "SELECT username, email FROM users WHERE id=%s",
                (created_id,)
            )
            row = db.cursor.fetchone()

            assert row is not None, f"数据库查不到 id={created_id} 的记录，数据未真正落库"
            assert row["username"] == test_username, f"库中用户名不一致：实际 {row['username']}"
            assert row["email"] == test_email, f"库中邮箱不一致：实际 {row['email']}"

            logger.info(f"数据库校验通过：id={created_id} 已落库")
        finally:
            # 6. 清理测试数据，避免污染后续测试
            db.cursor.execute("DELETE FROM users WHERE id=%s", (created_id,))
            db.conn.commit()
            db.close()

        print(f"\n[数据驱动成功] 用户：{test_username} 注册成功！")