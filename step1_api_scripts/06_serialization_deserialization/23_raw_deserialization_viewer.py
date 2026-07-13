#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
실습 23: 순수 메모리 연산을 이용한 원시 바이트 수동 역직렬화 및 시각화 (초급)

이 스크립트는 외부 변환 라이브러리(cv_bridge 등)를 전혀 사용하지 않고, 
CARLA 카메라로부터 수신한 raw_data(bytes) 1차원 이진 바이트 스트림 메모리를 
순수 NumPy 배열 조작(frombuffer 및 reshape)만을 통해 수동으로 역직렬화하여 
원래의 RGBA/BGR 이미지 행렬 구조로 복원하고 화면에 출력하는 방식을 배웁니다.
"""

import sys
import random
import time
import numpy as np
import cv2

try:
    import carla
except ImportError:
    print("Error: 'carla' python module is not installed. Please check your CARLA setup.", file=sys.stderr)
    sys.exit(1)

def manual_deserialization(raw_bytes, width, height):
    flat_array = np.frombuffer(raw_bytes, dtype=np.uint8)
    rgba_matrix = flat_array.reshape((height, width, 4))
    bgr_matrix = rgba_matrix[:, :, :3]
    return bgr_matrix

def main():
    actor_list = []
    print("Connecting to CARLA Server...")
    client = carla.Client('localhost', 2000)
    client.set_timeout(10.0)

    try:
        world = client.get_world()
        blueprint_library = world.get_blueprint_library()

        vehicle_bp = blueprint_library.find('vehicle.tesla.model3')
        spawn_point = random.choice(world.get_map().get_spawn_points())
        vehicle = world.spawn_actor(vehicle_bp, spawn_point)
        actor_list.append(vehicle)
        vehicle.set_autopilot(True)

        width, height = 640, 480
        camera_bp = blueprint_library.find('sensor.camera.rgb')
        camera_bp.set_attribute('image_size_x', str(width))
        camera_bp.set_attribute('image_size_y', str(height))
        camera_bp.set_attribute('fov', '90')
        camera = world.spawn_actor(camera_bp, carla.Transform(carla.Location(x=2.0, z=2.0)), attach_to=vehicle)
        actor_list.append(camera)

        def on_raw_data(image):
            binary_bytes = bytes(image.raw_data)
            bgr_img = manual_deserialization(binary_bytes, image.width, image.height)
            cv2.imshow("Manual Deserialized Image", bgr_img)
            cv2.waitKey(1)

        camera.listen(on_raw_data)
        print("\nSuccessfully listening to camera using manual deserialization.")
        print("Press Ctrl+C to exit and destroy actors.")
        
        while True:
            time.sleep(1.0)

    except KeyboardInterrupt:
        print("\nCancelled by user.")
    except Exception as e:
        print(f"Error occurred: {e}", file=sys.stderr)
    finally:
        print("Cleaning up actors...")
        for actor in actor_list:
            if actor.is_alive:
                actor.destroy()
        cv2.destroyAllWindows()
        print("Cleanup done.")

if __name__ == '__main__':
    main()
