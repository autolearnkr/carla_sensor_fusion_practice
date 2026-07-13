# ROS 2 센서 전처리 실습 패키지 (`ros2_sensor_processing`)

본 패키지는 CARLA 시뮬레이터 및 브릿지가 퍼블리시하는 자율주행 원시 센서 데이터를 수집하여, 2D 이미지 외곽선 검출 및 3D 점구름 ROI 필터링/데시메이션(다운샘플링) 등의 전처리를 수행하여 실시간으로 재발행하는 실습용 ROS 2 파이썬 노드 패키지입니다.

---

## 🎯 주요 기능 및 노드 역할

### 1. 카메라 이미지 왜곡/가공 노드 (`camera_pipeline_node.py`)
- **역할**: 카메라 이미지 토픽을 구독하여 BGR 매트릭스로 역직렬화한 후 Grayscale 변환 및 Canny Edge 알고리즘을 적용한 흑백 외곽선 영상으로 가공하여 송신합니다.
- **수신**: `/carla/hero/camera/rgb/front/image_raw` (`sensor_msgs/msg/Image`)
- **송신**: `/processed/camera/image` (`sensor_msgs/msg/Image`)

### 2. 3D 라이다 관심구역 필터링 및 다운샘플 노드 (`lidar_filter_create_cloud_node.py`)
- **역할**: 3D LiDAR 점구름 데이터를 structured numpy array로 수동 디코딩한 다음, 자율주행에 필요한 관심 영역(Crop Box ROI)만 추출하고 데이터를 3:1 다운샘플링하여 메시지 용량을 축소합니다.
- **수신**: `/carla/hero/lidar` (`sensor_msgs/msg/PointCloud2`)
- **송신**: `/processed/lidar/points` (`sensor_msgs/msg/PointCloud2`)
- **특징**: 자율주행 표준 규격인 **XYZIRC(24바이트/점 고정밀 포맷)** 정합성 강제 검증 제약 조건이 이식되어 있어, 규격 외 포맷 감지 시 경고 에러 발생.

---

## 🛠️ 실행 및 구동 방법

상위 colcon 워크스페이스인 `step2_ros2_bridge`에서 빌드 및 소스 로드 후 통합 실행할 수 있습니다.

### 1. 패키지 빌드
```bash
# 워크스페이스 홈으로 이동
cd ~/sensor_fusion_practice/step2_ros2_bridge

# 빌드 및 로드
colcon build --packages-select ros2_sensor_processing --symlink-install
source install/setup.bash
```

### 2. 런치 파일을 통한 기동
```bash
# 카메라 및 라이다 전처리 노드 통합 실행
ros2 launch ros2_sensor_processing sensor_processing.launch.py
```
