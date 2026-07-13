# 실습 1-2: RGB 카메라 센서 장착 및 이미지 가공 (02_group_camera)

본 실습에서는 에고 차량(Ego Vehicle)에 카메라 센서를 부착하여 이미지 프레임을 획득하고, 수신된 1차원 바이트 버퍼를 2D RGB/BGR 행렬 데이터로 역직렬화하여 실시간 OpenCV 렌더링 및 이미지 가공(90도 수동 회전)을 구현합니다.

---

## 🎯 학습 목표
1. 카메라 센서를 차량에 동적으로 마운트(Attach)하는 물리 구조(Sensor Attachment)를 이해합니다.
2. `sensor.listen(lambda data: ...)` 비동기 콜백을 등록하여 센서 원시 바이트 데이터를 획득합니다.
3. BGRA 형태의 1차원 이진 바이트 스트림을 NumPy 배열 연산을 거쳐 OpenCV 표준 `BGR` 이미지 프레임으로 변환할 수 있습니다.
4. 이미지 축 변환 및 회전 수학 공식을 적용하여 실시간으로 이미지를 90도 회전(수동 전처리)할 수 있습니다.

---

## 📂 실습 구성 파일
* **[07_spectator_follow.py](07_spectator_follow.py)**: 스폰된 에고 차량을 실시간 3D 위치 추적하여 Spectator 카메라를 자동 동기화.
* **[08_carla_attach_camera.py](08_carla_attach_camera.py)**: 기존에 생성된 차량에 전방 RGB 카메라 센서를 결속(Attach)시키는 동적 기동 스크립트.
* **[09_carla_view_camera.py](09_carla_view_camera.py)**: 장착된 카메라 센서의 원시 바이트 데이터를 실시간 수신하여 OpenCV BGR 창에 렌더링.
* **[10_carla_view_camera_rotated.py](10_carla_view_camera_rotated.py)**: 카메라 이미지 데이터를 수신 즉시 90도 수동 회전 전처리하여 윈도우에 렌더링.
* **[11_carla_camera_view.py](11_carla_camera_view.py)**: 차량 스폰, 카메라 장착 및 뷰 모니터링을 단일 스레드 내에서 원스톱으로 처리하는 종합 스크립트.

---

## 🛠️ 주요 코드 포인트 (학습 포인트)
### 1. 카메라 센서 부착 파라미터 및 결속
```python
camera_bp = blueprint_library.find('sensor.camera.rgb')
camera_bp.set_attribute('image_size_x', '800')
camera_bp.set_attribute('image_size_y', '600')
camera_bp.set_attribute('fov', '90')

camera_transform = carla.Transform(carla.Location(x=1.5, z=2.4))
camera = world.spawn_actor(camera_bp, camera_transform, attach_to=vehicle)
```
* 차량의 전방 범퍼/루프 기준 상대 좌표(`x=1.5`, `z=2.4`)에 센서를 결속(`attach_to=vehicle`)합니다.

### 2. BGRA ➔ BGR 이진 역직렬화 및 OpenCV 연동
```python
def process_img(image):
    # 1. 1차원 raw_data 바이트 스트림을 4채널 BGRA 형태의 2차원 NumPy 배열로 복구
    raw = np.frombuffer(image.raw_data, dtype=np.uint8)
    img_bgra = raw.reshape((image.height, image.width, 4))
    # 2. RGB 표준 렌더링을 위해 Alpha(A) 채널을 제거하고 BGR 3채널로 변환
    img_bgr = img_bgra[:, :, :3]
    
    cv2.imshow("Camera View", img_bgr)
    cv2.waitKey(1)
```

---

## 🚀 실습 실행 순서
1. **카메라 통합 기동 스크립트 실행**:
   차량이 스폰되고, 전방 카메라 뷰어가 독립 윈도우로 화면에 렌더링되는지 확인합니다.
   ```bash
   python3 11_carla_camera_view.py
   ```
2. **다중 프로세스/모듈러 리스너 실습**:
   터미널 1에서 차량과 카메라를 장착시킵니다:
   ```bash
   python3 08_carla_attach_camera.py
   ```
   터미널 2에서 카메라가 발행하는 이미지를 가로채 90도 회전 렌더링하는 전처리 노드를 단독 기동합니다:
   ```bash
   python3 10_carla_view_camera_rotated.py
   ```


