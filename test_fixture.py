import pytest
import requests


# @pytest.fixture
# def base_url():
#     """这个就是 fixture：它负责准备一个公共数据"""
#     return "https://reqres.in/api"


def test_get_users(base_url):
    """注意参数名 base_url，它和上面的函数名一模一样"""
    resp = requests.get(f"{base_url}/users?page=2")
    assert resp.status_code == 200
    print("\n✅ 用了fixture的测试通过")





    # ⬇️ 这一段顶格，不要在 class 里面！
@pytest.fixture(scope="class")
def create_user():
        payload = {"name": "morpheus", "job": "leader"}
        resp = requests.post("https://reqres.in/api/users", json=payload)
        print("\n🔧 fixture：创建用户")
        return resp.json()

class TestUsers:
        # ⬇️ 只有测试方法在 class 里面，注意不要写 self 在 create_user 上
    def test_user_create(self, create_user):
            assert "id" in create_user
            assert create_user["name"] == "morpheus"
            print("✅ 测试1：用户已创建")

    def test_user_has_job(self, create_user):
            assert create_user["job"] == "leader"
            print("✅ 测试2：用户有job字段")