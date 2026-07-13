#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
실습 18: 센서 좌표계 표준 변환 (LHS to RHS) (고급)

이 스크립트는 시뮬레이터(LHS, 왼손 좌표계)와 로봇/자율주행 프레임워크(RHS, 오른손 좌표계)
사이의 좌표계 극성 불일치를 해결하기 위한 수학적 변환 기법을 학습합니다.
"""

import sys
import numpy as np

def main():
    print("--- 실습 18: CARLA(LHS) ↔ ROS(RHS) 좌표계 변환 실습 ---")
    
    carla_points = np.array([
        [15.5,  2.3, -0.5, 0.9],  # 우측 장애물
        [8.0,  -4.1,  0.2, 0.4],  # 좌측 장애물
        [22.1,  0.0,  1.5, 0.1]   # 전방 마커
    ], dtype=np.float32)
    
    print("\n[Original CARLA Points (Left-Handed System)]")
    for i, pt in enumerate(carla_points):
        print(f"Point {i}: X={pt[0]:.1f}, Y={pt[1]:.1f} (Right), Z={pt[2]:.1f} | Intensity={pt[3]:.1f}")
        
    ros_points = np.copy(carla_points)
    ros_points[:, 1] = -carla_points[:, 1]
    
    print("\n[Converted ROS/Autoware Points (Right-Handed System)]")
    for i, pt in enumerate(ros_points):
        print(f"Point {i}: X={pt[0]:.1f}, Y={pt[1]:.1f} (Left), Z={pt[2]:.1f} | Intensity={pt[3]:.1f}")
        
    dist_carla = np.linalg.norm(carla_points[0, :3])
    dist_ros = np.linalg.norm(ros_points[0, :3])
    
    print(f"\nDistance from Origin (Point 0):")
    print(f" - CARLA distance: {dist_carla:.3f} m")
    print(f" - ROS distance:   {dist_ros:.3f} m")
    
    if np.isclose(dist_carla, dist_ros):
        print("\n[SUCCESS] Coordinate transformation completed without geometric distortion!")
    else:
        print("\n[FAILED] Geometric distortion detected in transformation.", file=sys.stderr)

if __name__ == '__main__':
    main()
