import requests
import logging
from requests.exceptions import RequestException

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')


class HTTPClient:
    def __init__(self, base_url):
        self.base_url = base_url

    def _request(self, method, path, **kwargs):
        url = f"{self.base_url}{path}"
        try:
            return requests.request(method, url, timeout=10, **kwargs)
        except RequestException as e:
            logging.error(f"请求异常: {e}")
            raise

    def get(self, path, **kwargs):
        return self._request("GET", path, **kwargs)

    def post(self, path, **kwargs):
        return self._request("POST", path, **kwargs)

    def put(self, path, **kwargs):
        return self._request("PUT", path, **kwargs)

    def delete(self, path, **kwargs):
        return self._request("DELETE", path, **kwargs)


client = HTTPClient("https://reqres.in")