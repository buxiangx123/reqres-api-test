import pytest
import requests

from apis.auth_api import AuthApi
from requests.exceptions import HTTPError

class TestAuth:

    def setup_class(self):
        self.api = AuthApi()

    @pytest.mark.smoke
    def test_login_success(self):
        """测试登录成功"""
        resp = self.api.login("sydney@fife.co", "pistol")
        assert resp.status_code == 200
        assert "token" in resp.json()

    @pytest.mark.smoke
    def test_login_fail(self):
        """异常场景：密码错误应返回 400"""
        resp = self.api.login(email="morpheus@matrix.com", password="wrong_password")

        assert resp.status_code == 400, f"密码错误应返回 400，实际：{resp.status_code}"

        print("异常场景校验通过：密码错误返回 400")


    def test_login_missing_password(self):
        """异常场景：登录缺少 password 应返回 400"""
        # 只传 email 不传 password，触发 app.py 第 227 行
        resp = self.api.login(email="morpheus@matrix.com")

        assert resp.status_code == 400, f"缺少 password 应返回 400，实际：{resp.status_code}"

        print("异常场景校验通过：登录缺 password 返回 400")

    def test_login_missing_email(self):
        """异常场景：登录缺少 email 应返回 400"""
        # 只传 password 不传 email
        resp = self.api.login(password="pistol")

        assert resp.status_code == 400, f"缺少 email 应返回 400，实际：{resp.status_code}"

        print("异常场景校验通过：登录缺 email 返回 400")