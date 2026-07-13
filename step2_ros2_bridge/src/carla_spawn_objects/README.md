# CARLA ROS 2 액터 자동 스폰 패키지 (`carla_spawn_objects`)

본 패키지는 설정 파일에 정의된 규칙에 기반하여 CARLA 시뮬레이션 월드 내에 자율주행 차량(Ego Vehicle) 및 관련 센서(카메라, 라이다, GNSS 등) 액터들을 동적으로 생성(Spawn), 결속(Attach), 소멸시키는 생명주기 관리 패키지입니다.

---

## 🎯 주요 기능

1. **설정 파일 기반 일괄 자동 스폰**:
   - `config/objects.json` 또는 ROS 2 파라미터를 읽어와 여러 차량 및 복수의 센서들을 한 번에 자동으로 서버에 생성 및 정렬합니다.
2. **동적 센서 결속 (Attachment)**:
   - 생성한 차량 액터 기준의 로컬 좌표(x, y, z, roll, pitch, yaw)를 기준으로 라이다 및 카메라 센서를 특정 차량에 결속(`attach_to`)시킵니다.
3. **TF 프레임 트리 구성**:
   - 스폰된 에고 차량 및 센서 간의 상대적 물리 거리 관계를 ROS 2 좌표 변환(TF/Static TF) 정보로 등록 및 발행합니다.
4. **차량 초기 좌표 설정**:
   - 차량의 주행 시작 위치(Spawn Point)를 `set_initial_pose` 서비스를 통해 설정 및 재조정할 수 있는 인터페이스를 제공합니다.

---

## 🛠️ 실행 방법

```bash
# 워크스페이스 홈으로 이동
cd ~/sensor_fusion_practice/step2_ros2_bridge

# 빌드 및 로드
colcon build --packages-select carla_spawn_objects --symlink-install
source install/setup.bash

# 예시 차량 및 기본 센서 팩 스폰 실행
ros2 launch carla_spawn_objects carla_example_ego_vehicle.launch.py
```
