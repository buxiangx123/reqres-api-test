"""
conftest.py —— pytest 全局钩子

职责：
  1. 每次运行前清空 allure 结果目录（解决"只增不减"）
  2. 写入 Allure 的 environment.properties（⚠️ 必须在"清空"之后写，否则会被删掉）
  3. 会话级启动 Flask Mock 服务（在 pytest 进程内跑，覆盖率才统计得到）
  4. 用例失败时，把最后一次请求/响应挂到 Allure 附件
"""

import json
import os
import shutil
import sys
import threading
import time
from datetime import datetime

import allure
import pytest
import requests


def allure_dir(config):
    """返回本次运行真实的 allure 结果目录。

    --alluredir 可能来自三处：pytest.ini 的 addopts、命令行参数、CI 的显式参数。
    这里直接问 config 要，避免几处各写一份导致不一致：
    本地是 report/allure_results，CI 是 allure-results，
    environment.properties 就会写到错误的目录、报告里看不到。
    """
    configured = getattr(config.option, "allure_report_dir", None)
    if configured:
        return os.path.abspath(configured)
    return os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "report", "allure_results"
    )


def pytest_sessionstart(session):
    """先清空上次结果，再写入 environment.properties —— 顺序不能反。"""
    results_dir = allure_dir(session.config)

    # 1) 清空
    if os.path.exists(results_dir):
        for item in os.listdir(results_dir):
            item_path = os.path.join(results_dir, item)
            if os.path.isdir(item_path):
                shutil.rmtree(item_path)
            else:
                os.remove(item_path)
    else:
        os.makedirs(results_dir, exist_ok=True)

    # 2) 写入环境信息
    env_props = {
        "Python": sys.version.split()[0],
        "Platform": sys.platform,
        "Test Environment": os.getenv("TEST_ENV", "local"),
        "Database": os.getenv("DB_NAME", "autotest_db"),
        "Mock Server": "http://127.0.0.1:5000",
        "Run Time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }

    with open(
        os.path.join(results_dir, "environment.properties"), "w", encoding="utf-8"
    ) as f:
        for k, v in env_props.items():
            f.write(f"{k}={v}\n")


@pytest.fixture(scope="session", autouse=True)
def mock_server():
    """在 pytest 进程内启动 Flask，让 coverage 能统计到 Mock 服务代码。"""
    from mock_server.app import app, ensure_seed_data

    ensure_seed_data()

    server = threading.Thread(
        target=lambda: app.run(host="127.0.0.1", port=5000, use_reloader=False),
        daemon=True,
    )
    server.start()

    # 等待服务就绪（最多 15 秒）
    for _ in range(30):
        try:
            requests.get("http://127.0.0.1:5000/api/users?page=1", timeout=1)
            break
        except Exception:
            time.sleep(0.5)

    yield


# ==================== 失败现场留存 ====================

_clients_at_test_start = {}


def pytest_runtest_setup(item):
    """记录本用例开始前，HttpClient 注册表的大小。"""
    from utils.http_client import HTTP_CLIENTS

    _clients_at_test_start[item.nodeid] = len(HTTP_CLIENTS)


def _client_for(item):
    """找出属于当前用例的 HttpClient。

    不能直接取 HTTP_CLIENTS[-1]：注册表是全局的、只增不减，
    最后创建的那个 client 未必属于当前失败的用例
    （例如 class 级 setup 创建的 client 会早于后面用例创建的 client）。
    """
    from utils.http_client import HTTP_CLIENTS

    start = _clients_at_test_start.get(item.nodeid, 0)
    created_in_this_test = [
        c for c in HTTP_CLIENTS[start:] if getattr(c, "last_request", None)
    ]
    if created_in_this_test:
        return created_in_this_test[-1]

    # 本用例没新建 client（复用了 class 级实例）→ 退回"最后一个发过请求的"
    with_request = [c for c in HTTP_CLIENTS if getattr(c, "last_request", None)]
    return with_request[-1] if with_request else None


def _safe_json(text):
    """尝试把响应体格式化成缩进 JSON，失败则原样返回。"""
    try:
        return json.dumps(json.loads(text), ensure_ascii=False, indent=2)
    except Exception:
        return text


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()

    if report.when != "call" or not report.failed:
        return

    client = _client_for(item)
    if client is not None:
        last_req = getattr(client, "last_request", None)
        last_resp = getattr(client, "last_response", None)

        if last_req:
            allure.attach(
                json.dumps(last_req, ensure_ascii=False, indent=2),
                name="请求详情",
                attachment_type=allure.attachment_type.JSON,
            )

        if last_resp:
            allure.attach(
                _safe_json(last_resp.get("body", "")),
                name="响应详情",
                attachment_type=allure.attachment_type.JSON,
            )

    if report.longrepr:
        allure.attach(
            str(report.longrepr),
            name="失败原因",
            attachment_type=allure.attachment_type.TEXT,
        )