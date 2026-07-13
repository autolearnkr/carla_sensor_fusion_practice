#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ROS2 LiDAR CropBox & Downsample 필터링 C++ create_cloud 호환 노드 (실습 2단계)

이 노드는 create_cloud 헬퍼 함수를 사용하여 
XYZIRC 고정밀 포인트 클라우드 메시지를 자동 조립하여 퍼블리시합니다.
"""

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import PointCloud2, PointField
from sensor_msgs_py.point_cloud2 import create_cloud
import numpy as np

class LidarFilterCreateCloudNode(Node):
    def __init__(self):
        super().__init__('lidar_filter_create_cloud_node')
        
        self.subscription = self.create_subscription(
            PointCloud2,
            '/carla/hero/lidar',
            self.lidar_callback,
            10
        )
        self.publisher = self.create_publisher(
            PointCloud2,
            '/processed/lidar/points',
            10
        )
        self.get_logger().info('LiDAR Filter [create_cloud Mode] Started.')

    def lidar_callback(self, msg):
        # [A] 데이터 포맷 강제 검증 (XYZIRC 포맷 정합성 강제화)
        field_names = [f.name for f in msg.fields]
        if 'channel' not in field_names or 'return_type' not in field_names:
            self.get_logger().error(
                "====================================================================\n"
                "🚨 [FORMAT ERROR] Invalid LiDAR Topic Format Received!\n"
                f"Expected XYZIRC format, but received fields: {field_names}.\n"
                "Please configure CARLA ROS Bridge to run with 'lidar_xyzirc.py'!\n"
                "===================================================================="
            )
            return

        # [B] 역직렬화: PointCloud2 이진 데이터 ➔ Structured NumPy 배열 변환
        dtype = [
            ("x", "f4"),
            ("y", "f4"),
            ("z", "f4"),
            ("intensity", "u1"),
            ("return_type", "u1"),
            ("channel", "u2"),
        ]
        
        try:
            points = np.frombuffer(msg.data, dtype=dtype)
        except Exception as parse_err:
            self.get_logger().error(f"Failed to deserialize PointCloud2 data: {parse_err}")
            return
            
        num_points = len(points)
        if num_points == 0:
            return
        
        # [C] Crop Box Filter 적용 (ROI 전방 20m, 좌우 8m, 높이 -2m~2m)
        x = points["x"]
        y = points["y"]
        z = points["z"]
        
        x_mask = (x >= 0.0) & (x <= 20.0)
        y_mask = (y >= -8.0) & (y <= 8.0)
        z_mask = (z >= -2.0) & (z <= 2.0)
        
        roi_mask = x_mask & y_mask & z_mask
        points_cropped = points[roi_mask]
        
        # [D] Downsample Filter 적용 (3대1 그리드 데시메이션)
        skip_factor = 3
        points_downsampled = points_cropped[::skip_factor]
        
        # [E] create_cloud 헬퍼 함수를 사용해 자동 직렬화 및 퍼블리시
        fields = [
            PointField(name="x", offset=0, datatype=PointField.FLOAT32, count=1),
            PointField(name="y", offset=4, datatype=PointField.FLOAT32, count=1),
            PointField(name="z", offset=8, datatype=PointField.FLOAT32, count=1),
            PointField(name="intensity", offset=12, datatype=PointField.UINT8, count=1),
            PointField(name="return_type", offset=13, datatype=PointField.UINT8, count=1),
            PointField(name="channel", offset=14, datatype=PointField.UINT16, count=1),
        ]
        processed_msg = create_cloud(msg.header, fields, points_downsampled)
        self.publisher.publish(processed_msg)
        
        # 성능 로깅
        if msg.header.stamp.nanosec % 5 == 0:
            self.get_logger().info(
                f"Lidar Filter Stats [create_cloud] -> Original: {num_points} | Cropped: {len(points_cropped)} | Downsampled: {len(points_downsampled)}"
            )

def main(args=None):
    rclpy.init(args=args)
    node = LidarFilterCreateCloudNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('Shutting down lidar filter create_cloud node.')
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
