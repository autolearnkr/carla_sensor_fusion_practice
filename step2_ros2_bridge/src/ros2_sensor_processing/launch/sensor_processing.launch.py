#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ROS2 센서 전처리 파이프라인 통합 구동 런치 파일

이 런치 스크립트는 RGB 카메라 Canny Edge 전처리 노드와 
LiDAR CropBox + Downsample 필터 노드를 일괄 실행해 줍니다.
학생들은 아래 Lidar 필터 노드 2종 중 원하는 모드 1개만 주석을 해제하여 구동합니다.
"""

from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        # 1. 카메라 이미지 Canny Edge 전처리 노드 구동
        Node(
            package='ros2_sensor_processing',
            executable='camera_pipeline_node',
            name='camera_pipeline_node',
            output='screen'
        ),
        
        # 2. [대안 A: 기본형] LiDAR create_cloud 적용 전처리 노드 구동
        Node(
            package='ros2_sensor_processing',
            executable='lidar_filter_create_cloud_node',
            name='lidar_filter_node',
            output='screen'
        ),
        
        # 3. [대안 B: 수동형] LiDAR tobytes() 수동 직렬화 적용 전처리 노드 구동
        # (원하는 경우 대안 A 노드 블록을 주석 처리하고, 아래 대안 B 노드 블록의 주석을 풀어서 기동합니다.)
        # Node(
        #     package='ros2_sensor_processing',
        #     executable='lidar_filter_tobyte_node',
        #     name='lidar_filter_node',
        #     output='screen'
        # )
    ])
