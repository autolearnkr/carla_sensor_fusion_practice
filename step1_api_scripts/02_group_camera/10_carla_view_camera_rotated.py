#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
실습 10: 기존 카메라 데이터 수신 및 OpenCV 90도 회전 출력 (중급 - 그룹 A)

이 스크립트는 시뮬레이터 월드 내에 이미 부착되어 실행 중인 카메라 센서(08번 예제)를 탐색하여 찾아내고,
해당 센서 스트림을 구독(`listen`)하여 이미지 데이터를 수집한 뒤
OpenCV 회전 API(`cv2.rotate`)를 적용해 시계방향으로 90도 회전한 영상을 화면에 렌더링하는 기법을 실습합니다.
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

def process_image_rotated(image, dialog_name="CARLA CV Camera Stream (Rotated 90 Deg)"):
    """
    CARLA 카메라 데이터 수신 시 OpenCV로 변환하고 90도 회전하여 출력하는 콜백
    """
    # 1. 1차원 바이트 스트림을 uint8 NumPy 배열로 변환
    raw_data = np.frombuffer(image.raw_data, dtype=np.uint8)
    
    # 2. 고정 해상도로 2차원 재구성 (RGBA)
    rgba_image = np.reshape(raw_data, (image.height, image.width, 4))
    
    # 3. BGR 3채널 슬라이싱
    bgr_image = rgba_image[:, :, :3]
    
    # 4. OpenCV 이미지 90도 시계방향 회전 연산 적용 (ROTATE_90_CLOCKWISE)
    rotated_image = cv2.rotate(bgr_image, cv2.ROTATE_90_CLOCKWISE)
    
    # 5. 회전된 이미지 화면 출력
    cv2.imshow(dialog_name, rotated_image)
    cv2.waitKey(1)

def find_existing_camera(world):
    """
    시뮬레이터 월드 상의 모든 액터 중 첫 번째 RGB 카메라 센서를 찾습니다.
    """
    actors = world.get_actors()
    for actor in actors:
        if 'sensor.camera.rgb' in actor.type_id:
            return actor
    return None

def main():
    # 1. CARLA 서버 연결
    print("Connecting to CARLA Server on localhost:2000...")
    client = carla.Client('127.0.0.1', 2000)
    client.set_timeout(10.0)
    
    camera = None
    try:
        world = client.get_world()
        
        # 2. 기존 카메라 센서 탐색
        print("Searching for an active RGB camera sensor in the simulator...")
        camera = find_existing_camera(world)
        
        if camera is None:
            print("\n[ERROR] No active RGB camera sensor found in the simulator!")
            print("Please make sure '08_carla_attach_camera.py' is running in Terminal 2.")
            sys.exit(1)
            
        print(f"Active camera found! Sensor ID: {camera.id} (Attached to Parent Vehicle ID: {camera.parent.id if camera.parent else 'None'})")
        
        # 3. 비동기 리스너 바인딩 (90도 회전 콜백)
        print("Subscribing to camera data feed...")
        camera.listen(process_image_rotated)
        
        print("\nStreaming 90-degree rotated camera images to OpenCV Window.")
        print("Press Ctrl+C to stop listening and close window.")
        
        while True:
            time.sleep(1.0)
            
    except KeyboardInterrupt:
        print("\nStopping camera stream subscription...")
    except Exception as e:
        print(f"Error occurred: {e}", file=sys.stderr)
    finally:
        # 4. 리스너 해제
        if camera is not None and camera.is_listening:
            camera.stop()
        cv2.destroyAllWindows()
        print("Stream closed. Camera sensor remains attached in CARLA.")

if __name__ == '__main__':
    main()
