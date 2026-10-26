import requests


def test_create_user(base_url, auth_token):
    """
    测试创建新用户（需要 Token 鉴权）
    参数写了 base_url 和 auth_token，Pytest 会自动从 conftest.py 找它们
    """
    # 1. 准备请求头
    # headers = {
    #     "Authorization": f"Bearer {auth_token}",  # 自动填入 token
    #     "Content-Type": "application/json"
    # }

    # 2. 准备创建用户的数据
    payload = {
        "name": "morpheus",
        "job": "leader"
    }

    # 3. 发起 POST 请求
    response = requests.post(f"{base_url}/users", json=payload)

    # 4. 断言状态码是 201（创建成功）
    assert response.status_code == 201
    assert response.json()["name"] == "morpheus"

    print("\n✅ 鉴权测试通过！用户创建成功！")