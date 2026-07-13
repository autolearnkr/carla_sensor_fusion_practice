#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
실습 03: 차량 블루프린트 스폰 및 자원 소멸 제어 (초급)

이 스크립트는 차량 모델 Blueprint를 필터링하여 찾아내고,
맵의 유효한 Spawn Point를 획득하여 시뮬레이터 상에 안전하게 스폰하며,
종료 시 이를 정상 삭제(Clean up)하여 시뮬레이터 서버 메모리를 누수 없이 관리하는 법을 배웁니다.
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
        
        # 1. Blueprint 검색 필터링 (Dodge Charger 모델 탐색)
        vehicle_bp = blueprint_library.find('vehicle.dodge.charger_police_2020')
        
        if vehicle_bp.has_attribute('color'):
            color = random.choice(vehicle_bp.get_attribute('color').recommended_values)
            vehicle_bp.set_attribute('color', color)
            print(f"Selected vehicle color: {color}")
            
        # 2. 맵에서 사용 가능한 정식 스폰 포인트 목록 가져오기
        spawn_points = world.get_map().get_spawn_points()
        if not spawn_points:
            print("[Error] No spawn points found in this map.", file=sys.stderr)
            sys.exit(1)
            
        spawn_point = random.choice(spawn_points)
        print(f"Selected Spawn Point Location: {spawn_point.location}")

        # 3. 시뮬레이터 월드에 차량 생성
        print("Spawning Dodge Charger vehicle...")
        vehicle = world.spawn_actor(vehicle_bp, spawn_point)
        actor_list.append(vehicle)
        print(f"Vehicle spawned successfully! ID: {vehicle.id} | Type: {vehicle.type_id}")
        
        # 4. 스폰된 상태로 3초 동안 시뮬레이션 유지
        print("Waiting for 3 seconds...")
        time.sleep(3.0)

    except Exception as e:
        print(f"Failed to spawn actor: {e}", file=sys.stderr)
    finally:
        # 5. 자원 소멸 제어
        print("\nCleaning up actors in simulator...")
        for actor in actor_list:
            if actor.is_alive:
                actor.destroy()
                print(f"Actor ID {actor.id} has been destroyed.")
        print("Cleanup completed.")

if __name__ == '__main__':
    main()
