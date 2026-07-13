#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
실습 16: 라이다 센서 스폰 및 점군 바이너리 파일 저장 (중급 - 단독형)

이 스크립트는 32채널 레이캐스트 라이다(Ray-cast LiDAR) 센서를 스폰하여 
차량에 장착하고, 포인트 클라우드 수집 성능 속성을 구성하여 
수신 데이터를 로컬 디렉터리에 raw 바이너리(.bin) 파일로 출력하는 실습입니다.
"""

import sys
import random
import time
import os

try:
    import carla
except ImportError:
    print("Error: 'carla' python module is not installed. Please check your CARLA setup.", file=sys.stderr)
    sys.exit(1)

def on_lidar_capture(point_cloud):
    raw_bytes = point_cloud.raw_data
    if point_cloud.frame % 10 == 0:
        output_path = f"saved_lidar/{point_cloud.frame:06d}.bin"
        with open(output_path, 'wb') as f:
            f.write(raw_bytes)
        print(f"Saved PointCloud: {output_path} | Total points: {len(point_cloud)}")

def main():
    print("Connecting to CARLA Server...")
    client = carla.Client('localhost', 2000)
    client.set_timeout(10.0)
    
    actor_list = []
    os.makedirs("saved_lidar", exist_ok=True)

    try:
        world = client.get_world()
        blueprint_library = world.get_blueprint_library()
        
        vehicle_bp = blueprint_library.find('vehicle.tesla.model3')
        spawn_point = random.choice(world.get_map().get_spawn_points())
        vehicle = world.spawn_actor(vehicle_bp, spawn_point)
        actor_list.append(vehicle)
        vehicle.set_autopilot(True)

        lidar_bp = blueprint_library.find('sensor.lidar.ray_cast')
        lidar_bp.set_attribute('channels', '32')
        lidar_bp.set_attribute('range', '50.0')
        lidar_bp.set_attribute('points_per_second', '300000')
        lidar_bp.set_attribute('rotation_frequency', '20.0')
        
        lidar_transform = carla.Transform(carla.Location(x=1.0, z=2.0))
        lidar = world.spawn_actor(lidar_bp, lidar_transform, attach_to=vehicle)
        actor_list.append(lidar)

        lidar.listen(on_lidar_capture)
        print("LiDAR collecting started. Saving bin files for 4 seconds...")
        time.sleep(4.0)
        
        lidar.stop()
        print("LiDAR collecting stopped.")

    except Exception as e:
        print(f"Error occurred: {e}", file=sys.stderr)
    finally:
        for actor in actor_list:
            if actor.is_alive:
                actor.destroy()
        print("Cleanup done.")

if __name__ == '__main__':
    main()
