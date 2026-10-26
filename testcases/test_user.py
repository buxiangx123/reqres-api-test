import pytest
import allure
from apis.user_api import UserApi


@pytest.fixture(scope="module")
def user_api():
    """模块级别复用 UserApi 实例"""
    return UserApi()


@allure.feature("用户管理")
@allure.story("查询用户列表")
@allure.title("查询第{page}页用户")
@pytest.mark.parametrize("page", [1, 2, 3])
@pytest.mark.smoke
def test_get_users(user_api, page):
    response = user_api.get_users(page=page)
    assert response.status_code == 200
    data = response.json()
    assert data["page"] == page


@allure.feature("用户管理")
@allure.story("用户注册")
@allure.title("注册接口-正常场景")
@pytest.mark.regression
def test_register_success(user_api):
    response = user_api.register("eve.holt@reqres.in", "cityslicka")
    assert response.status_code == 200
    assert "token" in response.json()


@allure.feature("用户管理")
@allure.story("用户注册")
@allure.title("注册接口-缺少密码")
@pytest.mark.regression
def test_register_missing_password(user_api):
    response = user_api.register("eve.holt@reqres.in", "")
    assert response.status_code == 400
    assert "error" in response.json()