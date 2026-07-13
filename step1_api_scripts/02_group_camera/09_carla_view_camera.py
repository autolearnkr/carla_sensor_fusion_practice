#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
실습 09: 기존 카메라 센서 스캔 및 독립적 스트림 모니터링 (중급 - 그룹 A)

이 스크립트는 시뮬레이터 월드 내에 이미 부착되어 실행 중인 카메라 센서(08번 예제)를 탐색하여 찾아내고,
해당 센서 스트림을 구독(`listen`)하여 실시간 창으로 송출한 뒤, 종료 시 센서를 파괴하지 않고 
구독 리스너만 해제(`stop`) 처리하는 독립식 뷰어 기법을 실습합니다.
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

def process_image(image, dialog_name="CARLA CV Camera Stream"):
    """
    CARLA 카메라 데이터 수신 시 OpenCV로 변환 및 디스플레이 콜백
    """
    raw_data = np.frombuffer(image.raw_data, dtype=np.uint8)
    rgba_image = np.reshape(raw_data, (image.height, image.width, 4))
    bgr_image = rgba_image[:, :, :3]
    cv2.imshow(dialog_name, bgr_image)
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
        
        # 3. 비동기 리스너 바인딩
        print("Subscribing to camera data feed...")
        camera.listen(process_image)
        
        print("\nStreaming camera images to OpenCV Window.")
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
