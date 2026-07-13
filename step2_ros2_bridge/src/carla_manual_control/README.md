# CARLA ROS 2 수동 제어 패키지 (`carla_manual_control`)

본 패키지는 CARLA 시뮬레이터에 생성된 에고 차량을 사용자가 키보드로 수동 조작하고, 주행 중 발생하는 다양한 차량 원격 측정(Telemetry) 데이터 및 센서 뷰를 실시간 모니터링할 수 있는 Pygame 기반의 수동 주행 GUI 노드를 제공합니다.

---

## 🎯 주요 기능

1. **키보드 기반 차량 물리 제어**:
   - `W`, `S`, `A`, `D` 키를 이용해 차량 조향 및 전진/후진 제어.
   - `Space` 키를 이용한 급제동(Handbrake) 작동.
   - `Q` 키를 누르면 기어를 수동/자동으로 전환 가능하며, 후진 기어 선택 가능.
2. **Pygame 기반의 HUD 가시화**:
   - 현재 속도(km/h), 엔진 RPM, 사용 중인 기어, 스티어링 각도, 액셀/브레이크 인풋 비율 등의 핵심 제어 상태 실시간 가시화.
   - 시뮬레이터 서버 시간 및 고정 프레임 정보 출력.
3. **실시간 센서 뷰 모니터링**:
   - 차량에 마운트된 전방 카메라 등 센서 토픽을 가로채 GUI 창 안에 출력 및 렌더링.
   - `Tab` 키 등을 이용해 장착된 카메라 시점 전환 가능.
4. **Spectator 및 차량 스폰 제어**:
   - 수동 제어 모드 기동 시 시뮬레이션 환경 내 주시 상태 설정.

---

## 🛠️ 실행 방법

```bash
# 워크스페이스 홈으로 이동
cd ~/sensor_fusion_practice/step2_ros2_bridge

# 빌드 실행
colcon build --packages-select carla_manual_control --symlink-install
source install/setup.bash

# 수동 제어 런치 실행 (Ego vehicle이 이미 기동되어 활성화된 상태여야 함)
ros2 launch carla_manual_control carla_manual_control.launch.py
```
