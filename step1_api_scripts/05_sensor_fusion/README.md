# 실습 1-5: 카메라-라이다 좌표계 동기화 및 3D 투영 센서 퓨전 (05_sensor_fusion)

본 실습은 다중 센서 퓨전의 정수로서, CARLA의 왼손 좌표계(LHS)를 ROS 2 표준 오른손 좌표계(RHS)로 정적 선형 변환하고, 카메라의 광학 렌즈 특성을 담은 내부 파라미터(Intrinsic) 및 라이다와 카메라 간 상대 위치를 담은 외부 파라미터(Extrinsic) 행렬을 연산하여 **3차원 라이다 좌표를 2차원 카메라 이미지 평면 상에 정확하게 투영(Projection)하여 시각화 퓨전**하는 과정을 학습합니다.

---

## 🎯 학습 목표
1. 왼손 좌표계(CARLA)와 오른손 좌표계(ROS2/ISO) 간 축 변환 및 부호 변환 수학 원리를 정밀하게 습득합니다.
2. 외부 캘리브레이션(Extrinsic Matrix) 및 내부 캘리브레이션(Intrinsic Matrix) 행렬곱을 순수 넘파이 행렬 연산으로 결합할 수 있습니다.
3. 2D 이미지 평면으로 사영된 라이다 포인트를 깊이(Depth/Distance) 기반 컬러 맵으로 시각화하여 정합 퓨전 이미지를 생성합니다.
4. 시뮬레이터 센서 큐(Sensor Queue) 동기화 파라미터를 조율하여 여러 센서의 촬영 타임스탬프를 물리적으로 완벽하게 동기 정합시킵니다.

---

## 📂 실습 구성 파일
* **[18_basic_coordinate_transform.py](18_basic_coordinate_transform.py)**: CARLA 좌표계(LHS: X-우측, Y-전방, Z-상단) ➔ ROS 좌표계(RHS: X-전방, Y-좌측, Z-상단) 변환 실습.
* **[19_basic_projection_math.py](19_basic_projection_math.py)**: 카메라 Intrinsic 행렬 모델(초점거리 $f_x, f_y$ 및 광학 주점 $c_x, c_y$) 구성과 3D 투영 공간 투영 행렬식 기본 수학 테스트.
* **[20_synchronous_mode_matching.py](20_synchronous_mode_matching.py)**: 시뮬레이터 fixed delta time 매칭 연산과 동기식(Synchronous) 센서 데이터 수신 큐 구축.
* **[21_run_manual_control.py](21_run_manual_control.py)**: 공식 키보드 주행 가동 모듈 실행 및 분석.
* **[22_sensor_fusion_visualization.py](22_sensor_fusion_visualization.py)**: **[1단계 종합 완성판]** 전방 카메라 프레임 위에 3D 라이다 반사점들의 상대 거리 정보를 컬러 점(빨강-가깝고, 파랑-멂)으로 실시간 융합하여 렌더링하는 핵심 센서 퓨전 실습.

---

## 🛠️ 주요 코드 포인트 (학습 포인트)
### 1. 카메라 Intrinsic(내부) 캘리브레이션 행렬식 구성
$$\mathbf{K} = \begin{bmatrix} f_x & 0 & c_x \\ 0 & f_y & c_y \\ 0 & 0 & 1 \end{bmatrix}$$
```python
# FOV 및 해상도로부터 초점 거리 f 연산
fov = 90.0
width = 800
height = 600
f = width / (2.0 * np.tan(fov * np.pi / 360.0))

intrinsic_matrix = np.array([
    [f, 0.0, width / 2.0],
    [0.0, f, height / 2.0],
    [0.0, 0.0, 1.0]
])
```

### 2. 3D 포인트 클라우드 ➔ 2D 이미지 평면 투영 수식
```python
# 1. 카메라 Extrinsic(외부) 변환 적용하여 카메라 중심 3D 좌표로 변환
points_cam = np.dot(extrinsic_matrix, np.vstack((pts_3d, np.ones(pts_3d.shape[1]))))
# 2. 전방 포인트 검사 (Z축이 0 이상인 전방 포인트만 사영)
valid_mask = points_cam[2, :] > 0.1
points_cam_valid = points_cam[:, valid_mask]

# 3. Intrinsic 투영 행렬곱 수행
points_2d = np.dot(intrinsic_matrix, points_cam_valid[:3, :])
# 4. Homogeneous 좌표 복원 (Z축 거리값으로 x, y를 나누어 2차원 픽셀 인덱스 좌표 획득)
pixel_u = points_2d[0, :] / points_2d[2, :]
pixel_v = points_2d[1, :] / points_2d[2, :]
```

---

## 🚀 실습 실행 순서
1. **정적 투영 수학 검증**:
   3차원 랜덤 좌표 1점이 이미지 격자 내 픽셀 인덱스로 완벽하게 역변환 정합 투영되는지 연산 결과를 확인합니다.
   ```bash
   python3 19_basic_projection_math.py
   ```
2. **동기식 매칭 검증**:
   카메라와 라이다 센서의 누적 버퍼 타임스탬음 오차가 완전히 일치하여 출력되는지 확인합니다.
   ```bash
   python3 20_synchronous_mode_matching.py
   ```
3. **[핵심] 실시간 센서 퓨전 시각화 구동**:
   차량 주행 도중 3D 물체들의 실시간 깊이(Depth) 포인트가 카메라 2D 객체(앞 차량 범퍼, 연석 등) 위에 오차 없이 완벽히 융합 투영 렌더링되는지 시각화 창을 통해 정밀 검증합니다.
   ```bash
   python3 22_sensor_fusion_visualization.py
   ```
