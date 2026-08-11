import pymysql
import logging
import os

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s | %(name)s || %(levelname)s | %(message)s',
                    handlers=[
                        logging.FileHandler("school.log", encoding="utf-8"),
                        logging.StreamHandler(),
                    ]
                    )


class DBmysql:
    def __init__(self):
        self.conn = None
        self.cur = None

    def get_conn(self):
        """连接数据库，优先使用环境变量，fallback 到默认值"""
        try:
            self.conn = pymysql.connect(
                host=os.getenv("DB_HOST", "127.0.0.1"),
                port=int(os.getenv("DB_PORT", "3306")),
                user=os.getenv("DB_USER", "root"),
                password=os.getenv("DB_PASS", "123456"),
                database=os.getenv("DB_NAME", "user_stu"),
                charset="utf8mb4",
                cursorclass=pymysql.cursors.DictCursor
            )
            self.cur = self.conn.cursor()
            logging.info(f"mysql数据库连接成功 host={os.getenv('DB_HOST', 'localhost')}")
        except Exception as e:
            logging.error(f"数据库连接失败：{e}")
            raise e

    def execute_dml(self, sql, params=None):
        """执行增删改（insert/update/delete）"""
        try:
            self.get_conn()
            if params is None:
                self.cur.execute(sql)
            else:
                self.cur.execute(sql, params)
            self.conn.commit()
            return self.cur.rowcount  # 返回影响行数
        except Exception as e:
            self.conn.rollback()
            print(e)
            logging.error(f"DML异常 SQL:{sql} Err:{str(e)}")
            raise
        finally:
            self.close()

    def execute_query(self, sql, params=None):
        """执行查询 select"""
        try:
            self.get_conn()
            if params is None:
                self.cur.execute(sql)
            else:
                self.cur.execute(sql, params)
            return self.cur.fetchall()
        except Exception as e:
            print(e)
            logging.error(f"{e}")
            logging.error(f"QUERY异常 SQL:{sql} Err:{str(e)}")
            raise
        finally:
            self.close()

    def execute_dml_return_id(self, sql, params=None):
        """执行 insert，提交后返回自增主键 id"""
        try:
            self.get_conn()
            if params is None:
                self.cur.execute(sql)
            else:
                self.cur.execute(sql, params)
            self.conn.commit()
            return self.cur.lastrowid
        except Exception as e:
            self.conn.rollback()
            logging.error(f"DML(return_id)异常 SQL:{sql} Err:{str(e)}")
            raise
        finally:
            self.close()

    def close(self):
        if self.cur:
            self.cur.close()
            self.cur = None
        if self.conn:
            self.conn.close()
            self.conn = None