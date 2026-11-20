import pytest
import requests

from apis.auth_api import AuthApi
from requests.exceptions import HTTPError

class TestAuth:

    def setup_class(self):
        self.api = AuthApi()

    @pytest.mark.smoke
    @pytest.mark.skip(reason="reqres.in 官方已废弃该登录接口，非代码问题")
    def test_login_success(self):
        """测试登录成功"""
        resp = self.api.login("sydney@fife.co", "pistol")
        assert resp.status_code == 200
        assert "token" in resp.json()
        # ... 后面的断言可以不管，因为已经被跳过了

    @pytest.mark.smoke
    # 这条好像不用了@pytest.mark.skip(reason="reqres.in 官方已废弃该登录接口，非代码问题")
    # @pytest.mark.rerun_failures(reruns=2, reruns_delay=1)
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
            # 抛出其他异常，让用例失败，触发重试
            pytest.fail(f"Unexpected exception: {type(e).__name__}: {e}")