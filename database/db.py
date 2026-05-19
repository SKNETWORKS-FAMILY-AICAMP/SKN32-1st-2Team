# db.py
import pymysql
from pymysql.cursors import DictCursor
from sqlalchemy import create_engine

def get_sqlalchemy_engine():
    USER     = "student"
    PASSWORD = "student80"
    HOST     = "localhost"
    PORT     = 3306
    DATABASE = "ev_database"
    url = f"mysql+pymysql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}?charset=utf8mb4"
    return create_engine(url)

class DBHandler:
    def __init__(self):
        self.config = {
            "host":        "localhost",
            "user":        "student",
            "password":    "student80",
            "database":    "ev_database",
            "charset":     "utf8mb4",
            "cursorclass": DictCursor
        }

    def execute(self, sql: str, params: tuple = ()):
        connection = pymysql.connect(**self.config)
        try:
            with connection.cursor() as cursor:
                cursor.execute(sql, params)
            connection.commit()
        finally:
            connection.close()

    # FAQ 크롤러가 execute_query 로 호출하므로 execute 와 동일하게 연결
    def execute_query(self, sql: str, params: tuple = ()):
        self.execute(sql, params)

    def fetch_all(self, sql: str, params: tuple = ()):
        connection = pymysql.connect(**self.config)
        try:
            with connection.cursor() as cursor:
                cursor.execute(sql, params)
                return cursor.fetchall()
        finally:
            connection.close()