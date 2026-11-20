import os
import pymysql

class DBUtil:
    """数据库工具类：封装连接、查询、增删改和关闭"""

    def __init__(self,
                 host=os.getenv("DB_HOST", "127.0.0.1"),
                 port=int(os.getenv("DB_PORT", "3306")),
                 user=os.getenv("DB_USER", "root"),
                 password=os.getenv("DB_PASSWORD", "123456"),
                 database=os.getenv("DB_NAME", "autotest_db"),
                 charset="utf8mb4"):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database
        self.charset = charset
        self.conn = None
        self.cursor = None

    def connect(self):
        """建立数据库连接"""
        self.conn = pymysql.connect(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            database=self.database,
            charset=self.charset,
            autocommit=False
        )
        self.cursor = self.conn.cursor(pymysql.cursors.DictCursor)
        return self

    def execute(self, sql, params=None):
        """执行增删改，返回影响行数"""
        if not self.conn or not self.cursor:
            self.connect()
        self.cursor.execute(sql, params)
        self.conn.commit()
        return self.cursor.rowcount

    def query_one(self, sql, params=None):
        """查询一条数据"""
        if not self.conn or not self.cursor:
            self.connect()
        self.cursor.execute(sql, params)
        return self.cursor.fetchone()

    def query_all(self, sql, params=None):
        """查询多条数据"""
        if not self.conn or not self.cursor:
            self.connect()
        self.cursor.execute(sql, params)
        return self.cursor.fetchall()

    def close(self):
        """关闭游标和连接"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        self.cursor = None
        self.conn = None

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()