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
        assert resp.status_code == 999
        assert "data" in resp.json()

    @pytest.mark.smoke
    def test_get_user(self):
        """测试获取单个用户详情（依赖 Flask 启动时预置的 id=1 George 种子数据）"""
        resp = self.api.get_user(1)
        assert resp.status_code == 200
        assert resp.json()["data"]["first_name"] == "George"

    @pytest.mark.smoke
    @pytest.mark.parametrize("user_data", YamlUtils.read_yaml("data/test_data.yaml", "create_user"))
    def test_create_user(self, user_data):
        """测试创建用户 (使用YAML数据进行数据驱动)"""
        resp = self.api.create_user(**user_data)

        assert resp.status_code == 201
        # 验证返回的name是否等于我们传入的name
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

    # ==================== 方向二：补全接口覆盖 ====================
    # 说明：打本地 Flask 后端时，PUT/DELETE 会真正改动数据库，
    #      因此不能操作 id=1（那是 test_get_user 依赖的种子数据），
    #      统一改为「先创建、再操作自己创建的那条」。

    @pytest.mark.smoke
    def test_update_user(self):
        """测试更新用户（先创建再更新，避免污染种子数据）"""
        # 1. 先创建一个专属用户，避免改动 id=1 的种子数据
        create_resp = self.api.create_user(name=fake.name(), job=fake.job())
        assert create_resp.status_code == 201, f"前置创建失败，状态码：{create_resp.status_code}"
        target_id = create_resp.json()['id']

        # 2. 用 Faker 生成新数据，避免硬编码
        new_name = fake.name()
        new_job = fake.job()

        print(f"\n本次更新使用的随机数据 -> id：{target_id}，姓名：{new_name}，职业：{new_job}")

        # 3. 调用更新接口
        resp = self.api.update_user(user_id=target_id, name=new_name, job=new_job)

        # 4. 核心断言：状态码
        assert resp.status_code == 200, f"更新用户失败，状态码：{resp.status_code}"

        # 5. 核心断言：响应体回显了传入的数据
        resp_data = resp.json()
        assert resp_data['name'] == new_name, f"姓名回显不一致：期望 {new_name}，实际 {resp_data.get('name')}"
        assert resp_data['job'] == new_job, f"职业回显不一致：期望 {new_job}，实际 {resp_data.get('job')}"

        # 6. 断言：返回了 updatedAt 时间戳
        assert 'updatedAt' in resp_data, f"响应体缺少 updatedAt 字段，实际字段：{list(resp_data.keys())}"

        print(f"更新接口回显校验通过：{resp_data['name']}")

    @pytest.mark.smoke
    def test_delete_user(self):
        """测试删除用户（DELETE 返回 204，响应体为空）
        先创建再删除，避免删掉 id=1 的种子数据导致 test_get_user 失败"""
        # 1. 先创建一个专属用户用于删除
        create_resp = self.api.create_user(name=fake.name(), job=fake.job())
        assert create_resp.status_code == 201, f"前置创建失败，状态码：{create_resp.status_code}"
        target_id = create_resp.json()['id']

        # 2. 调用删除接口
        resp = self.api.delete_user(user_id=target_id)

        # 3. 核心断言：DELETE 成功返回 204 No Content
        assert resp.status_code == 204, f"删除用户失败，状态码：{resp.status_code}"

        # 4. 核心断言：204 响应体必须为空
        #    注意：这里绝对不能调 resp.json()，204 没有响应体，会抛异常
        assert resp.text == "", f"204 响应体应为空，实际内容：{resp.text}"

        # 5. 【新增】删除后再查，确认真的删掉了（本地后端才能做这个验证）
        get_resp = self.api.get_user(target_id)
        assert get_resp.status_code == 404, f"删除后仍能查到该用户，状态码：{get_resp.status_code}"

        print("删除接口校验通过：状态码 204，响应体为空，且已确认删除生效")

    def test_update_user_not_exist(self):
        """异常场景：更新不存在的用户应返回 404"""
        resp = self.api.update_user(user_id=99999, name=fake.name(), job=fake.job())

        # 本地 Flask 后端对不存在的 id 返回 404（reqres 会返回 200，属其设计缺陷）
        assert resp.status_code == 404, f"更新不存在的用户应返回 404，实际：{resp.status_code}"

        print("异常场景校验通过：不存在的用户更新返回 404")

    def test_create_user_missing_name(self):
        """异常场景：创建用户缺少 name 字段应返回 400"""
        # 只传 job 不传 name，触发 app.py 第 57 行的参数校验
        resp = self.api.create_user(job=fake.job())

        assert resp.status_code == 400, f"缺少 name 应返回 400，实际：{resp.status_code}"
        assert "error" in resp.json(), f"响应体应包含 error 字段，实际：{resp.json()}"

        print("异常场景校验通过：缺少 name 返回 400")

    def test_delete_user_not_exist(self):
        """异常场景：删除不存在的用户应返回 404"""
        # 操作一个必然不存在的 id，触发 app.py 第 211 行
        resp = self.api.delete_user(user_id=99999)

        assert resp.status_code == 404, f"删除不存在的用户应返回 404，实际：{resp.status_code}"

        print("异常场景校验通过：不存在的用户删除返回 404")