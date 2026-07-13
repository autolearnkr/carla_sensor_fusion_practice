#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
실습 13: 기존 라이다 센서 스캔 및 실시간 3D 점군 시각화 (중급 - 그룹 B)

이 스크립트는 시뮬레이터 월드에 이미 장착되어 활성화되어 있는 라이다 센서(12번 예제)를 검색해내고,
그 데이터를 실시간으로 역직렬화 및 RHS(오른손계) 좌표 변환하여 
Open3D Visualizer 윈도우 창으로 송출해 주는 독립 3D 뷰어 실습입니다.
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

def on_lidar_receive(point_cloud):
    global pcd, vis
    flat_data = np.frombuffer(point_cloud.raw_data, dtype=np.float32)
    points = flat_data.reshape(-1, 4)
    xyz = points[:, :3]
    xyz[:, 1] = -xyz[:, 1]  # Y축 반전
    pcd.points = o3d.utility.Vector3dVector(xyz)
    
    intensities = points[:, 3]
    colors = np.zeros((len(intensities), 3))
    colors[:, 0] = intensities
    colors[:, 2] = 1.0 - intensities
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
        
        vis.create_window(window_name="CARLA Live 3D LiDAR Viewer", width=1280, height=720)
        pcd.points = o3d.utility.Vector3dVector(np.zeros((3, 3)))
        vis.add_geometry(pcd)
        
        lidar.listen(on_lidar_receive)
        print("\nStreaming 3D Point Cloud to Open3D Window.")
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
