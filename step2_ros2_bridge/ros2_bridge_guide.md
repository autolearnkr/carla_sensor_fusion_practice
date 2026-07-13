# CARLA-ROS-Bridge 및 센서 전처리 모듈 연동 가이드 (2단계)

본 가이드는 실습 2단계 과정으로, 시뮬레이터와 ROS 2 네트워크를 연결해 주는 **`carla-ros-bridge`** 패키지의 내부 작동 원리를 분석하고, 외부 종속성 에러 없이 바닐라 ROS 2 Humble/Foxy 데스크탑 환경에서도 100% 빌드 및 구동되는 **`ros2_sensor_processing` (파이썬 센서 처리 패키지)** 및 공식 **`image_pipeline`** 패키지를 통해 센서 전처리를 실행하고 시각화 검증을 완료하는 교육 매뉴얼입니다.

특히 본 실습은 자율주행 표준 규격인 **XYZIRC(24바이트/점 고정밀 라이다 데이터 포맷)** 정합성과 메시지 패킹 기법(자동 create_cloud vs 수동 tobytes)의 연쇄 실습을 제공합니다.

---

## 1. 2단계 실습용 ROS 2 표준 워크스페이스 구조

실습 디렉터리 내 [step2_ros2_bridge](step2_ros2_bridge) 하위에는 ROS 2 표준 빌드 레이아웃을 준수하여 소스들이 배치된 **`src/`** 폴더가 제공되며, 경량 파이썬 센서 처리 패키지의 명칭은 **`ros2_sensor_processing`** 입니다. 이 디렉터리 자체가 하나의 독립 colcon workspace로 동작합니다.

```
step2_ros2_bridge/
├── ros2_bridge_guide.md        # 본 가이드 지침서
└── src/                        # ROS2 표준 소스 디렉터리
    ├── carla_common/           # CARLA ROS 공통 유틸리티 라이브러리 패키지
    ├── carla_manual_control/   # Pygame 기반 수동 주행 및 HUD 제어 패키지
    ├── carla_msgs/             # CARLA ROS 커스텀 메시지 정의 패키지
    ├── carla_spawn_objects/    # objects.json 기반 액터/센서 자동 스폰 패키지
    ├── carla_ros_bridge/       # 시뮬레이터 ↔ ROS 2 통신 브릿지 패키지
    │   └── src/carla_ros_bridge/
    │       ├── lidar.py        # 기본형 4필드(XYZI) 라이다 변환 모듈
    │       ├── lidar_create_cloud.py # [참고 소스] create_cloud 적용 모듈
    │       └── lidar_tobytes.py      # [참고 소스] tobytes 직렬화 수동 적용 모듈
    └── ros2_sensor_processing/ # [NEW] 경량 파이썬 이미지/라이다 필터 통합 실습 패키지
        ├── launch/
        │   └── sensor_processing.launch.py # 2종 노드 선택 런치 스크립트
        └── ros2_sensor_processing/
            ├── camera_pipeline_node.py
            └── lidar_filter_create_cloud_node.py # [대안 A] 자동 API 직렬화 전처리 노드
```

---

## 2. 런치 파일(launch) 내부 설정을 통한 직렬화 모드 선택 제어

학생들은 `ros2_sensor_processing` 패키지의 런치 파일 [sensor_processing.launch.py](sensor_processing.launch.py) 코드 내부에서 **원하는 LiDAR 필터링 Executable 노드의 주석을 풀거나 지정**하여 직렬화 처리 노드를 자유롭게 스위칭하여 구동할 수 있습니다.

```python
# sensor_processing.launch.py 소스코드 내부
# [대안 A: 기본형] LiDAR create_cloud 적용 전처리 노드 구동
Node(
    package='ros2_sensor_processing',
    executable='lidar_filter_create_cloud_node',
    name='lidar_filter_node',
    output='screen'
),

# [대안 B: 수동형] LiDAR tobytes() 수동 직렬화 적용 전처리 노드 구동 (실습용)
# Node(
#     package='ros2_sensor_processing',
#     executable='lidar_filter_tobyte_node',
#     name='lidar_filter_node',
#     output='screen'
# )
```

---

## 3. 전처리 패키지별 상세 기능 및 작동 원리

### 3.1 카메라 전처리: `image_pipeline` & `ros2_sensor_processing` (패키지)
* **image_proc (rectify) & camera_pipeline_node**:
  - 역할: 왜곡 보정 및 Canny Edge 윤곽선을 추출하여 `/processed/camera/image`로 재발행합니다.

### 3.2 라이다 전처리 및 XYZIRC 포맷 강제 검증 제약 조건: `ros2_sensor_processing`
* **수신 토픽**: `/carla/hero/lidar`
* **동작 원리 및 정합 제약**:
  1. **[강제 정합 검사]**: 수신 PointField 데이터 헤더를 검사하여 `channel` 및 `return_type` 필드가 포함된 **XYZIRC(24바이트/점)** 구조인지 판별합니다.
     - 만약 기존의 4필드 기본 `XYZI` 포맷으로 토픽이 들어올 경우, 필터 처리를 즉시 중단하고 **포맷 불일치 경고 에러(🚨 FORMAT ERROR)**를 로그로 출력해 학생들이 브릿지 코드를 확장하도록 제약합니다.
  2. **수동 역직렬화**: structured numpy array 캐스팅을 통해 바이너리 버퍼를 정교하게 파싱합니다.
  3. **Crop Box Filter (ROI)**: 전방 20m, 좌우 8m, 높이 -2~2m 범위 외부 포인트들을 NumPy boolean masking 연산으로 제거합니다.
  4. **Downsample Filter (데시메이션)**: 3대1 균등 축소(`[::3]`)를 적용합니다.
  5. **[노드 조립 선택]**: 런치 파일 내부에서 선택된 노드(`lidar_filter_create_cloud_node` 또는 `lidar_filter_tobyte_node`)에 따라 `create_cloud` 방식 혹은 `tobytes()` 바이트 버퍼 수동 직렬화 방식으로 전처리 토픽을 재발행합니다.

---

## 4. 빌드 및 연동 검증 워크플로우

### 🛠️ 4.1 colcon 워크스페이스 빌드
```bash
# 1. 2단계 실습 워크스페이스 홈으로 이동
cd ~/sensor_fusion_practice/step2_ros2_bridge

# 2. 워크스페이스 전체 빌드 수행
colcon build --symlink-install

# 3. 환경 변수 로드
source install/setup.bash
```

### 🚀 4.2 패키지 구동 및 검증
1. **브릿지의 고정밀 라이다 연동 확인**:
   - `carla-ros-bridge`가 `lidar_xyzirc.py` 모듈을 로드하여 6개 필드(XYZIRC)를 정상 퍼블리시하도록 설정 및 스폰 상태를 정렬합니다.
2. **전처리 노드 구동**:
   - `sensor_processing.launch.py` 내의 실행 모드 노드 블록을 설정한 뒤 통합 런치를 구동합니다.
   ```bash
   ros2 launch ros2_sensor_processing sensor_processing.launch.py
   ```
3. 새 터미널을 열어 `rviz2` 또는 토픽 에코 도구를 실행하여 가공 완료된 토픽(`/processed/camera/image`, `/processed/lidar/points`)을 분석 검증합니다.

---

## 📖 이론 강좌: 센서 데이터 포맷 (Sensor Data Format)

자율주행 시스템에서 사용하는 핵심 센서인 카메라와 라이다는 물리적인 현상(빛의 흡수, 레이저의 반사)을 디지털 데이터로 변환합니다. 이 데이터를 연산 장치(CPU/GPU)가 효율적으로 처리할 수 있는 형태로 구성한 규칙을 **센서 데이터 포맷**이라고 합니다.

### 1. 카메라 데이터 포맷 (Camera Data Format)
카메라 센서는 렌즈를 통해 들어온 빛을 2D 이미지 센서(CCD 또는 CMOS) 상의 격자 형태로 배치된 픽셀로 변환합니다.

#### A. 원시 이미지 포맷 (Raw Image Formats)
- **RGB / BGR**:
  - 빛의 3원색인 Red, Green, Blue 채널을 표현합니다.
  - 보통 채널당 8비트(0~255 값)를 할당하여 총 24비트(3바이트)로 한 픽셀을 표현합니다.
  - OpenCV 라이브러리는 역사적인 이유로 BGR 순서를 표준으로 사용하고, PIL(Python Imaging Library)이나 PyTorch 등은 RGB 순서를 주로 사용합니다.
- **RGBA / BGRA**:
  - RGB에 Alpha(투명도 또는 정렬용 패딩 바이트) 채널을 추가한 형태입니다. 
  - 한 픽셀에 32비트(4바이트)를 할당하므로 32비트 컴퓨터 아키텍처에서 메모리 정렬(Memory Alignment)이 최적화되어 빠른 읽기/쓰기가 가능합니다.
  - **CARLA 시뮬레이터의 카메라 API는 기본적으로 BGRA 포맷으로 이미지를 제공합니다.**
- **YUV**:
  - 밝기 정보(Y: Luma)와 색상 정보(U/V: Chrominance)를 분리하여 저장하는 방식입니다.
  - 인간의 눈은 밝기 변화에는 민감하지만 색상 변화에는 둔감하다는 점을 이용하여, Y 채널은 원래 해상도대로 유지하고 U, V 채널의 해상도를 줄여 대역폭을 크게 절약합니다. (예: YUV420 포맷은 RGB 대비 약 50%의 대역폭 감소 효과)

#### B. 압축 이미지 포맷 (Compressed Image Formats)
- **JPEG / PNG**:
  - 카메라에서 전송되는 고해상도(예: FHD, 4K) RGB 데이터를 그대로 전송하면 대역폭이 초과할 수 있어, 이미지 압축 알고리즘을 사용합니다.
  - ROS 2 시스템에서는 대역폭 제약을 줄이기 위해 `sensor_msgs/msg/CompressedImage`를 사용하여 JPEG나 PNG 스트림으로 데이터를 주고받은 뒤, 수신부에서 압축을 풀어 사용합니다.

### 2. 라이다 데이터 포맷 (LiDAR Data Format)
라이다(Light Detection and Ranging)는 레이저 펄스를 쏘아 표면에 부딪혀 돌아오는 시간(ToF, Time of Flight)을 측정합니다. 이를 통해 얻은 수많은 3차원 위치 점들의 집합을 **포인트 클라우드(Point Cloud)**라고 부릅니다.

#### A. 3차원 좌표 (XYZ)
- 리드/라이다 센서 중심을 원점 `(0, 0, 0)`으로 하는 데카르트 좌표계 상의 공간 정보입니다.
- **좌표계 표준 규격 (중요)**:
  - **CARLA (왼손 좌표계 - LHS)**: X축(전방), Y축(우측), Z축(상방)
  - **ROS / Autoware (오른손 좌표계 - RHS)**: X축(전방), Y축(좌측), Z축(상방)
  - 따라서 CARLA 데이터를 ROS 2 환경으로 가져갈 때는 반드시 Y축 데이터의 부호를 반전(`Y_ros = -Y_carla`)해 주어야 공간이 왜곡되지 않습니다.

#### B. 반사도 (Intensity / Reflectivity)
- 레이저 펄스가 반사되어 되돌아온 신호의 세기(강도)입니다.
- 물체의 물리적 재질과 색상에 따라 달라집니다. (예: 차선용 흰색 페인트는 아스팔트보다 반사도가 높음)
- 인공지능 기반 3D Object Detection 모델은 형상 정보(XYZ)뿐만 아니라 반사도(Intensity) 정보를 함께 학습하여 검출 정확도를 높입니다.

#### C. 메타데이터 (Metadata)
- **Ring / Channel ID**: 라이다 채널(VLP-16인 경우 0~15번 채널 레이저) 번호입니다.
- **Timestamp / TimeOffset**: 한 프레임의 라이다 스캔 내에서도 개별 점이 스캔된 정밀한 타임스탬프입니다. (스피닝 라이다는 360도 도는 동안 차량이 이동하므로 왜곡 보정에 타임스탬프가 필요합니다.)

---

## 📖 이론 강좌: 포인트 클라우드 타입 구성 및 ROS 2 데이터 레이아웃

### 1. 알고리즘 요구사항에 따른 포인트 클라우드 타입 설정
라이다 점군을 사용하는 알고리즘(SLAM, 인지 딥러닝, 지면 분석 등)에 따라 Point Cloud 데이터의 구조적 속성을 다르게 구성해야 성능과 자원 효율성을 모두 극대화할 수 있습니다.

| 타입 이름 | 포함 필드 구성 | 크기(Byte/Point) | 주요 사용 분야 및 장단점 |
| :--- | :--- | :--- | :--- |
| **XYZ** | `float32 x, y, z` | 12 Bytes | - **용도**: 기하학적 장애물 매핑, 3D Octomap 생성, 저사양 SLAM<br>- **장점**: 용량이 가장 작고 연산 속도가 빠름.<br>- **단점**: 질감이나 채널 정보가 없어 의미적 인지(Semantic)가 어려움. |
| **XYZI** | `float32 x, y, z, intensity` | 16 Bytes | - **용도**: **Autoware 표준 인지 입력**, 딥러닝 3D Object Detection (PointPillars, PV-RCNN 등)<br>- **장점**: 강도 정보를 기반으로 도로의 차선, 마커, 표지판 식별 가능.<br>- **단점**: XYZ 대비 데이터 크기가 33% 증가함. |
| **XYZIR** | `float32 x, y, z, intensity`<br>`uint16 ring` (또는 `uint8`) | 18~20 Bytes (패딩 포함) | - **용도**: LIO-SAM 등 첨단 SLAM 알고리즘, 실시간 지면 제거(Ground Removal) 필터링<br>- **장점**: 레이저 채널별(Ring)로 묶어서 고속 연산 가능. 정렬되지 않은 원시 데이터를 라인별로 처리하기에 매우 용이.<br>- **단점**: 센서 드라이버가 Ring 인덱스를 제공해야만 파이프라인에서 활용 가능. |
| **XYZIRC** | `float32 x, y, z, intensity`<br>`uint16 ring`<br>`float32 time_offset` | 22~24 Bytes | - **용도**: 고속 주행 시 모션 왜곡 보정(Motion Deskewing)<br>- **장점**: 점마다의 타임스탬프(`time_offset`)를 이용하여 차가 달리는 도중 회전하는 라이다 센서의 모션 롤링 셔터 현상 보정 가능.<br>- **단점**: 연산 알고리즘이 정교해지고 패킷 해석 부하가 높음. |

### 2. ROS 2 PointCloud2 구조와 데이터 레이아웃 이해
ROS 2에서 포인트 클라우드를 다루기 위해 사용하는 메시지는 `sensor_msgs/msg/PointCloud2`입니다. 이 메시지는 직렬화된 바이트 배열(`data`)을 효과적으로 역직렬화하기 위해 다음과 같은 헤더 필드들을 가지고 있습니다.

* `height`: 점군의 이미지 매핑 형태(예: 세로 64채널, 가로 1024 해상도인 경우 64. 정렬되지 않은 경우 1).
* `width`: 한 채널당 속한 점의 개수(또는 전체 점 개수).
* `fields`: 각 점의 세부 구성 정보 리스트 (데이터 오프셋과 타입 정의).
  - 예: `[name='x', offset=0, datatype=FLOAT32]`, `[name='y', offset=4, datatype=FLOAT32]`, `[name='intensity', offset=12, datatype=FLOAT32]`
* `point_step`: 점 하나를 구성하는 바이트 크기 (예: XYZI는 16바이트).
* `row_step`: 포인트 클라우드 한 행을 구성하는 바이트 크기 (`width * point_step`).
* `data`: 실제 직렬화된 원시 바이트 스트림 (빅/리틀 엔디안 구분 포함).

