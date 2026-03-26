import roslibpy
import time

HOST = "127.0.0.1"
PORT = 9090
client = roslibpy.Ros(HOST, PORT)

lidar_topic = roslibpy.Topic(
    client,
    '(lidar_topic_name)',
    '(lidar_topic_interface)'
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


def main():
    client.run()
    msg = cmd_msg(lin_x=1.0, lin_y=0.5, ang_z=1.0)
    while client.is_connected:
        cmd_topic.publish(roslibpy.Message(msg))
        time.sleep(1)

    client.terminate()

if __name__ == '__main__':
    main()