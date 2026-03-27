import json
from datetime import datetime

import roslibpy
import time
from db_connector import DBConnector

HOST = "127.0.0.1"
PORT = 9090
client = roslibpy.Ros(HOST, PORT)

lidar_topic = roslibpy.Topic(
    client,
    '(PLACEHOLDER:lidar_topic_name)',
    '(PLACEHOLDER:lidar_topic_type)'
)
cmd_topic = roslibpy.Topic(
    client,
    '/turtle1/cmd_vel',
    'geometry_msgs/msg/Twist',
)

def cmd_msg(lin_x=0.0, lin_y=0.0, ang_z=0.0):
    return {
        "linear": {
            "x": lin_x,
            "y": lin_y
        },
        "angular": {
            "z": ang_z,
        }
    }

lidar_data = []
def update_lidar(msg):
    global lidar_data
    lidar_data = msg.PLACEHOLDER_lidar_data_name

def control_turtle():
    # todo
    action = "(PLACEHOLDER:action_name)"
    return action, cmd_msg()

def main(db):
    client.run()
    lidar_topic.subscribe(update_lidar)
    while client.is_connected:
        action, msg = control_turtle()
        cmd_topic.publish(roslibpy.Message(msg))
        db.put_data(
            ranges=lidar_data,
            when=datetime.now(),
            action=action,
        )
        time.sleep(1)

    client.terminate()

if __name__ == '__main__':
    HOST = 'localhost'
    PW = "0000"

    db = DBConnector(HOST, PW)
    main(db)