# 🚀 API AutoTest - 轻量级接口自动化测试框架

基于 Python3 + Pytest + Requests 构建的企业级 API 自动化测试框架。支持配置驱动、分层封装、双通道日志及多环境一键切换。

## 📁 项目目录结构

```text
C:\api-autotest/
├── apis/              # 业务层：按业务模块封装的接口类 (如 AuthApi, UserApi)
├── config/            # 配置层：存放基础 URL、超时时间等 YAML 配置文件
├── testcases/         # 用例层：存放 pytest 编写的测试用例 (.py 文件)
├── utils/             # 核心工具层：HTTP 封装、配置读取、日志封装
├── logs/              # 日志目录：自动生成的执行日志文件
├── __init__.py        # 项目根目录标识
└── README.md          # 项目说明文档