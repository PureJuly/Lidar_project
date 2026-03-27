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
    '/scan', # modified line by hyomin 
    'sensor_msgs/msg/LaserScan' # modified line by hyomin
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
    lidar_data = msg['ranges'] # modified line by hyomin

def control_turtle(): # modified function by hyomin
    global lidar_data

    if not lidar_data or len(lidar_data) < 360:
        return "move_front", cmd_msg(lin_x = 0.5, ang_z = 0.0)

    front_dist = min(min(lidar_data[0:20]), min(lidar_data[340:360]))
    left_dist = min(lidar_data[70:110])
    right_dist = min(lidar_data[250,290])

    SAFE_DIST = 1.0

    if front_dist < SAFE_DIST:
        action = "turn_right"
    elif left_dist < SAFE_DIST:
        action = "turn_right"
    elif right_dist < SAFE_DIST:
        action = "turn_left"
    else:
        action = "move_front"

    lin_x, ang_z = 0.0, 0.0
    if action == "move_front":
        lin_x = 0.5
    elif action == "turn_left":
        ang_z = 0.5
    elif action == "turn_right":
        ang_z = -0.5

    return action, cmd_msg(lin_x = lin_x, ang_z = ang_z)

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