"""
conftest.py —— pytest 全局配置钩子
职责：
  1. 每次运行前自动清空 allure 结果目录（解决"只增不减"问题）
  2. 未来可在此处添加统一的 fixture（如共享 HttpClient、登录态等）
"""

import os
import shutil


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