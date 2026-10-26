#测试allure
import pytest
import requests
import allure

@pytest.fixture(scope="session")
def base_url():
    return "https://reqres.in/api"

@allure.feature("用户管理")
@allure.story("查询用户列表")
@allure.title("查询第{page}页用户")
@pytest.mark.parametrize("page", [1, 2, 3])
@pytest.mark.smoke
def test_get_users(base_url, page):
    """查询用户列表接口"""
    response = requests.get(f"{base_url}/users", params={"page": page})
    assert response.status_code == 200
    data = response.json()
    assert data["page"] == page

@allure.feature("用户管理")
@allure.story("用户注册")
@allure.title("注册接口-正常场景")
@pytest.mark.regression
def test_register_success(base_url):
    """使用正确的邮箱和密码进行注册"""
    payload = {
        "email": "eve.holt@reqres.in",
        "password": "cityslicka"
    }
    response = requests.post(f"{base_url}/register", json=payload)
    assert response.status_code == 200
    assert "token" in response.json()

@allure.feature("用户管理")
@allure.story("用户注册")
@allure.title("注册接口-缺少密码")
@pytest.mark.regression
def test_register_missing_password(base_url):
    """密码为空时，注册应失败"""
    payload = {
        "email": "eve.holt@reqres.in",
        "password": ""
    }
    response = requests.post(f"{base_url}/register", json=payload)
    assert response.status_code == 400
    assert "error" in response.json()