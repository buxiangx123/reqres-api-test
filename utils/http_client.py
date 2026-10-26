import requests
from config.settings import BASE_URL, DEFAULT_HEADERS, TIMEOUT


class HttpClient:
    """统一的 HTTP 请求客户端"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(DEFAULT_HEADERS)

    def get(self, endpoint, params=None):
        """发送 GET 请求"""
        url = f"{BASE_URL}/{endpoint}"
        response = self.session.get(url, params=params, timeout=TIMEOUT)
        return response

    def post(self, endpoint, json=None):
        """发送 POST 请求"""
        url = f"{BASE_URL}/{endpoint}"
        response = self.session.post(url, json=json, timeout=TIMEOUT)
        return response