#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
실습 12: 기존 차량 검색 및 동적 라이다 스냅온 부착 (중급 - 그룹 B)

이 스크립트는 시뮬레이터 월드를 조회하여 이미 주행 중인 에고 차량(07번 예제)을 찾아내고,
해당 차량에 32채널 레이캐스트 라이다(LiDAR) 센서를 런타임에 동적으로 스냅온(Snap-on) 장착한 뒤
자원을 유지하는 멀티프로세스 센서 연동 실습입니다.
"""

import sys
import time

try:
    import carla
except ImportError:
    print("Error: 'carla' python module is not installed. Please check your CARLA setup.", file=sys.stderr)
    sys.exit(1)

def find_existing_vehicle(world):
    """
    현재 시뮬레이터 월드에 존재하는 활성 차량을 스캔하여 반환합니다.
    """
    actors = world.get_actors()
    for actor in actors:
        if 'vehicle' in actor.type_id:
            role_name = actor.attributes.get('role_name', '')
            if role_name == 'hero':
                return actor
    for actor in actors:
        if 'vehicle' in actor.type_id:
            return actor
    return None

def main():
    actor_list = []
    print("Connecting to CARLA Server on localhost:2000...")
    client = carla.Client('127.0.0.1', 2000)
    client.set_timeout(10.0)
    
    try:
        world = client.get_world()
        print("Searching for an existing vehicle in the simulator...")
        target_vehicle = find_existing_vehicle(world)
        
        if target_vehicle is None:
            print("\n[ERROR] No active vehicle found in the simulator!")
            print("Please run '07_spectator_follow.py' in Terminal 1 first to spawn a vehicle.")
            sys.exit(1)
            
        print(f"Target vehicle found! ID: {target_vehicle.id} | Type: {target_vehicle.type_id}")
        blueprint_library = world.get_blueprint_library()
        lidar_bp = blueprint_library.find('sensor.lidar.ray_cast')
        
        lidar_bp.set_attribute('channels', '32')
        lidar_bp.set_attribute('points_per_second', '300000')
        lidar_bp.set_attribute('rotation_frequency', '20.0')
        lidar_bp.set_attribute('range', '50.0')
        
        lidar_transform = carla.Transform(carla.Location(x=1.0, z=2.0))
        
        print(f"Dynamically attaching LiDAR sensor to Vehicle ID: {target_vehicle.id}...")
        lidar = world.spawn_actor(lidar_bp, lidar_transform, attach_to=target_vehicle)
        actor_list.append(lidar)
        print(f"LiDAR sensor attached successfully with ID: {lidar.id}")
        
        print("\nSensor holding active. Keep this script running to keep the LiDAR spawned.")
        print("Now you can run '13_carla_view_lidar.py' in Terminal 3 to watch the feed.")
        print("Press Ctrl+C to stop and remove the attached LiDAR sensor.")
        
        while True:
            time.sleep(1.0)
            
    except KeyboardInterrupt:
        print("\nDetaching LiDAR sensor.")
    except Exception as e:
        print(f"Error occurred: {e}", file=sys.stderr)
    finally:
        print("Cleaning up attached sensors...")
        for actor in actor_list:
            if actor.is_alive:
                actor.destroy()
        print("Sensor detached safely. Parent vehicle remains running in CARLA.")

if __name__ == '__main__':
    main()
