# 1. 실물 로봇 SLAM & NAVIGATION 구동 조건 
  * 사용할 ***LiDAR Package***가 구성 되어 있어야 함
  * ***SLAM Package***가 구성되어 있어야 함
  * 로봇의 ***URDF***가 정의되어 있어야 하며, 이를 통해 ***STATIC 및 DYNAMIC TF***가 발행되고 있어야 함
  * ***Odom Topic***이 구성되어 있어야 함
  * ***odom -> base_link***간의 ***dynamic tf***가 구성되어 있어야 함
  *  ***사용하는 모든 토픽의 timestamp가 동일해야함***
