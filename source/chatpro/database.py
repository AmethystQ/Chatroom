import pymysql
from config import *


class DataBase(object):
    def __init__(self):
        # connect to the sql database
        self.connect = pymysql.connect(host=DATABASE_HOST,
                                       port=DATABASE_PORT,
                                       database=DATABASE_NAME,
                                       user=DATABASE_USER,
                                       password=DATABASE_PASSWORD,
                                       charset='utf8')
        # get the cursor
        self.cursor = self.connect.cursor()

    def query(self, sql):
        # query the user information
        self.cursor.execute(sql)
        result = self.cursor.fetchone()
        if not result:
            return None
        fields = [field[0] for field in self.cursor.description]
        return_data = {}
        for field, value in zip(fields, result):
            return_data[field] = value
        return return_data

    def close(self):
        # release the resource
        self.cursor.close()
        self.connect.close()


if __name__ == '__main__':
    db = DataBase()
    data=db.query("select * from users WHERE user_name='user2'")
    print(data)
    db.close()
