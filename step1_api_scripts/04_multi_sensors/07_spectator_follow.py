#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
실습 07: 관찰자(Spectator)의 실시간 차량 추적 (초급 - 공유 구동 노드)

이 스크립트는 차량을 스폰하여 오토파일럿으로 주행시키고, 
시뮬레이터의 관찰자(Spectator) 카메라가 실시간 20Hz 루프 내에서 
차량의 진행 방향 후방에 정렬되어 추적하도록 3D 공간 제어를 구현하는 실습입니다.
이 프로세스를 백그라운드 터미널에 켜두고 다른 센서 동적 부착 예제들을 테스트합니다.
"""

import sys
import time

try:
    import carla
except ImportError:
    print("Error: 'carla' python module is not installed. Please check your Carla setup.", file=sys.stderr)
    sys.exit(1)

def main():
    actor_list = []
    print("Connecting to CARLA Server on localhost:2000...")
    client = carla.Client('127.0.0.1', 2000)
    client.set_timeout(10.0)
    
    try:
        world = client.get_world()
        blueprint_library = world.get_blueprint_library()
        
        # 2. 에고 차량 스폰
        vehicle_bp = blueprint_library.find('vehicle.dodge.charger_police_2020')
        vehicle_bp.set_attribute('role_name', 'hero')
        
        spawn_points = world.get_map().get_spawn_points()
        spawn_point = spawn_points[0] if spawn_points else carla.Transform()
        
        print("Spawning vehicle in CARLA...")
        vehicle = world.spawn_actor(vehicle_bp, spawn_point)
        actor_list.append(vehicle)
        print(f"Vehicle spawned successfully with ID: {vehicle.id}")
        
        print("Enabling autopilot on the vehicle...")
        vehicle.set_autopilot(True)
        
        # 3. Spectator 뷰 차량 3인칭 추적
        spectator = world.get_spectator()
        print("Aligning CARLA Spectator view to follow the vehicle...")
        print("Press Ctrl+C in terminal to exit and destroy the vehicle.")
        
        while True:
            time.sleep(0.05)
            vehicle_transform = vehicle.get_transform()
            vehicle_loc = vehicle_transform.location
            vehicle_rot = vehicle_transform.rotation
            
            forward_vector = vehicle_transform.get_forward_vector()
            spectator_loc = vehicle_loc - (forward_vector * 5.0) + carla.Location(z=2.5)
            
            spectator_transform = carla.Transform(spectator_loc, carla.Rotation(pitch=-15.0, yaw=vehicle_rot.yaw))
            spectator.set_transform(spectator_transform)
            
    except KeyboardInterrupt:
        print("\nCancelled by user.")
    except Exception as e:
        print(f"Error occurred: {e}", file=sys.stderr)
    finally:
        print("Cleaning up spawned actors...")
        for actor in actor_list:
            if actor.is_alive:
                actor.destroy()
        print("Cleanup completed. Exiting.")

if __name__ == '__main__':
    main()
