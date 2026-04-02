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
