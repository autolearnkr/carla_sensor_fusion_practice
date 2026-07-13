#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
실습 05: VehicleControl을 이용한 차량 물리 제어 (초급)

이 스크립트는 자율주행 알고리즘의 최하단에 해당하는 차량 제어 인터페이스인
VehicleControl API를 활용하여, 기어 변속(전진/후진), 엑셀 조작(throttle), 
조향(steer), 그리고 제동(brake)을 파이썬 코드로 직접 주입하는 기초 실습입니다.
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

        # 1. 전진 제어
        print("\nStep 1: Accelerating Forward (throttle=0.5)...")
        control = carla.VehicleControl(throttle=0.5, steer=0.0, brake=0.0, reverse=False)
        vehicle.apply_control(control)
        time.sleep(2.0)

        # 2. 제동 제어
        print("\nStep 2: Applying Brake (brake=1.0)...")
        control = carla.VehicleControl(throttle=0.0, steer=0.0, brake=1.0, reverse=False)
        vehicle.apply_control(control)
        time.sleep(1.5)

        # 3. 우회전 전진 제어
        print("\nStep 3: Turning Right while driving (steer=0.5)...")
        control = carla.VehicleControl(throttle=0.3, steer=0.5, brake=0.0, reverse=False)
        vehicle.apply_control(control)
        time.sleep(2.0)

        # 4. 정지 및 후진 변속 제어
        print("\nStep 4: Stopping and Shifting Gear to Reverse...")
        control = carla.VehicleControl(throttle=0.0, steer=0.0, brake=1.0, hand_brake=True)
        vehicle.apply_control(control)
        time.sleep(1.0)
        
        print("Driving backward (reverse=True)...")
        control = carla.VehicleControl(throttle=0.4, steer=0.0, brake=0.0, reverse=True)
        vehicle.apply_control(control)
        time.sleep(2.0)

        # 5. 최종 핸드브레이크 주차 제어
        print("\nStep 5: Applying Handbrake Parking...")
        control = carla.VehicleControl(throttle=0.0, steer=0.0, brake=0.0, hand_brake=True)
        vehicle.apply_control(control)
        time.sleep(1.0)

    except Exception as e:
        print(f"Error occurred: {e}", file=sys.stderr)
    finally:
        print("Cleaning up vehicle...")
        for actor in actor_list:
            if actor.is_alive:
                actor.destroy()
        print("Cleanup done.")

if __name__ == '__main__':
    main()
