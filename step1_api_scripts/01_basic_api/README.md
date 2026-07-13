# 실습 1-1: CARLA API 및 기초 차량 제어 (01_basic_api)

본 실습에서는 CARLA 시뮬레이터 파이썬 API를 사용하여 가상 세계(World)와 클라이언트(Client)를 연결하고, 맵(Map) 조회, 차량 스폰, 수동 물리 속성 제어, 그리고 3D 공간 상에서 Spectator 카메라를 정렬하는 기초적인 차량 제어 기술을 학습합니다.

---

## 🎯 학습 목표
1. CARLA 시뮬레이터 클라이언트를 생성하고 가상 월드 객체를 성공적으로 룩업할 수 있습니다.
2. 차량(Actor)의 블루프린트를 검색하고, 안전 충돌 검사 알고리즘을 적용하여 특정 좌표에 차량을 스폰 및 소멸시킬 수 있습니다.
3. `VehicleControl` 클래스를 사용하여 차량의 스로틀, 조향, 브레이크 등 물리 수동 제어 구조를 이해합니다.
4. 3D 벡터 수학(방향 벡터 연산)을 적용하여 시뮬레이터 카메라(Spectator)를 스폰된 차량 뒤에 자동으로 추적 정렬할 수 있습니다.

---

## 📂 실습 구성 파일
* **[01_connect_and_map.py](01_connect_and_map.py)**: 시뮬레이터 포트(2000) 연결 및 활성화된 월드 맵 정보 출력.
* **[02_weather_control.py](02_weather_control.py)**: 월드 날씨 파라미터(구름, 강수량, 태양 고도각 등) 동적 제어.
* **[03_spawn_vehicle.py](03_spawn_vehicle.py)**: `Model3` 차량 스폰 및 소멸 라이프사이클 처리.
* **[04_vehicle_autopilot.py](04_vehicle_autopilot.py)**: 오토파일럿 활성화 및 트래픽 매니저(TM) 연동 자율주행.
* **[05_vehicle_manual_physics.py](05_vehicle_manual_physics.py)**: 스로틀(throttle)과 조향(steer) 값을 루프 내에서 가변하여 원형 주행 물리 제어.
* **[06_spectator_align.py](06_spectator_align.py)**: 스폰된 차량 뒤쪽 공간으로 Spectator 고정 배치 연산.

---

## 🛠️ 주요 코드 포인트 (학습 포인트)
### 1. CARLA Client 및 Blueprint Library 조회
```python
client = carla.Client('localhost', 2000)
world = client.get_world()
blueprint_library = world.get_blueprint_library()
vehicle_bp = blueprint_library.filter('model3')[0]
```
* 포트 `2000`을 통해 시뮬레이터에 소켓 연결을 수행하고, 원하는 액터의 설계도(Blueprint)를 룩업합니다.

### 2. Spectator 카메라 추적 공간 변환 (3D 벡터 수학)
```python
# 차량 위치에서 뒤쪽(-yaw)으로 8미터, 위쪽으로 3미터 이동한 위치로 Spectator 카메라 이동
vehicle_transform = vehicle.get_transform()
vehicle_location = vehicle_transform.location
vehicle_rotation = vehicle_transform.rotation

yaw_rad = math.radians(vehicle_rotation.yaw)
camera_x = vehicle_location.x - 8.0 * math.cos(yaw_rad)
camera_y = vehicle_location.y - 8.0 * math.sin(yaw_rad)
camera_z = vehicle_location.z + 3.0
```

---

## 🚀 실습 실행 순서
> **[전제 조건]**: CARLA Simulator(EXE)가 백그라운드에 먼저 실행 중이어야 합니다.

1. **시뮬레이터 연결 확인**:
   ```bash
   python3 01_connect_and_map.py
   ```
2. **동적 날씨 변환 확인**:
   실행 후 시뮬레이터 화면의 태양 위치와 비구름 변화를 모니터링합니다.
   ```bash
   python3 02_weather_control.py
   ```
3. **차량 스폰 및 수동 주행 테스트**:
   차량이 정상적으로 원형을 돌며 전진 주행하는지 확인하고, 프로그램 종료 시 차량이 안전하게 소멸하는지 관찰합니다.
   ```bash
   python3 05_vehicle_manual_physics.py
   ```
