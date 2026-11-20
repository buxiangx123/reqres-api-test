import sys
import os
from loguru import logger

# 1. 获取项目根目录
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# 2. 设置日志存放的文件夹
LOG_DIR = os.path.join(BASE_DIR, "logs")
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)
# 3. 日志文件路径
LOG_FILE = os.path.join(LOG_DIR, "api_test_{time:YYYY-MM-DD}.log")

# 4. 移除默认的输出
logger.remove()

# 5. 配置控制台输出（带颜色的高亮日志）
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
    colorize=True,
)

# 6. 配置文件输出
logger.add(
    LOG_FILE,
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function} - {message}",
    rotation="500 MB",  # 日志文件超过 500M 自动切分
    retention="7 days", # 只保留最近 7 天的日志
)