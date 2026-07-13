# CARLA ROS 2 통신 브릿지 패키지 (`carla_ros_bridge`)

본 패키지는 독립된 CARLA 시뮬레이터 서버 프로세스와 ROS 2 네트워크 노드들을 상호 연결하여 자율주행 시뮬레이션을 구현해 주는 연동 브릿지 핵심 패키지입니다.

---

## 🎯 주요 기능

1. **양방향 통신 번역**:
   - CARLA 시뮬레이터의 3D 물리 엔진 데이터를 ROS 2 표준 센서 메시지 및 로봇 상태 토픽으로 변환 및 송출합니다.
   - 반대로 ROS 2 제어 토픽에서 조향, 속도 제어 명령을 접수하여 차량 제어 함수(`carla.VehicleControl`)로 전달합니다.
2. **동기식 제어(Synchronous Mode) 매칭**:
   - 센서 타임스탬프 동기화를 위해 시뮬레이터 서버 프레임을 통제하여 고정 델타 시간 간격으로 연산되도록 연동 제어합니다.
3. **액터 매니저**:
   - 시뮬레이터 내부에 존재하는 차량, 스펙테이터(관찰 카메라), 신호등 등의 다양한 액터들을 ROS 2 노드 모델로 매핑 및 관리합니다.

---

## 🛠️ 실행 및 구동 방법

```bash
# 워크스페이스 홈으로 이동
cd ~/sensor_fusion_practice/step2_ros2_bridge

# 빌드 및 로드
colcon build --packages-select carla_ros_bridge --symlink-install
source install/setup.bash

# 브릿지 런치 기동
ros2 launch carla_ros_bridge carla_ros_bridge.launch.py
```
*(참고: 연결 정보 및 동기식 모드 스위치는 `config/settings.yaml` 파일 내에서 지정할 수 있습니다.)*
