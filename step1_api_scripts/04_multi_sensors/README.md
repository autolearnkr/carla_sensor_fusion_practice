# 실습 1-4: 다중 센서 스냅온 및 AEB 제동 알고리즘 (04_multi_sensors)

본 실습에서는 서라운드 인식을 위한 다중(6개 방향) 카메라 센서 장착 기법을 익히고, 수집된 라이다 포인트 클라우드 로우 데이터를 파일로 저장하는 바이너리 수집을 수행하며, 전방 거리 연산을 실시간 피드백 루프로 돌려 자동 비상 제동을 활성화시키는 **AEB(Autonomous Emergency Braking) 시스템**을 구현합니다.

---

## 🎯 학습 목표
1. 자율주행 차량의 6방향 서라운드 카메라를 체계적으로 배치하고 `role_name` 및 소켓 통신 토픽을 논리적으로 분리하는 법을 이해합니다.
2. 실시간 센서 스트림 데이터를 로컬 바이너리(.bin) 파일로 정확하게 쓰기 및 복구하는 로깅 실습을 수행합니다.
3. 라이다 전방 반사면 점군과의 최소 거리(Distance) 연산 피드백을 차량 제어 API(`VehicleControl`)에 결속시켜 AEB 비상 제동 로직을 완성합니다.

---

## 📂 실습 구성 파일
* **[07_spectator_follow.py](07_spectator_follow.py)**: 에고 차량의 위치를 추적하여 Spectator 고정 정렬.
* **[15_carla_attach_6_cameras.py](15_carla_attach_6_cameras.py)**: 차량의 전/후/좌/우/전좌/전우 등 6방향에 카메라를 다중 장착하고 각 role_name을 `front`, `back`, `left`, `right`, `front_left`, `front_right`로 이식.
* **[16_lidar_collect_binary.py](16_lidar_collect_binary.py)**: 3D 라이다 스캔 데이터를 수신하여 로컬 파일 시스템 상에 실시간으로 `.bin` 바이너리 로그 파일을 누적 저장.
* **[17_carla_aeb_simulation.py](17_carla_aeb_simulation.py)**: 차량 전방 10m 이내에 장애물(주차 차량, 파편 등) 감지 시 자동으로 강력한 제동(`brake=1.0`, `throttle=0.0`) 명령을 전송하여 추돌을 제어하는 실습 스크립트.

---

## 🛠️ 주요 코드 포인트 (학습 포인트)
### 1. 6방향 카메라 각도 매핑 기법
```python
# 각 카메라마다 방향(Pitch, Yaw, Roll)을 다르게 결속
rotations = {
    "front": carla.Rotation(yaw=0),
    "back": carla.Rotation(yaw=180),
    "left": carla.Rotation(yaw=-90),
    "right": carla.Rotation(yaw=90),
    "front_left": carla.Rotation(yaw=-45),
    "front_right": carla.Rotation(yaw=45)
}
```

### 2. AEB 비상 자동 제동 논리 연산
```python
def check_aeb_condition(lidar_data):
    # 전방 관심 차선 구역(좌우 1.5m 이내, 높이 -1.5~1m 이내) 필터링
    x = lidar_data[:, 0]
    y = lidar_data[:, 1]
    z = lidar_data[:, 2]
    
    aeb_zone_mask = (x > 0.0) & (x < 10.0) & (y >= -1.5) & (y <= 1.5) & (z >= -1.5) & (z <= 1.0)
    aeb_points = lidar_data[aeb_zone_mask]
    
    if len(aeb_points) > 10:  # 감지된 반사점 개수가 기준치 초과 시 위험 상황으로 판정
        min_dist = np.min(aeb_points[:, 0])
        return True, min_dist
    return False, None
```

---

## 🚀 실습 실행 순서
1. **6방향 다중 센서 스냅온 구동**:
   차량 스폰 후 6개 방향의 각각 독립된 카메리가 결속되고 터미널에 스폰 이력이 로깅되는지 확인합니다.
   ```bash
   python3 15_carla_attach_6_cameras.py
   ```
2. **라이다 로그 데이터 아카이빙**:
   수집 완료 후 폴더 내에 수많은 바이너리 `.bin` 파일이 저장되는지 확인합니다.
   ```bash
   python3 16_lidar_collect_binary.py
   ```
3. **AEB 장애물 충돌 제동 시험**:
   도로상에 장애물 차량을 배치하고, 에고 차량이 돌진하다가 전방 10미터 이내에서 브레이크 등과 함께 차량이 스키드마크를 내며 자동 비상 정지하는지 가시성 체크를 진행합니다.
   ```bash
   python3 17_carla_aeb_simulation.py
   ```
