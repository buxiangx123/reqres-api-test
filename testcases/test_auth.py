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
        """测试登录失败 (期望得到 400 错误)"""
        try:
            self.api.login("sydney@fife.co", "wrong_password")
            # 如果未抛出异常，说明登录成功（不符合预期），抛出AssertionError
            pytest.fail("Expected HTTPError but no exception was raised")
        except requests.exceptions.HTTPError as e:
            # 验证异常信息包含'400'
            assert '400' in str(e), f"Expected '400' in error message, got: {e}"
        except Exception as e:
            # 其他异常视为用例失败
            pytest.fail(f"Unexpected exception: {type(e).__name__}: {e}")