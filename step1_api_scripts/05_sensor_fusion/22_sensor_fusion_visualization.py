#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
실습 22: 실시간 카메라-라이다 센서 퓨전 시각화 (고급 - Capstone 통합본)

이 스크립트는 1단계 실습의 최종 결과물(캡스톤)입니다. 
시뮬레이터 동기 모드 하에서 시간 축이 완벽하게 일치된 카메라 이미지와 라이다 데이터를 수집한 뒤,
LHS->RHS 좌표 변환 및 내/외부 캘리브레이션 투영 행렬식을 연동 적용하여, 
카메라 영상 픽셀 위에 라이다 3D 포인트를 거리(Depth)별 색상으로 실시간 오버레이 매핑하여 
OpenCV 창으로 스트리밍하는 실시간 3D 센서 퓨전을 시각적으로 구현합니다.
"""

import sys
import queue
import time
import numpy as np
import cv2

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
    
    actor_list = []

    width, height = 800, 600
    cx = width / 2.0
    cy = height / 2.0
    fov = 90.0
    f = width / (2.0 * np.tan(fov * np.pi / 360.0))
    
    K = np.array([
        [f,   0.0, cx],
        [0.0, f,   cy],
        [0.0, 0.0, 1.0]
    ])

    extrinsic = np.array([
        [1.0, 0.0, 0.0,  0.5],
        [0.0, 1.0, 0.0,  0.0],
        [0.0, 0.0, 1.0, -0.3],
        [0.0, 0.0, 0.0,  1.0]
    ])

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
        actor_list.append(vehicle)
        vehicle.set_autopilot(True)

        camera_bp = blueprint_library.find('sensor.camera.rgb')
        camera_bp.set_attribute('image_size_x', str(width))
        camera_bp.set_attribute('image_size_y', str(height))
        camera_bp.set_attribute('fov', str(fov))
        camera_transform = carla.Transform(carla.Location(x=2.0, z=1.7))
        camera = world.spawn_actor(camera_bp, camera_transform, attach_to=vehicle)
        actor_list.append(camera)

        lidar_bp = blueprint_library.find('sensor.lidar.ray_cast')
        lidar_bp.set_attribute('channels', '32')
        lidar_bp.set_attribute('points_per_second', '300000')
        lidar_bp.set_attribute('rotation_frequency', '20.0')
        lidar_bp.set_attribute('range', '50.0')
        lidar_transform = carla.Transform(carla.Location(x=1.5, z=2.0))
        lidar = world.spawn_actor(lidar_bp, lidar_transform, attach_to=vehicle)
        actor_list.append(lidar)

        camera.listen(lambda image: sensor_queue.put((image.frame, 'camera', image)))
        lidar.listen(lambda point_cloud: sensor_queue.put((point_cloud.frame, 'lidar', point_cloud)))
        
        print("\nReal-time Camera-LiDAR Sensor Fusion Display Active.")
        print("Press Ctrl+C in terminal to exit.")

        while True:
            world_frame = world.tick()
            
            data_dict = {}
            while len(data_dict) < 2:
                try:
                    s_frame, s_name, s_data = sensor_queue.get(timeout=1.0)
                    if s_frame == world_frame:
                        data_dict[s_name] = s_data
                except queue.Empty:
                    break
            
            if 'camera' in data_dict and 'lidar' in data_dict:
                cam_image = data_dict['camera']
                lidar_scan = data_dict['lidar']
                
                raw_img = np.frombuffer(cam_image.raw_data, dtype=np.uint8)
                rgba_img = raw_img.reshape((height, width, 4))
                bgr_img = rgba_img[:, :, :3].copy()
                
                raw_lidar = np.frombuffer(lidar_scan.raw_data, dtype=np.float32)
                points_3d = raw_lidar.reshape(-1, 4)[:, :3]
                points_3d[:, 1] = -points_3d[:, 1]
                
                points_3d_homo = np.hstack((points_3d, np.ones((len(points_3d), 1)))).T
                points_cam_frame = np.dot(extrinsic, points_3d_homo)
                
                front_mask = points_cam_frame[2, :] > 0.1
                points_cam_frame = points_cam_frame[:, front_mask]
                
                if points_cam_frame.shape[1] > 0:
                    pixel_homo = np.dot(K, points_cam_frame[:3, :])
                    u = pixel_homo[0, :] / pixel_homo[2, :]
                    v = pixel_homo[1, :] / pixel_homo[2, :]
                    depths = points_cam_frame[2, :]
                    
                    valid_mask = (u >= 0) & (u < width) & (v >= 0) & (v < height)
                    u_valid = u[valid_mask].astype(int)
                    v_valid = v[valid_mask].astype(int)
                    depth_valid = depths[valid_mask]
                    
                    max_detect_depth = 30.0
                    for px, py, dp in zip(u_valid, v_valid, depth_valid):
                        ratio = min(dp / max_detect_depth, 1.0)
                        color = (int(255 * ratio), 0, int(255 * (1.0 - ratio)))
                        cv2.circle(bgr_img, (px, py), 2, color, -1)
                
                cv2.imshow("Real-Time Camera-LiDAR Sensor Fusion", bgr_img)
                cv2.waitKey(1)
                
            time.sleep(0.01)

    except KeyboardInterrupt:
        print("\nStopping sensor fusion loop...")
    except Exception as e:
        print(f"Error occurred: {e}", file=sys.stderr)
    finally:
        print("\nRestoring original world settings...")
        world.apply_settings(original_settings)
        
        print("Cleaning up spawned actors...")
        if camera is not None and camera.is_listening: camera.stop()
        if lidar is not None and lidar.is_listening: lidar.stop()
        for actor in actor_list:
            if actor.is_alive:
                actor.destroy()
        cv2.destroyAllWindows()
        print("Cleanup finished. Exiting.")

if __name__ == '__main__':
    main()
