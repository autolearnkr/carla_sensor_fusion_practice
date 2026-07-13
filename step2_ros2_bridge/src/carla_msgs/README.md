# CARLA ROS 2 커스텀 메시지 패키지 (`carla_msgs`)

본 패키지는 CARLA 시뮬레이터와 ROS 2 네트워크 간에 구조화된 자율주행 정보(차량 제어 상태, 액터 목록, 센서 정합 데이터, 위부 날씨 설정 등)를 유통하기 위해 설계된 커스텀 ROS 2 메시지(`.msg`) 및 서비스(`.srv`) 정의 패키지입니다.

---

## 🎯 주요 정의 내용

### 1. 차량 제어 및 상태 정보 (`msg/`)
* **`CarlaEgoVehicleControl`**: 에고 차량에 탑재할 가속도(Throttle), 제동(Brake), 조향(Steer), 기어 및 핸드브레이크 상태 제어용 메시지.
* **`CarlaEgoVehicleStatus`**: 실시간 차량 제어 결과(속도, RPM, 가속 방향, 기어 등)를 피드백하는 상태 메시지.
* **`CarlaEgoVehicleInfo`**: 차량 액터의 고유 물리 한계 스펙(타이어 마찰력, 질량, 엔진 토크 맵 등)을 전송하는 정보 메시지.

### 2. 센서 및 물리적 이벤트 알림 (`msg/`)
* **`CarlaCollisionEvent`**: 타 액터 혹은 장애물과의 물리적 충돌 감지 정보 및 전달 속도 벡터를 중계하는 충돌 감지 메시지.
* **`CarlaLaneInvasionEvent`**: 차량 바퀴가 차선을 침범했을 때 차선 침범 타입(점선, 실선 등)을 감지하는 이벤트 메시지.
* **`CarlaBoundingBox`**: 센서 및 3D 물체 식별을 위한 bounding box 좌표 및 부피 크기 정보.

### 3. 월드 환경 정보 (`msg/`)
* **`CarlaWeatherParameters`**: 시뮬레이션 환경 내의 비구름(Rain), 태양 고도각(Sun Altitude), 안개(Fog), 바람(Wind) 등의 날씨 정보를 설정하는 파라미터.
* **`CarlaWorldInfo`**: 현재 로드된 맵 이름(Town01 ~ Town15 등) 및 OpenDRIVE XML 파일 콘텐츠 정보 전달.

---

## 🛠️ 빌드 방법

```bash
# 워크스페이스 홈으로 이동
cd ~/sensor_fusion_practice/step2_ros2_bridge

# 빌드 실행 (C++ 및 Python 헤더가 ROS 2 환경에 자동 등록됩니다)
colcon build --packages-select carla_msgs --symlink-install
source install/setup.bash
```
