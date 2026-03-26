import json

import pymysql
from datetime import datetime
import pandas as pd

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

    def get_data(self, from_n:int|None=None, to_n:int|None=None, latest_n:int|None=None, return_pd:bool=False):
        if (from_n or to_n) and latest_n:
            raise Exception("ID range selector(from_n, to_n) is not compatible with latest selector(latest_n)")
        elif (from_n is None) != (to_n is None):
            raise Exception(f"the value needed: {'to_n' if to_n is None else 'from_n'}")


        stmt = "select action, ranges from lidardata "
        args = ()
        if latest_n is not None:
            stmt += "order by id desc limit %s"
            args = (latest_n,)
        elif from_n is not None:
            stmt += "where id between %s and %s"
            args = (from_n, to_n)

        stmt += ";"

        if return_pd:
            return pd.read_sql_query(stmt, self.conn, params=list(args))
        else:
            try:
                self.cur.execute(stmt, args)
                return self.cur.fetchall()
            except Exception as e:
                self.conn.rollback()
                raise e



if __name__ == '__main__':
    HOST = 'localhost'
    PW = "0000"

    db = DBConnector(HOST, PW)
    cursor = db.conn.cursor()

    df = db.get_data(from_n=20, to_n=50)
    print(df)
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