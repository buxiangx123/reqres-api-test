from utils.http_client import HttpClient


class UserApi:
    """用户相关接口封装"""

    def __init__(self):
        self.client = HttpClient()

    def get_users(self, page=1):
        """查询用户列表"""
        return self.client.get("users", params={"page": page})

    def register(self, email, password):
        """用户注册"""
        payload = {"email": email, "password": password}
        return self.client.post("register", json=payload)