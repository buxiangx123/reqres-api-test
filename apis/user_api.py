from apis.base_api import BaseAPI

class UserApi(BaseAPI):
    """用户管理相关接口"""

    def list_users(self, page=1):
        """获取用户列表"""
        return self.client.send_request(
            method="GET",
            url="/users",  # 注意：这里只写路径，不要带 base_url
            params={"page": page}
        )

    def get_user(self, user_id):
        """获取指定用户"""
        return self.client.send_request(
            method="GET",
            url=f"/users/{user_id}" # 同样，只写路径
        )

    def create_user(self, name, job):
        """新增用户 (原 reqres 风格接口)"""
        payload = {"name": name, "job": job}
        return self.client.send_request(
            method="POST",
            url="/users", # 只写路径
            json=payload
        )

    def update_user(self, user_id, name, job):
        """更新用户"""
        payload = {"name": name, "job": job}
        return self.client.send_request(
            method="PUT",
            url=f"/users/{user_id}", # 只写路径
            json=payload
        )

    def delete_user(self, user_id):
        """删除用户"""
        return self.client.send_request(
            method="DELETE",
            url=f"/users/{user_id}" # 只写路径
        )

    def add_user(self, username, email):
        """新增用户 (你的业务接口)"""
        payload = {
            "username": username,
            "email": email
        }
        return self.client.send_request(
            method="POST",
            url="/users", # 只写路径
            json=payload
        )