# 실습 1-3: 3D LiDAR 포인트클라우드 및 ROI Crop Box 필터 (03_group_lidar)

본 실습에서는 3차원 라이다(LiDAR) 센서를 에고 차량에 동적으로 장착하여 주변 환경의 점 구름(Point Cloud) 데이터를 획득하고, 실시간 3D 뷰어 모니터링을 구동하며, NumPy 인덱싱 마스킹 기법을 사용해 차량 주변 특정 좌표 범위 영역만 걸러내는 **Crop Box ROI(Region of Interest) 필터**를 수동 구현합니다.

---

## 🎯 학습 목표
1. 라이다 센서의 스캔 방식(채널 수, 회전 속도, 초당 스캔 점 개수 등) 속성을 제어할 수 있습니다.
2. Open3D 또는 Matplotlib 라이브러리를 연동하여 비동기로 수집되는 3D 공간 좌표(X, Y, Z, Intensity)를 렌더링합니다.
3. NumPy Boolean Masking 연산을 활용해 외부 필터링 라이브러리 없이 순수 파이썬 메모리 가속을 통하여 Crop Box 관심 영역(ROI) 필터를 제작합니다.

---

## 📂 실습 구성 파일
* **[07_spectator_follow.py](07_spectator_follow.py)**: 에고 차량의 위치를 추적하여 Spectator 고정 정렬.
* **[12_carla_attach_lidar.py](12_carla_attach_lidar.py)**: 차량의 상단 루프 중앙 좌표에 32채널 3D LiDAR 센서를 결속(Attach).
* **[13_carla_view_lidar.py](13_carla_view_lidar.py)**: 실시간으로 수집되는 원시 3D 점구름 데이터를 Matplotlib 3D 투영 공간 상에 가시화.
* **[14_carla_view_lidar_cropped.py](14_carla_view_lidar_cropped.py)**: NumPy 조건부 마스킹을 사용해 차량 전방 20m, 좌우 8m 범위 내의 데이터만 가공하여 노출시키는 Crop Box ROI 필터링 뷰어 스크립트.

---

## 🛠️ 주요 코드 포인트 (학습 포인트)
### 1. 라이다 스펙 파라미터 구성 및 장착
```python
lidar_bp = blueprint_library.find('sensor.lidar.ray_cast')
lidar_bp.set_attribute('channels', '32')
lidar_bp.set_attribute('range', '50.0')
lidar_bp.set_attribute('points_per_second', '100000')
lidar_bp.set_attribute('rotation_frequency', '10')

lidar_transform = carla.Transform(carla.Location(x=0.0, z=2.5))
lidar = world.spawn_actor(lidar_bp, lidar_transform, attach_to=vehicle)
```

### 2. NumPy Boolean Masking 기반 Crop Box 필터 원리
```python
# 1. raw_data 바이트 스트림을 float32 데이터로 파싱하고 [N, 4] 행렬로 형상 복구 (x, y, z, intensity)
points = np.frombuffer(lidar_measurement.raw_data, dtype=np.float32).reshape(-1, 4)

# 2. X, Y, Z 각 축별 관심 범위 설정
x = points[:, 0]
y = points[:, 1]
z = points[:, 2]

# 전방 0~20미터, 좌우 8미터, 높이 -2~2미터 내의 데이터만 유지하는 boolean mask 생성
x_mask = (x >= 0.0) & (x <= 20.0)
y_mask = (y >= -8.0) & (y <= 8.0)
z_mask = (z >= -2.0) & (z <= 2.0)
roi_mask = x_mask & y_mask & z_mask

# NumPy 마스킹 필터링 실행
cropped_points = points[roi_mask]
```

---

## 🚀 실습 실행 순서
1. **에고 차량 스폰 및 라이다 마운트**:
   ```bash
   python3 12_carla_attach_lidar.py
   ```
2. **원시 3D 라이다 뷰어 구동**:
   차량 주변의 3D 반사 매체들이 공간 좌표 상에 원형으로 실시간 플로팅되는지 확인합니다.
   ```bash
   python3 13_carla_view_lidar.py
   ```
3. **수동 Crop Box 필터 검증**:
   마스크가 씌워져 에고 차량 전방 관심 구역(차량 범퍼 기준 사각 ROI 공간)을 제외한 나머지 노이즈 포인트들이 완벽히 여과되어 렌더링되는지 관찰합니다.
   ```bash
   python3 14_carla_view_lidar_cropped.py
   ```


