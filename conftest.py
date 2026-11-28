"""
conftest.py —— pytest 全局配置钩子
职责：
  1. 每次运行前自动清空 allure 结果目录（解决"只增不减"问题）
  2. 未来可在此处添加统一的 fixture（如共享 HttpClient、登录态等）
"""
import pytest
import os
import shutil
from datetime import datetime
import sys
import threading
import time
import requests

def pytest_sessionstart(session):
    """
    pytest 启动时自动执行：清空 allure 结果目录，
    确保每次生成的报告只包含本次运行的结果。
    """
    allure_results_dir = os.path.join(session.config.rootdir.strpath, "report", "allure_results")

    if os.path.exists(allure_results_dir):
        # 删除目录下所有文件和子目录，但保留 allure_results 本身
        for item in os.listdir(allure_results_dir):
            item_path = os.path.join(allure_results_dir, item)
            if os.path.isdir(item_path):
                shutil.rmtree(item_path)
            else:
                os.remove(item_path)
    else:
        # 目录不存在则创建（首次运行时）
        os.makedirs(allure_results_dir, exist_ok=True)


def pytest_configure(config):
    """生成 Allure 环境信息文件"""
    env_dir = "allure-results"
    os.makedirs(env_dir, exist_ok=True)

    env_props = {
        "Python": sys.version.split()[0],
        "Platform": sys.platform,
        "Test Environment": os.getenv("TEST_ENV", "local"),
        "Database": os.getenv("DB_NAME", "reqres_test"),
        "Mock Server": "http://127.0.0.1:5000",
        "Run Time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }

    with open(os.path.join(env_dir, "environment.properties"), "w", encoding="utf-8") as f:
        for k, v in env_props.items():
            f.write(f"{k}={v}\n")


@pytest.fixture(scope="session", autouse=True)
def mock_server():
    """在 pytest 进程内启动 Flask，让 coverage 能统计到"""
    from mock_server.app import app, ensure_seed_data
    ensure_seed_data()

    server = threading.Thread(
        target=lambda: app.run(host="127.0.0.1", port=5000, use_reloader=False),
        daemon=True
    )
    server.start()

    # 等待服务就绪
    for _ in range(30):
        try:
            requests.get("http://127.0.0.1:5000/api/users?page=1", timeout=1)
            break
        except Exception:
            time.sleep(0.5)

    yield