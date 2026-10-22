import pytest
import requests


class TestReqResAPI:

    BASE_URL = "https://reqres.in"

    def test_get_users(self):
        """测试1：获取用户列表"""
        resp = requests.get(f"{self.BASE_URL}/api/users?page=2")
        assert resp.status_code == 200, "获取用户列表失败"
        assert "data" in resp.json()
        print("\n✅ 测试1通过：获取用户列表")

    def test_get_not_exist_user(self):
        """测试2：查询不存在的用户（404）"""
        resp = requests.get(f"{self.BASE_URL}/api/users/9999")
        assert resp.status_code == 404
        # 404返回空对象，不需要断言data
        print("\n✅ 测试2通过：查询不存在的用户")

    def test_login(self):
        """测试3：用户登录"""
        payload = {"email": "eve.holt@reqres.in", "password": "cityslicka"}
        resp = requests.post(f"{self.BASE_URL}/api/login", json=payload)
        assert resp.status_code == 200
        body = resp.json()
        assert "token" in body, "登录应该返回token"
        print("\n✅ 测试3通过：用户登录")