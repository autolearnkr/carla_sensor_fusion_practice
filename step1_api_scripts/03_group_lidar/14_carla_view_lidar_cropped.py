#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
실습 14: 라이다 스캔 포인트 실시간 Crop Box Filter 전처리 및 3D 시각화 (중급 - 그룹 B)

이 스크립트는 월드 상의 기존 라이다 센서(12번 예제)를 검색해 내고,
NumPy를 사용해 자율주행의 핵심 전처리 단계인 **Crop Box Filter(ROI 필터)**를 직접 구현하여
특정 관심 영역(전방 0~25m, 좌우 10m, 높이 -2~2m) 내의 3D 포인트 클라우드만 선별 추출한 뒤
Open3D Visualizer 윈도우 창으로 실시간 시각화하는 실습입니다.
"""

import sys
import time
import numpy as np

try:
    import carla
except ImportError:
    print("Error: 'carla' python module is not installed.", file=sys.stderr)
    sys.exit(1)

try:
    import open3d as o3d
    OPEN3D_AVAILABLE = True
except ImportError:
    OPEN3D_AVAILABLE = False
    print("Error: 'open3d' python module is not installed. Run: pip install open3d", file=sys.stderr)
    sys.exit(1)

pcd = o3d.geometry.PointCloud()
vis = o3d.visualization.Visualizer()

def crop_box_filter(xyz, intensities, x_range=(0.0, 25.0), y_range=(-10.0, 10.0), z_range=(-2.0, 2.0)):
    """
    3D 직육면체(Crop Box) 범위를 기준으로 관심 영역(ROI) 포인트만 남기는 수동 필터링 함수
    """
    x_min, x_max = x_range
    y_min, y_max = y_range
    z_min, z_max = z_range
    
    # NumPy boolean indexing을 통한 Crop Box 영역 마스크 생성
    mask = (xyz[:, 0] >= x_min) & (xyz[:, 0] <= x_max) & \
           (xyz[:, 1] >= y_min) & (xyz[:, 1] <= y_max) & \
           (xyz[:, 2] >= z_min) & (xyz[:, 2] <= z_max)
           
    # 필터 적용 데이터 선별
    filtered_xyz = xyz[mask]
    filtered_intensities = intensities[mask]
    
    return filtered_xyz, filtered_intensities

def on_lidar_receive(point_cloud):
    global pcd, vis
    
    # 1. raw_data 바이트 스트림 역직렬화
    flat_data = np.frombuffer(point_cloud.raw_data, dtype=np.float32)
    points = flat_data.reshape(-1, 4)
    
    # 2. LHS(CARLA) -> RHS(ROS) 축 반전
    xyz = points[:, :3]
    xyz[:, 1] = -xyz[:, 1]  # Y축 반전
    intensities = points[:, 3]
    
    # 3. [Crop Box Filter 전처리 수행]
    # 에고 차량 전방 25m, 좌우 10m, 높이 -2m~2m 범위의 관심 영역(ROI)만 필터링합니다.
    xyz_cropped, intensities_cropped = crop_box_filter(
        xyz, intensities,
        x_range=(0.0, 25.0),    # 전방 방향 (X)
        y_range=(-10.0, 10.0),  # 좌우 방향 (Y)
        z_range=(-2.0, 2.0)     # 상하 방향 (Z)
    )
    
    # 필터링 결과가 없을 경우 예외 처리
    if len(xyz_cropped) == 0:
        pcd.points = o3d.utility.Vector3dVector(np.zeros((1, 3)))
        pcd.colors = o3d.utility.Vector3dVector(np.zeros((1, 3)))
    else:
        pcd.points = o3d.utility.Vector3dVector(xyz_cropped)
        
        # 반사 강도 기반 컬러링
        colors = np.zeros((len(intensities_cropped), 3))
        colors[:, 0] = intensities_cropped        # Red 채널 비례
        colors[:, 2] = 1.0 - intensities_cropped  # Blue 채널 반비례
        pcd.colors = o3d.utility.Vector3dVector(colors)
    
    vis.update_geometry(pcd)
    vis.poll_events()
    vis.update_renderer()

def find_existing_lidar(world):
    actors = world.get_actors()
    for actor in actors:
        if 'sensor.lidar.ray_cast' in actor.type_id:
            return actor
    return None

def main():
    global pcd, vis
    if not OPEN3D_AVAILABLE:
        return

    print("Connecting to CARLA Server on localhost:2000...")
    client = carla.Client('127.0.0.1', 2000)
    client.set_timeout(10.0)
    
    lidar = None
    try:
        world = client.get_world()
        print("Searching for an active LiDAR sensor in the simulator...")
        lidar = find_existing_lidar(world)
        
        if lidar is None:
            print("\n[ERROR] No active LiDAR sensor found in the simulator!")
            print("Please make sure '12_carla_attach_lidar.py' is running in Terminal 2.")
            sys.exit(1)
            
        print(f"Active LiDAR found! Sensor ID: {lidar.id}")
        
        vis.create_window(window_name="CARLA ROI CropBox Filtered LiDAR Viewer", width=1280, height=720)
        pcd.points = o3d.utility.Vector3dVector(np.zeros((3, 3)))
        vis.add_geometry(pcd)
        
        lidar.listen(on_lidar_receive)
        print("\nStreaming ROI Crop Box Filtered 3D Point Cloud to Open3D Window.")
        print("Press Ctrl+C in terminal or close the window to exit.")
        
        while True:
            vis.poll_events()
            vis.update_renderer()
            time.sleep(0.01)
            
    except KeyboardInterrupt:
        print("\nStopping LiDAR stream subscription...")
    except Exception as e:
        print(f"Error occurred: {e}", file=sys.stderr)
    finally:
        if lidar is not None and lidar.is_listening:
            lidar.stop()
        vis.destroy_window()
        print("Stream closed. LiDAR sensor remains attached in CARLA.")

if __name__ == '__main__':
    main()
