#!/usr/bin/env python
#
# Copyright (c) 2019-2020 Intel Corporation
#
# This work is licensed under the terms of the MIT license.
# For a copy, see <https://opensource.org/licenses/MIT>.
"""
Node to re-spawn vehicle in the ros-bridge

Subscribes to ROS topic /carla/<role_name>/init_pose and publishes the pose on /carla/<role_name>/set_transform

Uses ROS parameter: role_name

Whenever a pose is received via /carla/<role_name>init_pose, the vehicle gets respawned at that
position.

/carla/<role_name>/init_pose might be published via RVIZ '2D Pose Estimate" button.
"""

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseWithCovarianceStamped, Pose 


class SetInitialPose(Node):

    def __init__(self):
        super(SetInitialPose, self).__init__("set_initial_pose")

        self.declare_parameter("role_name", "hero")
        self.declare_parameter("control_id", "control")

        self.role_name = self.get_parameter("role_name").value
        self.control_id = self.get_parameter("control_id").value

        self.transform_publisher = self.create_publisher(
            Pose,
            "/carla/{}/{}/set_transform".format(self.role_name, self.control_id),
            10)

        self.initial_pose_subscriber = self.create_subscription(
            PoseWithCovarianceStamped,
            "/carla/{}/init_pose".format(self.role_name),
            self.intial_pose_callback,
            10)

    def intial_pose_callback(self, initial_pose):
        pose_to_publish = initial_pose.pose.pose
        pose_to_publish.position.z += 2.0
        self.transform_publisher.publish(pose_to_publish)


def main(args=None):
    rclpy.init(args=args)

    try:
        set_initial_pose_node = SetInitialPose()
        rclpy.spin(set_initial_pose_node)
    except KeyboardInterrupt:
        pass
    finally:
        rclpy.shutdown()

if __name__ == '__main__':
    main()
