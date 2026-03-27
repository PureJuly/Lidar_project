import json
import math
import os
import random
import rclpy as rp
from rclpy.node import Node
from sensor_msgs.msg import LaserScan

ANGLE_MIN_DEG = 0
ANGLE_MAX_DEG = 359
ANGLE_INCREMENT_DEG = 1
NUM_POINTS = 360
RANGE_MIN = 0.12
RANGE_MAX = 3.5

def create_empty_scan():
	ranges = [RANGE_MAX for _ in range(NUM_POINTS)]
	intensities = [100 for _ in range(NUM_POINTS)]
	scan = {
	"angle_min" : math.radians(ANGLE_MIN_DEG), 
	"angle_max" : math.radians(ANGLE_MAX_DEG), 
	"angle_increment" : math.radians(ANGLE_INCREMENT_DEG), 
	"range_min" : RANGE_MIN, 
	"range_max" : RANGE_MAX, 
	"ranges" : ranges,
	"intensities" : intensities
	}
	return scan

def make_the_wall(ranges, center_deg, width_deg):
	half_width = width_deg // 2
	for offset in range(-half_width, half_width + 1):
		idx = (center_deg + offset) % NUM_POINTS
		ranges[idx] = 0.4

def pattern_front_wall(scan):
	make_the_wall(scan["ranges"], center_deg = 0, width_deg = 40)

def pattern_left_wall(scan):
	make_the_wall(scan["ranges"], center_deg = 90, width_deg = 30)

def pattern_right_wall(scan):
	make_the_wall(scan["ranges"], center_deg = 270, width_deg = 30)

def generate_single_scan(pattern_name):
	scan = create_empty_scan()
	if pattern_name == "front_wall":
		pattern_front_wall(scan)
	elif pattern_name == "left_wall":
		pattern_left_wall(scan)
	elif pattern_name == "right_wall":
		pattern_right_wall(scan)
	return scan

AVAILABLE_PATTERNS = ["front_wall", "left_wall", "right_wall"]

class LidarPublisher(Node):
	def __init__(self, delay_seconds, out_dir):
		super().__init__("lidar_mock_publisher")
		self.publisher_ = self.create_publisher(LaserScan, "scan", 10)
		self.timer = self.create_timer(delay_seconds, self.timer_callback)
		self.out_dir = out_dir
		self.index = 1
		os.makedirs(self.out_dir, exist_ok = True)
		self.get_logger().info("Lidar publisher node has been started.")

	def timer_callback(self):
		pattern_name = random.choice(AVAILABLE_PATTERNS)
		scan_data = generate_single_scan(pattern_name)
		scan_data["meta"] = {"pattern" : pattern_name, "index" : self.index}
		filename = os.path.join(self.out_dir, f"lds02_mock_{self.index:03d}.json")
		
		with open(filename, "w", encoding = "utf-8") as f:
			json.dump(scan_data, f, ensure_ascii = False, indent = 2)
		
		msg = LaserScan()

		msg.header.stamp = self.get_clock().now().to_msg()
		msg.header.frame_id = "laser_frame"

		msg.angle_min = float(scan_data["angle_min"])
		msg.angle_max = float(scan_data["angle_max"])
		msg.angle_increment = float(scan_data["angle_increment"])
		msg.time_increment = 0.0
		msg.scan_time = 0.0
		msg.range_min = float(scan_data["range_min"])
		msg.range_max = float(scan_data["range_max"])

		msg.ranges = [float(r) for r in scan_data["ranges"]]
		msg.intensities = [float(i) for i in scan_data["intensities"]]

		self.publisher_.publish(msg)

		self.get_logger().info(f"Published scan & saved {filename} (pattern: {pattern_name})")
		self.index += 1

if __name__ == "__main__":
	rp.init()

	lidar_node = LidarPublisher(delay_seconds = 2.0, out_dir = "lds02_dataset")

	try:
		rp.spin(lidar_node)
	except KeyboardInterrupt:
		lidar_node.get_logger().info("Keyboard Interrupt (SIGINT)")
	finally:
		lidar_node.destroy_node()
		rp.shutdown()