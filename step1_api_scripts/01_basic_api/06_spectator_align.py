#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
실습 06: 시뮬레이터 관찰자(Spectator) 뷰 정렬 (초급)

이 스크립트는 시뮬레이션 환경 내에서 사용자 화면에 해당하는 
스펙테이터(Spectator) 카메라를 조작하는 방법을 학습합니다. 
특정 차량이나 랜드마크 위치로 카메라를 정렬하는 3차원 월드 제어의 기초입니다.
"""

import sys
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

    try:
        world = client.get_world()
        spectator = world.get_spectator()
        
        # 현재 Spectator의 위치와 각도 로깅
        current_transform = spectator.get_transform()
        print(f"Current Spectator Location: {current_transform.location}")
        print(f"Current Spectator Rotation: {current_transform.rotation}")

        # 0번째 위치로 Spectator 이동
        spawn_points = world.get_map().get_spawn_points()
        if spawn_points:
            target_spawn_point = spawn_points[0]
            print(f"\nMoving Spectator to Spawn Point 0: {target_spawn_point.location}")
            
            camera_location = target_spawn_point.location + carla.Location(z=5.0)
            camera_rotation = carla.Rotation(pitch=-30.0, yaw=target_spawn_point.rotation.yaw, roll=0.0)
            
            new_transform = carla.Transform(camera_location, camera_rotation)
            spectator.set_transform(new_transform)
            
            time.sleep(3.0)
            print("Spectator alignment completed.")
        else:
            print("[Warning] No spawn points available on the map.")

    except Exception as e:
        print(f"Error occurred: {e}", file=sys.stderr)

if __name__ == '__main__':
    main()
