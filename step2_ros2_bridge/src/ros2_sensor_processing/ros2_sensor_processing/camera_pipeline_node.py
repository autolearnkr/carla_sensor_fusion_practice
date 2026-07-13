#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ROS2 카메라 이미지 파이프라인 전처리 노드 (실습 2단계)

이 노드는 CARLA-ROS-Bridge가 발행하는 카메라 토픽을 구독하여:
1. cv_bridge를 사용해 ROS Image 메시지를 OpenCV Mat 형식으로 변환합니다.
2. Grayscale 변환 및 Canny Edge 검출 전처리를 가합니다.
3. 변환된 영상을 다시 ROS Image 메시지로 직렬화하여 퍼블리시합니다.
"""

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge, CvBridgeError
import cv2

class CameraPipelineNode(Node):
    def __init__(self):
        super().__init__('camera_pipeline_node')
        self.bridge = CvBridge()
        self.subscription = self.create_subscription(
            Image,
            '/carla/hero/camera/rgb/front/image_raw',
            self.image_callback,
            10
        )
        self.publisher = self.create_publisher(
            Image,
            '/processed/camera/image',
            10
        )
        self.get_logger().info('Camera Pipeline Node Started. Subscribed to /carla/hero/camera/rgb/front/image_raw')

    def image_callback(self, msg):
        try:
            cv_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
            gray_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
            edge_image = cv2.Canny(gray_image, threshold1=50, threshold2=150)
            
            processed_msg = self.bridge.cv2_to_imgmsg(edge_image, encoding='mono8')
            processed_msg.header = msg.header
            self.publisher.publish(processed_msg)
        except CvBridgeError as e:
            self.get_logger().error(f'CvBridge Error: {e}')

def main(args=None):
    rclpy.init(args=args)
    node = CameraPipelineNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('Shutting down camera pipeline node.')
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
