#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
실습 04: 트래픽 매니저(Traffic Manager) 및 차량 오토파일럿 (초급)

이 스크립트는 CARLA의 지능형 제어 서버인 Traffic Manager를 사용해 
차량에 자동 조향 및 가감속 운행(Autopilot) 기능을 부여하고 스스로 
도로 위를 주행하도록 활성화하는 방법을 배웁니다.
"""

import sys
import random
import time

try:
    import carla
except ImportError:
    print("Error: 'carla' python module is not installed. Please check your CARLA setup.", file=sys.stderr)
    sys.exit(1)

def main():
    print("Connecting to CARLA Server...")
    client = carla.Client('localhost', 2000)
    client.set_timeout(10.0)
    
    actor_list = []

    try:
        world = client.get_world()
        blueprint_library = world.get_blueprint_library()
        
        # 차량 스폰
        vehicle_bp = blueprint_library.find('vehicle.tesla.model3')
        spawn_points = world.get_map().get_spawn_points()
        spawn_point = random.choice(spawn_points)
        
        vehicle = world.spawn_actor(vehicle_bp, spawn_point)
        actor_list.append(vehicle)
        print(f"Vehicle spawned: {vehicle.type_id} | ID: {vehicle.id}")

        # 1. Traffic Manager(TM) 인스턴스 획득
        traffic_manager = client.get_trafficmanager(8000)
        traffic_manager.set_distance_to_leading_vehicle(vehicle, 3.0)
        
        # 2. 에고 차량 오토파일럿 활성화
        print("Enabling autopilot on the vehicle...")
        vehicle.set_autopilot(True, traffic_manager.get_port())
        
        # 3. 속도 모니터링
        print("Autopilot driving active. Monitoring for 5 seconds...")
        for i in range(5):
            v = vehicle.get_velocity()
            speed = 3.6 * (v.x**2 + v.y**2 + v.z**2)**0.5
            print(f" - Speed: {speed:.1f} km/h")
            time.sleep(1.0)

    except Exception as e:
        print(f"Error occurred: {e}", file=sys.stderr)
    finally:
        print("Cleaning up spawned vehicle...")
        for actor in actor_list:
            if actor.is_alive:
                actor.destroy()
        print("Cleanup done.")

if __name__ == '__main__':
    main()
