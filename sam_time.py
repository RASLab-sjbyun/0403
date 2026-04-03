import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from nav_msgs.msg import Odometry

class ScanTimeSync(Node):
    def __init__(self):
        super().__init__('scan_time_sync')

        # /scan 구독
        self.scan_sub = self.create_subscription(
            LaserScan,
            '/scan_base',
            self.scan_callback,
            10)

        # /utlidar/robot_odom 구독
        self.odom_sub = self.create_subscription(
            Odometry,
            '/utlidar/robot_odom',
            self.odom_callback,
            10)

        # 재퍼블리시 /scan
        self.scan_pub = self.create_publisher(LaserScan, '/scan', 10)

        self.latest_odom_stamp = None

    def odom_callback(self, msg: Odometry):
        # 최신 odom timestamp 저장
        self.latest_odom_stamp = msg.header.stamp

    def scan_callback(self, msg: LaserScan):
        if self.latest_odom_stamp is None:
            self.get_logger().warn("No odom timestamp yet, skipping scan")
            return

        # 메시지 timestamp를 odom 기준으로 변경
        msg.header.stamp = self.latest_odom_stamp
        msg.header.frame_id = "velodyne"
        self.scan_pub.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = ScanTimeSync()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()

