#!/usr/bin/env python
#
# Copyright (c) 2019-2020 Intel Corporation
#
# This work is licensed under the terms of the MIT license.
# For a copy, see <https://opensource.org/licenses/MIT>.
"""
spawning objects (carla actors and pseudo_actors) in ROS

Gets config file from ros parameter objects_definition_file and spawns corresponding objects
through ROS service /carla/spawn_object.

Looks for an initial spawn point first in the launchfile, then in the config file, and
finally ask for a random one to the spawn service.
"""

import json
import math
import os
import sys

from transforms3d.euler import euler2quat

import rclpy
from rclpy.node import Node
from rclpy.task import Future

from carla_msgs.msg import CarlaActorList
from carla_msgs.srv import SpawnObject, DestroyObject
from diagnostic_msgs.msg import KeyValue
from geometry_msgs.msg import Pose


def wait_for_message(node, topic, msg_type, timeout=None):
    future = Future()
    sub = node.create_subscription(msg_type, topic, lambda msg: future.set_result(msg), 10)
    try:
        rclpy.spin_until_future_complete(node, future, timeout_sec=timeout)
    finally:
        node.destroy_subscription(sub)
    return future.result()


class CarlaSpawnObjects(Node):

    """
    Handles the spawning of the ego vehicle and its sensors
    """

    def __init__(self):
        super(CarlaSpawnObjects, self).__init__('carla_spawn_objects')

        self.declare_parameter('objects_definition_file', '')
        self.declare_parameter('spawn_sensors_only', False)

        self.objects_definition_file = self.get_parameter('objects_definition_file').value
        self.spawn_sensors_only = self.get_parameter('spawn_sensors_only').value

        self.players = []
        self.vehicles_sensors = []
        self.global_sensors = []

        self.spawn_object_service = self.create_client(SpawnObject, "/carla/spawn_object")
        self.destroy_object_service = self.create_client(DestroyObject, "/carla/destroy_object")

    def spawn_object(self, spawn_object_request):
        if not self.spawn_object_service.wait_for_service(timeout_sec=5.0):
            self.get_logger().error("Spawn service /carla/spawn_object not available!")
            return -1

        future = self.spawn_object_service.call_async(spawn_object_request)
        rclpy.spin_until_future_complete(self, future)
        response = future.result()
        if response is None:
            self.get_logger().error("Error calling spawn service")
            return -1
        
        response_id = response.id
        if response_id != -1:
            self.get_logger().info("Object (type='{}', id='{}') spawned successfully as {}.".format(
                spawn_object_request.type, spawn_object_request.id, response_id))
        else:
            self.get_logger().warn("Error while spawning object (type='{}', id='{}').".format(
                spawn_object_request.type, spawn_object_request.id))
            raise RuntimeError(response.error_string)
        return response_id

    def spawn_objects(self):
        """
        Spawns the objects
        """
        if not self.objects_definition_file or not os.path.exists(self.objects_definition_file):
            raise RuntimeError(
                "Could not read object definitions from {}".format(self.objects_definition_file))
        with open(self.objects_definition_file) as handle:
            json_actors = json.loads(handle.read())

        global_sensors = []
        vehicles = []
        found_sensor_actor_list = False

        for actor in json_actors["objects"]:
            actor_type = actor["type"].split('.')[0]
            if actor["type"] == "sensor.pseudo.actor_list" and self.spawn_sensors_only:
                global_sensors.append(actor)
                found_sensor_actor_list = True
            elif actor_type == "sensor":
                global_sensors.append(actor)
            elif actor_type == "vehicle" or actor_type == "walker":
                vehicles.append(actor)
            else:
                self.get_logger().warn(
                    "Object with type {} is not a vehicle, a walker or a sensor, ignoring".format(actor["type"]))
        if self.spawn_sensors_only is True and found_sensor_actor_list is False:
            raise RuntimeError("Parameter 'spawn_sensors_only' enabled, " +
                               "but 'sensor.pseudo.actor_list' is not instantiated, add it to your config file.")

        self.setup_sensors(global_sensors)

        if self.spawn_sensors_only is True:
            # get vehicle id from topic /carla/actor_list for all vehicles listed in config file
            actor_info_list = wait_for_message(self, "/carla/actor_list", CarlaActorList)
            if actor_info_list is not None:
                for vehicle in vehicles:
                    for actor_info in actor_info_list.actors:
                        if actor_info.type == vehicle["type"] and actor_info.rolename == vehicle["id"]:
                            vehicle["carla_id"] = actor_info.id

        self.setup_vehicles(vehicles)
        self.get_logger().info("All objects spawned.")

    def setup_vehicles(self, vehicles):
        for vehicle in vehicles:
            if self.spawn_sensors_only is True:
                # spawn sensors of already spawned vehicles
                try:
                    carla_id = vehicle["carla_id"]
                except KeyError:
                    self.get_logger().error(
                        "Could not spawn sensors of vehicle {}, its carla ID is not known.".format(vehicle["id"]))
                    break
                # spawn the vehicle's sensors
                self.setup_sensors(vehicle["sensors"], carla_id)
            else:
                spawn_object_request = SpawnObject.Request()
                spawn_object_request.type = vehicle["type"]
                spawn_object_request.id = vehicle["id"]
                spawn_object_request.attach_to = 0
                spawn_object_request.random_pose = False

                spawn_point = None

                # check if there's a spawn_point corresponding to this vehicle
                self.declare_parameter("spawn_point_" + vehicle["id"], '')
                spawn_point_param = self.get_parameter("spawn_point_" + vehicle["id"]).value
                spawn_param_used = False
                if spawn_point_param:
                    # try to use spawn_point from parameters
                    spawn_point = self.check_spawn_point_param(spawn_point_param)
                    if spawn_point is None:
                        self.get_logger().warn("{}: Could not use spawn point from parameters, ".format(vehicle["id"]) +
                                     "the spawn point from config file will be used.")
                    else:
                        self.get_logger().info("Spawn point from ros parameters")
                        spawn_param_used = True

                if "spawn_point" in vehicle and spawn_param_used is False:
                    # get spawn point from config file
                    try:
                        spawn_point = self.create_spawn_point(
                            vehicle["spawn_point"]["x"],
                            vehicle["spawn_point"]["y"],
                            vehicle["spawn_point"]["z"],
                            vehicle["spawn_point"]["roll"],
                            vehicle["spawn_point"]["pitch"],
                            vehicle["spawn_point"]["yaw"]
                        )
                        self.get_logger().info("Spawn point from configuration file")
                    except KeyError as e:
                        self.get_logger().error("{}: Could not use the spawn point from config file, ".format(vehicle["id"]) +
                                    "the mandatory attribute {} is missing, a random spawn point will be used".format(e))

                if spawn_point is None:
                    # pose not specified, ask for a random one in the service call
                    self.get_logger().info("Spawn point selected at random")
                    spawn_point = Pose()  # empty pose
                    spawn_object_request.random_pose = True

                player_spawned = False
                while not player_spawned and rclpy.ok():
                    spawn_object_request.transform = spawn_point

                    response_id = self.spawn_object(spawn_object_request)
                    if response_id != -1:
                        player_spawned = True
                        self.players.append(response_id)
                        # Set up the sensors
                        try:
                            self.setup_sensors(vehicle["sensors"], response_id)
                        except KeyError:
                            self.get_logger().warn(
                                "Object (type='{}', id='{}') has no 'sensors' field in his config file, none will be spawned.".format(spawn_object_request.type, spawn_object_request.id))

    def setup_sensors(self, sensors, attached_vehicle_id=None):
        """
        Create the sensors defined by the user and attach them to the vehicle
        """
        sensor_names = []
        for sensor_spec in sensors:
            if not rclpy.ok():
                break
            try:
                sensor_type = str(sensor_spec.pop("type"))
                sensor_id = str(sensor_spec.pop("id"))

                sensor_name = sensor_type + "/" + sensor_id
                if sensor_name in sensor_names:
                    raise NameError
                sensor_names.append(sensor_name)

                if attached_vehicle_id is None and "pseudo" not in sensor_type:
                    spawn_point = sensor_spec.pop("spawn_point")
                    sensor_transform = self.create_spawn_point(
                        spawn_point.pop("x"),
                        spawn_point.pop("y"),
                        spawn_point.pop("z"),
                        spawn_point.pop("roll", 0.0),
                        spawn_point.pop("pitch", 0.0),
                        spawn_point.pop("yaw", 0.0))
                else:
                    # if sensor attached to a vehicle, or is a 'pseudo_actor', allow default pose
                    spawn_point = sensor_spec.pop("spawn_point", 0)
                    if spawn_point == 0:
                        sensor_transform = self.create_spawn_point(0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
                    else:
                        sensor_transform = self.create_spawn_point(
                            spawn_point.pop("x", 0.0),
                            spawn_point.pop("y", 0.0),
                            spawn_point.pop("z", 0.0),
                            spawn_point.pop("roll", 0.0),
                            spawn_point.pop("pitch", 0.0),
                            spawn_point.pop("yaw", 0.0))

                spawn_object_request = SpawnObject.Request()
                spawn_object_request.type = sensor_type
                spawn_object_request.id = sensor_id
                spawn_object_request.attach_to = attached_vehicle_id if attached_vehicle_id is not None else 0
                spawn_object_request.transform = sensor_transform
                spawn_object_request.random_pose = False  # never set a random pose for a sensor

                attached_objects = []
                for attribute, value in list(sensor_spec.items()):
                    if attribute == "attached_objects":
                        for attached_object in sensor_spec["attached_objects"]:
                            attached_objects.append(attached_object)
                        continue
                    spawn_object_request.attributes.append(
                        KeyValue(key=str(attribute), value=str(value)))

                response_id = self.spawn_object(spawn_object_request)

                if response_id == -1:
                    raise RuntimeError("Error calling spawn service")

                if attached_objects:
                    # spawn the attached objects
                    self.setup_sensors(attached_objects, response_id)

                if attached_vehicle_id is None:
                    self.global_sensors.append(response_id)
                else:
                    self.vehicles_sensors.append(response_id)

            except KeyError as e:
                self.get_logger().error(
                    "Sensor {} will not be spawned, the mandatory attribute {} is missing".format(sensor_name, e))
                continue

            except RuntimeError as e:
                self.get_logger().error(
                    "Sensor {} will not be spawned: {}".format(sensor_name, e))
                continue

            except NameError:
                self.get_logger().error("Sensor rolename '{}' is only allowed to be used once. The second one will be ignored.".format(
                    sensor_id))
                continue

    def create_spawn_point(self, x, y, z, roll, pitch, yaw):
        spawn_point = Pose()
        spawn_point.position.x = x
        spawn_point.position.y = y
        spawn_point.position.z = z
        quat = euler2quat(math.radians(roll), math.radians(pitch), math.radians(yaw))

        spawn_point.orientation.w = quat[0]
        spawn_point.orientation.x = quat[1]
        spawn_point.orientation.y = quat[2]
        spawn_point.orientation.z = quat[3]
        return spawn_point

    def check_spawn_point_param(self, spawn_point_parameter):
        components = spawn_point_parameter.split(',')
        if len(components) != 6:
            self.get_logger().warn("Invalid spawnpoint '{}'".format(spawn_point_parameter))
            return None
        spawn_point = self.create_spawn_point(
            float(components[0]),
            float(components[1]),
            float(components[2]),
            float(components[3]),
            float(components[4]),
            float(components[5])
        )
        return spawn_point

    def destroy(self):
        """
        destroy all the players and sensors
        """
        self.get_logger().info("Destroying spawned objects...")
        try:
            # wait for service
            if not self.destroy_object_service.wait_for_service(timeout_sec=1.0):
                self.get_logger().warn("Destroy object service not available")
                return

            # destroy vehicles sensors
            for actor_id in self.vehicles_sensors:
                destroy_object_request = DestroyObject.Request()
                destroy_object_request.id = actor_id
                future = self.destroy_object_service.call_async(destroy_object_request)
                rclpy.spin_until_future_complete(self, future, timeout_sec=0.5)
                self.get_logger().info("Object {} successfully destroyed.".format(actor_id))
            self.vehicles_sensors = []

            # destroy global sensors
            for actor_id in self.global_sensors:
                destroy_object_request = DestroyObject.Request()
                destroy_object_request.id = actor_id
                future = self.destroy_object_service.call_async(destroy_object_request)
                rclpy.spin_until_future_complete(self, future, timeout_sec=0.5)
                self.get_logger().info("Object {} successfully destroyed.".format(actor_id))
            self.global_sensors = []

            # destroy player
            for player_id in self.players:
                destroy_object_request = DestroyObject.Request()
                destroy_object_request.id = player_id
                future = self.destroy_object_service.call_async(destroy_object_request)
                rclpy.spin_until_future_complete(self, future, timeout_sec=0.5)
                self.get_logger().info("Object {} successfully destroyed.".format(player_id))
            self.players = []
        except Exception as e:
            self.get_logger().warn(
                'Could not call destroy service on objects: {}'.format(e))


def main(args=None):
    rclpy.init(args=args)
    spawn_objects_node = None
    try:
        spawn_objects_node = CarlaSpawnObjects()
    except KeyboardInterrupt:
        print("Could not initialize CarlaSpawnObjects. Shutting down.", file=sys.stderr)
        rclpy.shutdown()
        return

    if spawn_objects_node:
        try:
            spawn_objects_node.spawn_objects()
            rclpy.spin(spawn_objects_node)
        except (KeyboardInterrupt, SystemExit):
            pass
        except RuntimeError as e:
            print("Exception caught: {}".format(e), file=sys.stderr)
        finally:
            spawn_objects_node.destroy()
            spawn_objects_node.destroy_node()
            rclpy.shutdown()


if __name__ == '__main__':
    main()
