#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
실습 20: 동기식 모드(Synchronous Mode) 센서 데이터 프레임 동기화 (고급)

이 스크립트는 시뮬레이터를 동기식 모드로 강제 제어하고 고정 타임스텝(20Hz)을 설정한 뒤,
카메라와 라이다 센서 데이터를 동일 시뮬레이션 타임스탬프(프레임 번호) 기준으로 
안전하게 수집하고 정합하기 위한 동기식 큐(Synchronous Queue) 메커니즘을 학습합니다.
"""

import sys
import queue
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

    sensor_queue = queue.Queue()
    world = client.get_world()
    original_settings = world.get_settings()

    try:
        settings = world.get_settings()
        settings.synchronous_mode = True
        settings.fixed_delta_seconds = 0.05
        world.apply_settings(settings)
        print("Synchronous mode enabled.")

        blueprint_library = world.get_blueprint_library()
        vehicle_bp = blueprint_library.find('vehicle.tesla.model3')
        spawn_point = world.get_map().get_spawn_points()[0]
        vehicle = world.spawn_actor(vehicle_bp, spawn_point)
        vehicle.set_autopilot(True)

        camera_bp = blueprint_library.find('sensor.camera.rgb')
        camera = world.spawn_actor(camera_bp, carla.Transform(carla.Location(x=2.0, z=2.0)), attach_to=vehicle)

        lidar_bp = blueprint_library.find('sensor.lidar.ray_cast')
        lidar = world.spawn_actor(lidar_bp, carla.Transform(carla.Location(x=1.0, z=2.0)), attach_to=vehicle)

        camera.listen(lambda image: sensor_queue.put((image.frame, 'camera', image)))
        lidar.listen(lambda point_cloud: sensor_queue.put((point_cloud.frame, 'lidar', point_cloud)))
        
        print("\nStart frame synchronization loop for 30 ticks...")

        for step in range(30):
            world_frame = world.tick()
            data_dict = {}
            
            while len(data_dict) < 2:
                try:
                    s_frame, s_name, s_data = sensor_queue.get(timeout=1.0)
                    if s_frame == world_frame:
                        data_dict[s_name] = s_data
                except queue.Empty:
                    print(f" -> [Warning] Frame {world_frame}: Sensor data packet delayed...")
                    break
            
            if 'camera' in data_dict and 'lidar' in data_dict:
                cam = data_dict['camera']
                lid = data_dict['lidar']
                print(f"Tick {step:02d} | Frame {world_frame} -> Synchronized! Camera: {cam.width}x{cam.height} | LiDAR Points: {len(lid)}")
            else:
                print(f"Tick {step:02d} | Frame {world_frame} -> [Failed] Failed to match sensor data.")
                
            time.sleep(0.02)

    except Exception as e:
        print(f"Error occurred: {e}", file=sys.stderr)
    finally:
        print("\nRestoring original world settings...")
        world.apply_settings(original_settings)
        print("Cleaning up spawned actors...")
        if camera is not None: camera.destroy()
        if lidar is not None: lidar.destroy()
        if vehicle is not None: vehicle.destroy()
        print("Cleanup done.")

if __name__ == '__main__':
    main()
