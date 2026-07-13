#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
LiDAR processor using standard create_cloud helper (Structured Array mapping).
"""

import numpy
from carla_ros_bridge.sensor import Sensor, create_cloud
from sensor_msgs.msg import PointCloud2, PointField

class Lidar(Sensor):
    def __init__(self, uid, name, parent, relative_spawn_pose, node, carla_actor, synchronous_mode):
        super(Lidar, self).__init__(uid=uid,
                                    name=name,
                                    parent=parent,
                                    relative_spawn_pose=relative_spawn_pose,
                                    node=node,
                                    carla_actor=carla_actor,
                                    synchronous_mode=synchronous_mode)

        self.lidar_publisher = node.new_publisher(PointCloud2,
                                                  self.get_topic_prefix(),
                                                  qos_profile=10)
        self.listen()

    def destroy(self):
        super(Lidar, self).destroy()
        self.node.destroy_publisher(self.lidar_publisher)

    def sensor_data_updated(self, carla_lidar_measurement):
        """
        Transform using create_cloud and structured array.
        """
        header = self.get_msg_header(timestamp=carla_lidar_measurement.timestamp)
        fields = [
            PointField(name="x", offset=0, datatype=PointField.FLOAT32, count=1),
            PointField(name="y", offset=4, datatype=PointField.FLOAT32, count=1),
            PointField(name="z", offset=8, datatype=PointField.FLOAT32, count=1),
            PointField(name="intensity", offset=12, datatype=PointField.UINT8, count=1),
            PointField(name="return_type", offset=13, datatype=PointField.UINT8, count=1),
            PointField(name="channel", offset=14, datatype=PointField.UINT16, count=1),
        ]

        lidar_data = numpy.frombuffer(
            carla_lidar_measurement.raw_data, dtype=numpy.float32
        ).reshape(-1, 4)
        
        intensity = lidar_data[:, 3]
        intensity = (numpy.clip(intensity, 0, 1) * 255).astype(numpy.uint8).reshape(-1, 1)
        return_type = numpy.zeros((lidar_data.shape[0], 1), dtype=numpy.uint8)
        channel = numpy.empty((0, 1), dtype=numpy.uint16)

        try:
            num_channels = int(self.carla_actor.attributes.get("channels", 32))
        except Exception:
            num_channels = 32

        for i in range(num_channels):
            current_ring_points_count = carla_lidar_measurement.get_point_count(i)
            channel = numpy.vstack(
                (channel, numpy.full((current_ring_points_count, 1), i, dtype=numpy.uint16))
            )

        lidar_data = numpy.hstack((lidar_data[:, :3], intensity, return_type, channel))
        lidar_data[:, 1] *= -1

        dtype = [
            ("x", "f4"),
            ("y", "f4"),
            ("z", "f4"),
            ("intensity", "u1"),
            ("return_type", "u1"),
            ("channel", "u2"),
        ]

        # structured array 생성 및 매핑
        structured_lidar_data = numpy.zeros(lidar_data.shape[0], dtype=dtype)
        structured_lidar_data["x"] = lidar_data[:, 0]
        structured_lidar_data["y"] = lidar_data[:, 1]
        structured_lidar_data["z"] = lidar_data[:, 2]
        structured_lidar_data["intensity"] = lidar_data[:, 3].astype(numpy.uint8)
        structured_lidar_data["return_type"] = lidar_data[:, 4].astype(numpy.uint8)
        structured_lidar_data["channel"] = lidar_data[:, 5].astype(numpy.uint16)

        # [create_cloud 방식]
        point_cloud_msg = create_cloud(header, fields, structured_lidar_data)
        self.lidar_publisher.publish(point_cloud_msg)
