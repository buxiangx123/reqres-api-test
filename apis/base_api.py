from utils.http_client import HttpClient


class BaseAPI:
    """
    所有具体 API 类的基类
    """

    def __init__(self):
        # 1. 统一初始化 HTTP 客户端（HttpClient 内部会自动读取 config.yaml 中的 base_url）
        self.http_client = HttpClient()

    @property
    def client(self):
        """对外暴露统一的请求发送器"""
        return self.http_client