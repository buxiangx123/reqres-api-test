import pytest
import requests

@pytest.fixture(scope="session")
def base_url():
    """
    全局共享的基础 URL
    """
    url = "https://reqres.in/api"
    print(f"\n[Fixture] 初始化 base_url: {url}")
    return url

@pytest.fixture(scope="session")
def auth_token(base_url):
    """
    全局共享的 Token
    因为参数里写了 base_url，Pytest 会自动把上面的 base_url 传给这里
    """
    # 1. 准备登录账号密码
    login_data = {
        "email":"eve.holt@reqres.in",
        "password":"cityslicka"
    }

    # 2. 发起登录请求
    response = requests.post(f"{base_url}/register", json=login_data)

    # 3. 从返回的 JSON 数据中提取 token
    token = response.json().get("token")
    print(f"\n[Fixture] 成功获取 Token: {token}")
    return token






