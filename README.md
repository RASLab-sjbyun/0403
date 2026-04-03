# 1. 실물 로봇 SLAM & NAVIGATION 구동 조건 
  * 사용할 ***LiDAR Package***가 구성 되어 있어야 함
  * ***SLAM Package***가 구성되어 있어야 함
  * 로봇의 ***URDF***가 정의되어 있어야 하며, 이를 통해 ***STATIC 및 DYNAMIC TF***가 발행되고 있어야 함
  * ***Odom Topic***이 구성되어 있어야 함
  * ***odom -> base_link***간의 ***dynamic tf***가 구성되어 있어야 함
  *  ***사용하는 모든 토픽의 timestamp가 동일해야함***

# 2. LiDAR Package
## 2.1. install
  ```bash
  sudo apt-get install ros-humble-velodyne
  mkdir -p ~/<your_ws>/src
  git clone https://github.com/ros-drivers/velodyne.git
  cd ..
  source /opt/ros/humble/setup.bash
  rosdep install --from-paths src --ignore-src --rosdistro humble –y –r
  colcon build
  ros2 launch velodyne-all-nodes-VLP16-launch.py
  ```
## 2.2. connection check
  ```bash
  sudo apt install wireshark
  sudo wireshark
  ```
## 2.3. params modify  
  ```bash
  cd ~/<your_Ws>/src/velodyne/velodyne_driver/config
  gedit VLP16-velodyne_driver_node-params.yam
  ```
## 2.4. build and run
  ```bash
  source /opt/ros/humble/setup.bash
  cd ~/<your_Ws>/
  colcon build
  source install/setup.bash
  ros2 launch velodyne velodyne-all-nodes-VLP16-launch.py
  ```
# 3. Navigation and SLAM PACKAGE 
## 3.1 install
  ```bash
  sudo apt install ros-humble-bondcpp
  sudo apt install libsuitesparse-dev
  sudo apt install ros-humble-navigation2
  sudo apt install ros-humble-nav2-bringup
  ```
  ```bash
  cd ~/<your_ws>/src/
  git clone -b humble https://github.com/SteveMacenski/slam_toolbox.git
  cd ~/<your_ws>
  colcon build
  ```
# 4. URDF and Laumch 
## 4.1 URDF modify 
  * revolute -> fix
  * add lidar
  * base -> base_link rename
  * add base_footpirnt
  * add joint(base_link <->base_footprint)

# 5. odom topic publisehr 
## 5.1 odom data sub and pub (sub: '/utlidar/robot_odom', child_frame_id: 'base_link')
```bash
lab@lab:~$ ros2 interface show nav_msgs/msg/Odometry 
# This represents an estimate of a position and velocity in free space.
# The pose in this message should be specified in the coordinate frame given by header.frame_id
# The twist in this message should be specified in the coordinate frame given by the child_frame_id

# Includes the frame id of the pose parent.
std_msgs/Header header
	builtin_interfaces/Time stamp
		int32 sec
		uint32 nanosec
	string frame_id

# Frame id the pose points to. The twist is in this coordinate frame.
string child_frame_id

# Estimated pose that is typically relative to a fixed world frame.
geometry_msgs/PoseWithCovariance pose
	Pose pose
		Point position
			float64 x
			float64 y
			float64 z
		Quaternion orientation
			float64 x 0
			float64 y 0
			float64 z 0
			float64 w 1
	float64[36] covariance

# Estimated linear and angular velocity relative to child_frame_id.
geometry_msgs/TwistWithCovariance twist
	Twist twist
		Vector3  linear
			float64 x
			float64 y
			float64 z
		Vector3  angular
			float64 x
			float64 y
			float64 z
	float64[36] covariance
```
# 6 TF publish
```
lab@lab:~$ ros2 interface show geometry_msgs/msg/TransformStamped 
# This expresses a transform from coordinate frame header.frame_id
# to the coordinate frame child_frame_id at the time of header.stamp
#
# This message is mostly used by the
# <a href="https://index.ros.org/p/tf2/">tf2</a> package.
# See its documentation for more information.
#
# The child_frame_id is necessary in addition to the frame_id
# in the Header to communicate the full reference for the transform
# in a self contained message.

# The frame id in the header is used as the reference frame of this transform.
std_msgs/Header header
	builtin_interfaces/Time stamp
		int32 sec
		uint32 nanosec
	string frame_id

# The frame id of the child frame to which this transform points.
string child_frame_id

# Translation and rotation in 3-dimensions of child_frame_id from header.frame_id.
Transform transform
	Vector3 translation
		float64 x
		float64 y
		float64 z
	Quaternion rotation
		float64 x 0
		float64 y 0
		float64 z 0
		float64 w 1
```
* TF broad caster 생성
```python
from geometry_msgs.msg import TransformStamped
from tf2_ros import TransformBroadcaster

self.tf_broadcaster = TransformBroadcaster(self)
self.tf_broadcaster.sendTransform(<msg>)
```

# 7 lidar time synchronization
## 7.1. topic name chaneg
  * 현재 velodyne에서 발행하고 있는 scan 토픽을 scan_base라는 이름으로 발행되도록 변경
  * scan <- scan_base <- go2 시간 연동 

```pyhton
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
```
