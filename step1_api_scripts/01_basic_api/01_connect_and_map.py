#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
실습 01: CARLA 시뮬레이터 연결 및 월드 정보 조회 (초급)

이 스크립트는 CARLA 클라이언트를 사용해 시뮬레이터 서버와 통신을 개설하고,
현재 활성화되어 있는 맵(Map) 정보 및 서버-클라이언트 API 버전을 조회하는 기초 예제입니다.
"""

import sys

try:
    import carla
except ImportError:
    print("Error: 'carla' python module is not installed. Please check your CARLA setup.", file=sys.stderr)
    sys.exit(1)

def main():
    # 1. CARLA 클라이언트 객체 생성 (기본값: localhost:2000)
    print("Connecting to CARLA Server on localhost:2000...")
    client = carla.Client('localhost', 2000)
    client.set_timeout(10.0)

    try:
        # 2. 서버와 클라이언트 버전 정보 로깅
        server_version = client.get_server_version()
        client_version = client.get_client_version()
        print(f"CARLA Server Version: {server_version}")
        print(f"CARLA Client Version: {client_version}")
        
        # 3. 월드 및 맵 이름 획득
        world = client.get_world()
        carla_map = world.get_map()
        print(f"Loaded Map name: {carla_map.name}")
        
        # 4. 사용 가능한 맵 목록 출력
        available_maps = client.get_available_maps()
        print("\nAvailable maps in the simulator:")
        for m in available_maps:
            print(f" - {m}")
            
    except Exception as e:
        print(f"Failed to connect or retrieve data: {e}", file=sys.stderr)

if __name__ == '__main__':
    main()
