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

        self.initialize()

    def initialize(self):

        try:
            self.cur.execute((
                "create table if not exists lidardata("
                    "id int primary key auto_increment,"
                    "ranges json,"
                    "when_ datetime,"
                    "action varchar(50)"
                ");"
            ))
            self.conn.commit()
        except:
            self.conn.rollback()


    def put_data(self, ranges:list[float], when:datetime, action:str):
        try:
            json_ranges = json.dumps(ranges)
            self.cur.execute(
                '''insert into lidardata(ranges, when_, action) values(%s,%s,%s)''',
                (json_ranges,when,action)
            )
            self.conn.commit()
        except:
            self.conn.rollback()


if __name__ == '__main__':
    HOST = 'localhost'
    PW = "0000"

    db = DBConnector(HOST, PW)
    cursor = db.conn.cursor()

    #
    # import time
    # import random
    #
    # for i in range(100):
    #     lidar = [250-(random.random()*30) for _ in range(360)]
    #     action = random.sample(["move_front", "turn_left", "turn_right"], 1)[0]
    #     db.put_data(
    #         lidar,
    #         datetime.now(),
    #         action
    #     )
    #
    #     time.sleep(0.5)