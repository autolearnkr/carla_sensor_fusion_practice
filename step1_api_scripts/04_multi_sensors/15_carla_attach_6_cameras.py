#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
실습 15: 6방향 서라운드 뷰 카메라 다중 장착 및 role_name 설정 (중급)

이 스크립트는 시뮬레이션 환경 내의 차량에 6개 방향의 카메라 센서를 다중 장착하되, 
ROS 2 통신 시 각 카메라가 독립된 토픽 이름을 생성하도록 
고유의 `role_name` 속성값을 주입하여 스폰하는 방법을 배웁니다.
"""

import sys
import time

try:
    import carla
except ImportError:
    print("Error: 'carla' python module is not installed. Please check your CARLA setup.", file=sys.stderr)
    sys.exit(1)

def find_existing_vehicle(world):
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
        print("Searching for target vehicle in the simulator...")
        target_vehicle = find_existing_vehicle(world)
        
        if target_vehicle is None:
            print("\n[ERROR] No active vehicle found in the simulator!")
            print("Please run '07_spectator_follow.py' in Terminal 1 first.")
            sys.exit(1)
            
        print(f"Target vehicle found! ID: {target_vehicle.id}")
        blueprint_library = world.get_blueprint_library()
        
        camera_configs = [
            (carla.Location(x=2.0, z=2.0), carla.Rotation(yaw=0.0), 'front'),
            (carla.Location(x=1.8, y=-0.5, z=2.0), carla.Rotation(yaw=-45.0), 'front_left'),
            (carla.Location(x=1.8, y=0.5, z=2.0), carla.Rotation(yaw=45.0), 'front_right'),
            (carla.Location(x=-2.0, z=2.0), carla.Rotation(yaw=180.0), 'rear'),
            (carla.Location(x=-1.8, y=-0.5, z=2.0), carla.Rotation(yaw=-135.0), 'rear_left'),
            (carla.Location(x=-1.8, y=0.5, z=2.0), carla.Rotation(yaw=135.0), 'rear_right'),
        ]
        
        print("\nSpawning and attaching 6 surround-view cameras...")
        for loc, rot, tag in camera_configs:
            bp = blueprint_library.find('sensor.camera.rgb')
            bp.set_attribute('role_name', f'camera_{tag}')
            bp.set_attribute('image_size_x', '800')
            bp.set_attribute('image_size_y', '600')
            bp.set_attribute('fov', '90')
            
            transform = carla.Transform(loc, rot)
            camera = world.spawn_actor(bp, transform, attach_to=target_vehicle)
            actor_list.append(camera)
            print(f"-> Attached camera [{tag}] with ID: {camera.id}")
            
        print("\nAll 6 cameras are successfully mounted to the vehicle!")
        print("Press Ctrl+C to stop and remove all 6 camera sensors.")
        
        while True:
            time.sleep(1.0)
            
    except KeyboardInterrupt:
        print("\nDetaching all 6 cameras...")
    except Exception as e:
        print(f"Error occurred: {e}", file=sys.stderr)
    finally:
        print("Cleaning up attached sensors...")
        for actor in actor_list:
            if actor.is_alive:
                actor.destroy()
        print("All 6 sensors detached safely. Vehicle remains in CARLA.")

if __name__ == '__main__':
    main()
