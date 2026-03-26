import json

import pymysql
from datetime import datetime

class DBConnector:
    def __init__(self, host, pw):
        self.conn = pymysql.connect(
            host=host,
            user='root',
            password=pw,
            database='ros',
            charset='utf8'
        )
        self.cur = self.conn.cursor()

    def put_data(self, ranges:list[float], when:datetime, action:str):
        try:
            json_ranges = json.dumps(ranges)
            self.cur.execute(
                '''insert into lidardata(ranges, when_, action) values(%s,%s,%s)''',
                (json_ranges,when,action)
            )
            self.cur.fetchall()
            self.conn.commit()
        except:
            self.conn.rollback()


if __name__ == '__main__':
    HOST = 'localhost'
    PW = "0000"

    db = DBConnector(HOST, PW)
    cursor = db.conn.cursor()