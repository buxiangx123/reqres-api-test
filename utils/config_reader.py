import os
import yaml


class ConfigReader:
    """
    配置文件读取器，支持多环境（envs）配置

    取值优先级：
      1. envs[test_env] 里同名的键
      2. 文件顶层的同名键
      3. 调用时传入的 default
    """

    def __init__(self, file_path=None):
        self.file_path = file_path
        self._config = {}
        if not self.file_path:
            return
        if not os.path.exists(self.file_path):
            # 找不到配置文件必须立刻报错。否则会静默读成空字典，
            # 表现为 base_url 为空、URL 变成 "/users"，很难排查。
            raise FileNotFoundError(f"配置文件不存在: {self.file_path}")
        self._load_config()

    def _load_config(self):
        """加载 YAML 配置文件"""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                self._config = yaml.safe_load(f) or {}
        except yaml.YAMLError as e:
            raise ValueError(f"YAML 解析失败: {e}") from e

    def _env_config(self):
        """返回 envs 下当前激活环境（test_env）的配置字典"""
        envs = self._config.get("envs") or {}
        env = self._config.get("test_env")
        if env is None:
            return {}
        if env not in envs:
            raise KeyError(
                f"test_env={env!r} 在 envs 中不存在，可选值: {list(envs)}"
            )
        return envs[env] or {}

    def get(self, key, default=None):
        """
        获取配置项：先看当前环境，再看顶层，最后用 default
        这样 get("base_url") 返回的就是 envs[test_env].base_url
        """
        env_cfg = self._env_config()
        if key in env_cfg:
            return env_cfg[key]
        return self._config.get(key, default)