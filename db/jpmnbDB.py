import pymysql
import os
from dotenv import load_dotenv
load_dotenv()

db_host = os.getenv("db_host")
db_user = os.getenv("db_user")
db_password = os.getenv('db_password')
db_name = os.getenv('db_name')
db_charset  = os.getenv('db_charset')
db_port = os.getenv('db_port')

class DB:
    def connect(self):
        self.conn = pymysql.connect(
                             host=db_host,
                             user=db_user,
                             password=db_password,
                             db=db_name,
                             charset=db_charset,
                             cursorclass=pymysql.cursors.DictCursor,
                             port=int(db_port))

    def query(self, sql):
        try:
            self.connect()
            cursor = self.conn.cursor()
            cursor.execute(sql)
            self.conn.commit()
        except pymysql.OperationalError:
            self.connect()
            cursor = self.conn.cursor()
            cursor.execute(sql)
            self.conn.commit()
            print('重新連線')
        return cursor
    def close(self):
        self.connect()
        self.conn.close()