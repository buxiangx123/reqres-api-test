import requests
import os
from requests.exceptions import RequestException
from utils.config_reader import ConfigReader
from utils.logger import logger

# 全局注册表：记录所有创建过的 HttpClient 实例，供失败时留存现场
HTTP_CLIENTS = []
class HttpClient:
    """
    框架底层通用请求类
    负责处理：统一URL拼接、超时设置、异常捕获、Token管理
    """

    def __init__(self):
        # 确保这一行是小写的 logger
        from utils.logger import logger

        # 1. 初始化配置读取器
        # 自动定位 config.yaml 的路径并传入
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        config_path = os.path.join(root_dir, "config", "config.yaml")
        self.reader = ConfigReader(config_path)

        self.log = logger
        # 2. 从配置中读取基础URL和超时时间，并保存为类属性
        self.base_url = self.reader.get("base_url", "")
        self.TIMEOUT = self.reader.get("timeout", 10) # 获取超时时间，默认为10秒  # 【新增】这一步让后面能找到 TIMEOUT
        self.session = requests.Session()
        # 记录最后一次请求/响应，供失败时留存现场
        self.last_request = None
        self.last_response = None
        # 登记到全局注册表
        HTTP_CLIENTS.append(self)

    def set_token(self, token):
        """
        设置全局 Token，之后的请求会自动带上
        """
        if token:
            self.session.headers.update({"Authorization": f"Bearer {token}"})

    def send_request(self, method, url, raise_error=True, **kwargs):
        """
        统一的请求发送核心方法
        method: 请求方式 (GET, POST, PUT, DELETE)
        url: 接口的后半段路径 (例如: /users)
        raise_error: 是否对 4xx/5xx 抛出异常。
                     默认 True（保持原有行为）；
                     测试「期望失败」的场景时传 False，由测试自行断言状态码。
        **kwargs: 接收所有额外参数 (json, params, headers, data等)
        """
        # 1. 拼接完整URL
        full_url = f"{self.base_url}{url}"

        try:
            # 【新增】打印请求日志
            self.log.info(f"发送 {method} 请求: {full_url}")
            self.log.info(f"请求参数: {kwargs}")

            # 2. 统一设置超时时间，防止某个请求卡死整个框架
            kwargs.setdefault("timeout", self.TIMEOUT)

            # 3. 使用 session.request 统一发送请求
            # session.request 比 session.get/post 更灵活，它能处理所有HTTP方法
            # 记录请求现场
            self.last_request = {
                "method": method,
                "url": full_url,
                "params": kwargs.get("params"),
                "json": kwargs.get("json"),
                "data": kwargs.get("data"),
                "headers": dict(self.session.headers),
            }
            resp = self.session.request(method=method, url=full_url, **kwargs)

            # 如果状态码不是 2xx，抛出异常（可通过 raise_error=False 关闭）
            if raise_error:
                resp.raise_for_status()

            # 【新增】打印响应日志
            self.log.info(f"响应状态码: {resp.status_code}")
            # 记录响应现场（截断过长的响应体，避免报告过大）
            body_text = resp.text[:2000] if resp.text else ""
            self.last_response = {
                "status_code": resp.status_code,
                "elapsed_ms": round(resp.elapsed.total_seconds() * 1000, 2),
                "body": body_text,
            }
            # 4. 返回完整的响应对象
            return resp

        except RequestException as e:
            # 统一捕获并打印详细的错误信息，方便排查问题
            print(f"\n❌ 请求异常: {full_url} | 错误原因: {e}\n")
            # 【新增】打印错误日志
            self.log.error(f"请求异常: {e}")
            raise

    def close(self):
        """用完之后记得关闭会话"""
        self.session.close()