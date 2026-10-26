#测试参数化
import pytest
import requests

@pytest.fixture(scope="session")
def base_url():
    return "https://reqres.in/api"

@pytest.mark.parametrize("email, password, expect_code, expect_token", [
    ("eve.holt@reqres.in", "cityslicka", 200, True),   # 正常登录，应该有 token
    ("eve.holt@reqres.in", "", 400, False),             # 密码为空，应该没有 token
    ("", "cityslicka", 400, False),                     # 邮箱为空，应该没有 token
    ("notexist@test.com", "123456", 400, False),        # 账号不存在，应该没有 token
])
def test_register_with_body(base_url, email, password, expect_code, expect_token):
    """
    测试注册/登录接口，同时验证状态码和响应体
    expect_token: True 表示期望返回中包含 token，False 表示期望不包含
    """
    payload = {
        "email": email,
        "password": password
    }

    response = requests.post(f"{base_url}/register", json=payload)
    data = response.json()

    # 1. 断言状态码
    assert response.status_code == expect_code, f"状态码不对，期望 {expect_code}，实际 {response.status_code}"

    # 2. 断言响应体内容
    if expect_token:
        # 成功时，响应体里应该有 token 字段，且不为空
        assert "token" in data, "响应体中缺少 token 字段"
        assert data["token"], "token 字段为空"
        assert isinstance(data["token"], str), "token 应该是字符串类型"
        print(f"\n✅ 登录成功，Token: {data['token']}")
    else:
        # 失败时，响应体里应该有 error 字段（reqres 接口会返回错误信息）
        assert "error" in data, "失败时响应体中缺少 error 字段"
        print(f"\n⚠️  登录失败，错误信息: {data['error']}")