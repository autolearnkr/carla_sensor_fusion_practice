#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
실습 24: 수동 역직렬화 ➔ 이미지 90도 회전 ➔ 수동 재직렬화 ➔ UDP 소켓 전송 (고급)

이 스크립트는 CARLA 카메라로부터 160x120 해상도(대역폭 최적화) 영상을 받아와서:
1. raw_data(bytes) 바이트 스트림을 BGR 이미지로 수동 역직렬화합니다.
2. OpenCV를 이용해 시계방향 90도로 이미지 회전 처리를 가합니다.
3. 회전 완료된 이미지 행렬을 순수 1차원 이진 바이트 스트림(`tobytes()`)으로 수동 재직렬화합니다.
4. 직렬화된 57,600바이트의 패킷을 UDP 소켓 통신을 이용해 루프백 주소(127.0.0.1:5005)로 전송합니다.
"""

import sys
import random
import time
import socket
import numpy as np
import cv2

try:
    import carla
except ImportError:
    print("Error: 'carla' python module is not installed. Please check your CARLA setup.", file=sys.stderr)
    sys.exit(1)

def main():
    actor_list = []
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_address = ('127.0.0.1', 5005)
    
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

        width, height = 160, 120
        camera_bp = blueprint_library.find('sensor.camera.rgb')
        camera_bp.set_attribute('image_size_x', str(width))
        camera_bp.set_attribute('image_size_y', str(height))
        camera_bp.set_attribute('fov', '90')
        camera = world.spawn_actor(camera_bp, carla.Transform(carla.Location(x=2.0, z=2.0)), attach_to=vehicle)
        actor_list.append(camera)

        def on_camera_capture(image):
            flat_array = np.frombuffer(image.raw_data, dtype=np.uint8)
            rgba_image = flat_array.reshape((image.height, image.width, 4))
            bgr_image = rgba_image[:, :, :3]
            
            rotated_image = cv2.rotate(bgr_image, cv2.ROTATE_90_CLOCKWISE)
            serialized_bytes = rotated_image.tobytes()
            
            try:
                sock.sendto(serialized_bytes, server_address)
                if image.frame % 20 == 0:
                    print(f"Sent Serialized Packet: Frame {image.frame} | Size: {len(serialized_bytes)} Bytes ➔ UDP Loopback")
            except Exception as send_err:
                print(f"Send error: {send_err}", file=sys.stderr)

        camera.listen(on_camera_capture)
        print("\nImage processing node active. Capturing 160x120 raw images...")
        print("Now start '25_deserialization_socket_viewer.py' in a new terminal to receive and view.")
        print("Press Ctrl+C to stop.")
        
        while True:
            time.sleep(1.0)

    except KeyboardInterrupt:
        print("\nStopping image processor node...")
    except Exception as e:
        print(f"Error occurred: {e}", file=sys.stderr)
    finally:
        sock.close()
        print("Cleaning up spawned actors...")
        for actor in actor_list:
            if actor.is_alive:
                actor.destroy()
        print("Cleanup done.")

if __name__ == '__main__':
    main()
