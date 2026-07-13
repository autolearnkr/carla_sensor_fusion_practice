#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
실습 25: UDP 수신 바이트 스트림 모니터링, 수동 역직렬화 및 실시간 시각화 (고급)

이 스크립트는 루프백 소켓(127.0.0.1:5005)으로부터 패킷을 대기하다가:
1. 역직렬화하기 전에 수신된 원시 쌩 바이트 데이터(raw bytes)의 타입과 헥사(Hex) 값을 출력하여 통신의 이진 형태를 확인합니다.
2. 수신된 바이트 스트림을 순수 NumPy 조작만으로 역직렬화하여 회전 해상도(Height 160, Width 120, 3채널)를 가진 이미지로 복구합니다.
3. 복구된 BGR 이미지를 OpenCV 창에 시각화하여 최종 검증합니다.
"""

import sys
import socket
import numpy as np
import cv2

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_address = ('127.0.0.1', 5005)
    sock.bind(server_address)
    
    rotated_width = 120
    rotated_height = 160
    channels = 3
    expected_size = rotated_width * rotated_height * channels  # 57,600 Bytes
    
    print("====================================================================")
    print(f" UDP Socket Server Listening on 127.0.0.1:5005")
    print(f" Expected Packet Size: {expected_size} Bytes")
    print("====================================================================")
    print("Waiting for serialized image packets from '24_image_processor_node.py'...")
    
    frame_count = 0
    try:
        while True:
            data, address = sock.recvfrom(65535)
            frame_count += 1
            
            if frame_count % 20 == 0:
                print("\n-------------------------------------------------------------")
                print(" [Deserialization Step 1: Inspect Raw Bytes Before Parsing]")
                print("-------------------------------------------------------------")
                print(f"  - Received Data Type: {type(data)}")
                print(f"  - Received Data Size: {len(data)} Bytes")
                hex_dump = " ".join([f"{b:02x}" for b in data[:20]])
                print(f"  - Hex Dump (First 20 bytes): {hex_dump}")
                print(f"  - Raw Bytes Representation:   {data[:20]}")
                print("-------------------------------------------------------------")
                
            if len(data) != expected_size:
                if frame_count % 20 == 0:
                    print(f" -> [Warning] Packet size mismatch. Expected {expected_size}, got {len(data)}.")
                continue
                
            flat_array = np.frombuffer(data, dtype=np.uint8)
            bgr_image = flat_array.reshape((rotated_height, rotated_width, channels))
            
            cv2.imshow("UDP Socket Received & Deserialized Image (Rotated)", bgr_image)
            cv2.waitKey(1)
            
    except KeyboardInterrupt:
        print("\nStopping UDP socket viewer...")
    except Exception as e:
        print(f"Error occurred: {e}", file=sys.stderr)
    finally:
        sock.close()
        cv2.destroyAllWindows()
        print("Socket and windows closed. Exiting.")

if __name__ == '__main__':
    main()
