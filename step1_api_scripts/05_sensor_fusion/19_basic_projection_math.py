#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
실습 19: 카메라-라이다 3D 투영 수학 연산 (고급)

이 스크립트는 3차원 라이다 포인트(XYZ)를 카메라 내부/외부 파라미터를 사용하여 
2차원 카메라 이미지 평면 상의 픽셀 좌표(u, v)로 매핑 투영(Projection)하는 
수학적 공식과 알고리즘을 파이썬 NumPy 행렬 연산으로 순수 구현하는 예제입니다.
"""

import sys
import numpy as np

def main():
    print("--- 실습 19: 카메라-라이다 3D 투영 수학 구현 ---")

    # 1. 3D LiDAR 포인트 정의 (동차 좌표계 표현을 위해 1.0 패딩 추가)
    lidar_points = np.array([
        [10.0,  0.0,  0.0, 1.0],  # 정중앙 10m 전방의 보행자 위치
        [15.0,  2.0,  1.0, 1.0],  # 15m 전방, 2m 우측, 1m 높이에 있는 신호등 기둥
        [5.0,  -1.5, -0.5, 1.0]   # 5m 전방, 1.5m 좌측, 바닥에 위치한 연석
    ], dtype=np.float32)
    
    # 2. 외부 파라미터 행렬 (Extrinsic Matrix, [R | T]) 정의 (4x4)
    extrinsic_matrix = np.array([
        [1.0, 0.0, 0.0,  0.5],
        [0.0, 1.0, 0.0,  0.0],
        [0.0, 0.0, 1.0, -0.2],
        [0.0, 0.0, 0.0,  1.0]
    ], dtype=np.float32)

    # 3. 내부 파라미터 행렬 (Intrinsic Matrix, K) 정의 (3x3)
    K = np.array([
        [400.0,   0.0, 400.0],  # f_x, 0, c_x (c_x = 800/2)
        [  0.0, 400.0, 300.0],  # 0, f_y, c_y (c_y = 600/2)
        [  0.0,   0.0,   1.0]
    ], dtype=np.float32)

    print("\n[Projection Step 1: Transforming LiDAR points to Camera Frame]")
    points_camera_frame = np.dot(extrinsic_matrix, lidar_points.T) # [4, N]
    print(f"Points in Camera Frame:\n{points_camera_frame[:3, :].T}")

    # 4. 카메라 3D 좌표를 2D 이미지 평면으로 투영 (Intrinsic 연산)
    print("\n[Projection Step 2: Projecting Camera 3D points to 2D Image Plane]")
    points_image_plane_homo = np.dot(K, points_camera_frame[:3, :]) # [3, N]
    
    # 5. 동차 좌표계 정규화 (Z축 깊이 값으로 나누기)
    u = points_image_plane_homo[0, :] / points_image_plane_homo[2, :]
    v = points_image_plane_homo[1, :] / points_image_plane_homo[2, :]
    depths = points_camera_frame[2, :]

    print("\n[Projection Result: Final 2D Pixel Coordinates (u, v)]")
    for i in range(len(lidar_points)):
        p_u, p_v, d = u[i], v[i], depths[i]
        is_visible = (0 <= p_u < 800) and (0 <= p_v < 600)
        status = "VISIBLE in Image" if is_visible else "OUT OF FIELD"
        print(f"Lidar Point {i} -> Pixel Coordinates: u={p_u:.1f}, v={p_v:.1f} | Depth={d:.1f}m | Status: {status}")

if __name__ == '__main__':
    main()
