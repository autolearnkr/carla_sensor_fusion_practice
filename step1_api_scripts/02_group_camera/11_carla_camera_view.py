#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
실습 11: 통합 카메라 뷰어 및 OpenCV 연동 (중급 - 단독형)

이 스크립트는 단일 스크립트 내에서 차량 스폰, 카메라 센서 장착, 
그리고 listen 콜백을 통한 이미지 raw_data를 실시간으로 OpenCV BGR 3채널 이미지로 
역직렬화하여 `cv2.imshow` 창에 비디오 스트림 형태로 송출하고 종료 시 정리하는 과정을 배옵니다.
"""

import sys
import time
import numpy as np
import cv2

try:
    import carla
except ImportError:
    print("Error: 'carla' python module is not installed. Please check your CARLA setup.", file=sys.stderr)
    sys.exit(1)

def process_image(image, dialog_name="CARLA Camera View"):
    """
    CARLA raw 카메라 데이터를 받아 실시간 OpenCV 창으로 렌더링하는 콜백 함수
    """
    raw_data = np.frombuffer(image.raw_data, dtype=np.uint8)
    rgba_image = np.reshape(raw_data, (image.height, image.width, 4))
    bgr_image = rgba_image[:, :, :3]
    cv2.imshow(dialog_name, bgr_image)
    cv2.waitKey(1)

def main():
    actor_list = []
    
    # 1. CARLA 서버 연결
    print("Connecting to CARLA Server on localhost:2000...")
    client = carla.Client('127.0.0.1', 2000)
    client.set_timeout(10.0)
    
    try:
        world = client.get_world()
        blueprint_library = world.get_blueprint_library()
        
        # 2. 에고 차량 스폰
        vehicle_bp = blueprint_library.find('vehicle.dodge.charger_police_2020')
        spawn_points = world.get_map().get_spawn_points()
        spawn_point = spawn_points[0] if spawn_points else carla.Transform()
        
        print("Spawning vehicle...")
        vehicle = world.spawn_actor(vehicle_bp, spawn_point)
        actor_list.append(vehicle)
        print(f"Vehicle spawned successfully with ID: {vehicle.id}")
        
        vehicle.set_autopilot(True)
        
        # 3. RGB 카메라 스폰 및 부착
        camera_bp = blueprint_library.find('sensor.camera.rgb')
        camera_bp.set_attribute('image_size_x', '1024')
        camera_bp.set_attribute('image_size_y', '768')
        camera_bp.set_attribute('fov', '90')
        
        camera_transform = carla.Transform(carla.Location(x=2.0, z=2.0))
        camera = world.spawn_actor(camera_bp, camera_transform, attach_to=vehicle)
        actor_list.append(camera)
        
        # 4. 리스너 콜백 연동
        camera.listen(process_image)
        print("Camera view is active. Press Ctrl+C in terminal to exit.")
        
        while True:
            time.sleep(1.0)
            
    except KeyboardInterrupt:
        print("\nCancelled by user.")
    except Exception as e:
        print(f"Error occurred: {e}", file=sys.stderr)
    finally:
        print("Cleaning up spawned actors...")
        for actor in actor_list:
            if actor.is_alive:
                actor.destroy()
        cv2.destroyAllWindows()
        print("Cleanup completed. Exiting.")

if __name__ == '__main__':
    main()
