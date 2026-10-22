import pytest
from http_client import client


@pytest.mark.parametrize("method, path, payload, expected_status, case_name", [
    ("get",    "/api/users?page=2", None, 200, "获取用户列表"),
    ("get",    "/api/users/2",      None, 200, "查询存在的用户"),
    ("get",    "/api/users/9999",   None, 404, "查询不存在的用户(404)"),
    ("post",   "/api/login", {"email": "eve.holt@reqres.in", "password": "cityslicka"}, 200, "用户登录"),
    ("post",   "/api/users", {"name": "morpheus", "job": "leader"}, 201, "创建用户(201)"),
    ("put",    "/api/users/2", {"name": "morpheus", "job": "zion resident"}, 200, "更新用户"),
    ("delete", "/api/users/2", None, 204, "删除用户(204无响应体)"),
])
def test_users(method, path, payload, expected_status, case_name):
    if method == "get":
        resp = client.get(path)
    elif method == "post":
        resp = client.post(path, json=payload)
    elif method == "put":
        resp = client.put(path, json=payload)
    elif method == "delete":
        resp = client.delete(path)
    else:
        raise ValueError(f"不支持的请求方法: {method}")

    # 1. 基础断言 (assert ==)：状态码必须符合预期
    assert resp.status_code == expected_status, \
        f"{case_name} 失败：期望 {expected_status}，实际 {resp.status_code}"

    # 404 和 204 比较特殊，无需检查响应体内部数据
    if expected_status == 404 or expected_status == 204:
        print(f"\n✅ {case_name} 通过 | 状态码: {resp.status_code}")
        return

    body = resp.json()
    assert body is not None, f"{case_name} 失败：响应为空"

    # 2. 业务逻辑断言 (assert in)：针对不同接口做差异化断言
    if "login" in path:
        # 登录接口断言：必须返回 token
        assert "token" in body, f"{case_name} 失败：未返回 token"
    elif "api/users/9999" in path:
        # 404 接口断言：确保是空的 (上面已经过滤，这里只是兜底)
        assert body == {}, f"{case_name} 失败：响应不为空"
    elif "api/users" in path and method == "post":
        # 创建用户断言：检查响应是否包含我们传入的 name 和 job
        assert body["name"] == payload["name"] and body["job"] == payload["job"], \
            f"{case_name} 失败：创建的用户信息不匹配"
    elif "api/users/2" in path and method == "put":
        # 更新用户断言：检查响应是否包含修改后的 name
        assert "morpheus" in str(body.values()), f"{case_name} 失败：未正确返回更新数据"
    else:
        # 常规的 GET 请求：检查是否有 data 字段
        assert "data" in body, f"{case_name} 失败：响应缺少关键字段"

    print(f"\n✅ {case_name} 通过 | 状态码: {resp.status_code} | 响应数据: {str(body)[:150]}")