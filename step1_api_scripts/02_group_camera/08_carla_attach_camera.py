#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
실습 08: 기존 차량 검색 및 동적 카메라 스냅온 부착 (중급 - 그룹 A)

이 스크립트는 시뮬레이터 월드를 조회하여 이미 주행 중인 에고 차량(07번 예제)을 찾아내고,
해당 차량에 1024x768 RGB 카메라 센서를 런타임에 동적으로 스냅온(Snap-on) 장착한 뒤
자원을 생존 유지하는 멀티프로세스 센서 연동 실습입니다.
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
    
    # 1. role_name이 'hero'인 에고 차량 우선 탐색
    for actor in actors:
        if 'vehicle' in actor.type_id:
            role_name = actor.attributes.get('role_name', '')
            if role_name == 'hero':
                return actor
                
    # 2. 예비 수단: 아무 일반 차량이나 식별
    for actor in actors:
        if 'vehicle' in actor.type_id:
            return actor
            
    return None

def main():
    actor_list = []
    
    # 1. CARLA 서버 연결
    print("Connecting to CARLA Server on localhost:2000...")
    client = carla.Client('127.0.0.1', 2000)
    client.set_timeout(10.0)
    
    try:
        world = client.get_world()
        
        # 2. 월드에서 실행 중인 차량 검색
        print("Searching for an existing vehicle in the simulator...")
        target_vehicle = find_existing_vehicle(world)
        
        if target_vehicle is None:
            print("\n[ERROR] No active vehicle found in the simulator!")
            print("Please run '07_spectator_follow.py' in Terminal 1 first to spawn a vehicle.")
            sys.exit(1)
            
        print(f"Target vehicle found! ID: {target_vehicle.id} | Type: {target_vehicle.type_id}")
        
        # 3. 카메라 블루프린트 생성 및 차량 부착
        blueprint_library = world.get_blueprint_library()
        camera_bp = blueprint_library.find('sensor.camera.rgb')
        camera_bp.set_attribute('image_size_x', '1024')
        camera_bp.set_attribute('image_size_y', '768')
        camera_bp.set_attribute('fov', '90')
        
        # 차량 앞유리 근처에 스폰 위치 설정
        camera_transform = carla.Transform(carla.Location(x=2.0, z=2.0))
        
        print(f"Dynamically attaching camera sensor to Vehicle ID: {target_vehicle.id}...")
        camera = world.spawn_actor(camera_bp, camera_transform, attach_to=target_vehicle)
        actor_list.append(camera)
        print(f"Camera sensor attached successfully with ID: {camera.id}")
        
        print("\nSensor holding active. Keep this script running to keep the camera spawned.")
        print("Now you can run '09_carla_view_camera.py' in Terminal 3 to watch the feed.")
        print("Press Ctrl+C to stop and remove the attached camera sensor.")
        
        # 스크립트 프로세스가 유지되는 동안 센서 객체가 생존함
        while True:
            time.sleep(1.0)
            
    except KeyboardInterrupt:
        print("\nDetaching camera sensor.")
    except Exception as e:
        print(f"Error occurred: {e}", file=sys.stderr)
    finally:
        # 4. 부착했던 센서만 파괴
        print("Cleaning up attached sensors...")
        for actor in actor_list:
            if actor.is_alive:
                actor.destroy()
        print("Sensor detached safely. Parent vehicle remains running in CARLA.")

if __name__ == '__main__':
    main()
