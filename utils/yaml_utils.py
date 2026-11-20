import yaml
import os


class YamlUtils:
    @staticmethod
    def read_yaml(yaml_file, key=None):
        """
        读取YAML文件并返回数据
        :param yaml_file: YAML文件名 (如 'test_data.yaml')
        :param key: 想要获取的顶层键名 (如 'create_user')，默认为None返回所有数据
        :return: 解析后的 Python 数据 (字典或列表)
        """
        # 获取当前文件所在的根目录路径，实现相对路径读取
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        yaml_path = os.path.join(root_dir, yaml_file)

        try:
            with open(yaml_path, 'r', encoding='utf-8') as file:
                data = yaml.safe_load(file)

            # 如果传入了key，就返回对应的数据；否则返回所有数据
            if key:
                return data.get(key, None)
            return data
        except FileNotFoundError:
            raise FileNotFoundError(f"找不到 YAML 文件: {yaml_path}") from None
        except yaml.YAMLError as exc:
            raise ValueError(f"YAML 解析失败: {yaml_path}: {exc}") from exc