import random
from utils.http_client import HttpClient
from utils.config_reader import ConfigReader

class AuthApi:
    """
    认证相关接口封装
    主要负责：登录、注册、获取Token
    """

    def __init__(self):
        self.client = HttpClient()  # 只写这一行！里面不要有任何参数

    def login(self, email=None, password=None):
        """
        用户登录接口
        """
        # 每次发请求前，清空历史遗留的 Token，防止 401
        self.client.session.headers.pop("Authorization", None)

        url = "/login"
        payload = {
            "email": email,
            "password": password,
            "_random": random.randint(1, 100000)
        }

        print(f"🚀 正在尝试登录用户: {email}...")
        resp = self.client.send_request("POST", url, json=payload, raise_error=False)

        # 如果登录成功（200），提取 Token
        if resp.status_code == 200:
            try:
                data = resp.json()
                token = data.get("token")

                if token:
                    self.client.set_token(token.strip())
                    print(f"\n✅ 登录成功！Token 已自动注入到 Session 中。")
                else:
                    print("\n⚠️ 登录成功但未在响应中找到 Token。")
            except Exception as e:
                print(f"\n⚠️ 解析 Token 失败: {e}")

        return resp

    def register(self, email, password):
        """
        用户注册接口
        """
        # 同样，发送注册请求前也清理一下 Header
        self.client.session.headers.pop("Authorization", None)

        url = "/register"
        payload = {
            "email": email,
            "password": password
        }
        return self.client.send_request("POST", url, json=payload)