# CARLA ROS 2 공통 라이브러리 패키지 (`carla_common`)

본 패키지는 CARLA-ROS-Bridge 내 여러 패키지(브릿지 메인, 수동 제어, 객체 스폰 등)에서 공통적으로 필요로 하는 보조 함수와 기본 설정 및 자료구조 변환 인터페이스를 정의한 공통 종속 패키지입니다.

---

## 🎯 주요 역할

1. **공통 유틸리티 제공**:
   - CARLA 좌표 시스템과 ROS 좌표 시스템 간의 정합 연산 및 공통적인 데이터 파싱 유틸리티를 지원합니다.
2. **패키지 빌드 종속성 허브**:
   - 브릿지 구동 전반에 사용되는 변환 인터페이스를 한 곳에 모아 컴파일 및 링크 에러 없이 패키지를 기동할 수 있도록 돕습니다.

---

## 🛠️ 빌드 방법

```bash
# 워크스페이스 홈으로 이동
cd ~/sensor_fusion_practice/step2_ros2_bridge

# 빌드 실행
colcon build --packages-select carla_common --symlink-install
```
