import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..')) # 确保项目根目录在查找路径中



# 1. 引入 pytest 库
import pytest

from faker import Faker

from utils.yaml_utils import YamlUtils
# 2. 引入我们封装好的 UserApi 类
from apis.user_api import UserApi

fake = Faker('zh_CN')

class TestUser:

    def setup_class(self):
        """在运行整个测试类之前，创建一个用户接口的实例"""
        self.api = UserApi()

    @pytest.mark.smoke
    def test_list_users(self):
        """测试获取用户列表"""
        resp = self.api.list_users()
        assert resp.status_code == 200
        assert "data" in resp.json()

    @pytest.mark.smoke
    def test_get_user(self):
        """测试获取单个用户详情"""
        resp = self.api.get_user(1)
        assert resp.status_code == 200
        assert resp.json()["data"]["first_name"] == "George"

    @pytest.mark.smoke
    @pytest.mark.parametrize("user_data", YamlUtils.read_yaml("data/test_data.yaml", "create_user"))
    def test_create_user(self, user_data):
        """测试创建用户 (使用YAML数据进行数据驱动)"""
        # 2. 直接传入动态的 user_data
        resp = self.api.create_user(**user_data)

        assert resp.status_code == 201
        # 验证返回的name是否等于我们传入的name+
        assert resp.json()['name'] == user_data['name']

    def test_user_flow(self):
        """测试完整业务流程：使用 Faker 生成随机数据"""

        # 1. 使用 Faker 生成随机数据
        random_name = fake.name()
        random_job = fake.job()

        print(f"\n 本次测试使用的随机数据 -> 姓名: {random_name}, 职业: {random_job}")

        # 2. 发送请求创建用户
        create_data = {'name': random_name, 'job': random_job}
        create_resp = self.api.create_user(**create_data)

        # 3. 核心断言
        assert create_resp.status_code == 201
        resp_data = create_resp.json()
        assert resp_data['name'] == random_name
        assert resp_data['job'] == random_job

        print(f" 数据断言通过：{resp_data['name']} 已正确生成！")