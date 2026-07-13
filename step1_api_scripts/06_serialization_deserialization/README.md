# 실습 1-6: 1차원 이진 바이트 스트림 수동 직렬화 및 소켓 역직렬화 (06_serialization_deserialization)

본 실습에서는 자율주행 센서 데이터가 네트워크(예: ROS 2 DDS, TCP/UDP 소켓)를 통해 유통되는 저수준(Low-Level) 메커니즘을 상세히 다룹니다. 메모리 상의 다차원 넘파이 배열 데이터를 **1차원 바이트 스트림(Raw Byte Stream)으로 직렬화(Serialization)**하고, 소켓 통신으로 이를 루프백 전송하여 수신 측에서 메모리 포인터 캐스팅 기법으로 원형을 복구하는 **수동 역직렬화(Deserialization)** 원리를 완성합니다.

---

## 🎯 학습 목표
1. 메모리 정렬 및 데이터 규격(dtype)에 따른 바이트 크기를 직접 판독할 수 있습니다.
2. OpenCV 2D 영상 배열 데이터를 1차원 플랫 바이트 버퍼로 직렬화하여 송신하는 데이터 직렬화 원리를 이해합니다.
3. 역직렬화 전 데이터의 타입 정보, 전체 바이트 길이, 그리고 날것(raw)의 Hex Dump(16진수) 덤프 코드를 로깅하여 패킷의 정합성을 직접 모니터링합니다.
4. UDP 소켓 통신 수신 루프 내에서 NumPy 고속 포인터 캐스팅을 적용하여 수동 역직렬화를 구현합니다.

---

## 📂 실습 구성 파일
* **[23_raw_deserialization_viewer.py](23_raw_deserialization_viewer.py)**: 파일로 수집된 1차원 이진 바이트 버퍼(`.bin`)를 메모리 캐스팅하여 원래 3D 라이다 XYZI 좌표 배열 정보로 역직렬화 복구 모니터링.
* **[24_image_processor_node.py](24_image_processor_node.py)**: 수집된 카메라 데이터를 실시간 90도 회전 수동 변환 후, `.tobytes()` 1차원 직렬화 데이터로 조립하여 로컬 포트(5005)로 UDP 루프백 송신하는 발신기 노드.
* **[25_deserialization_socket_viewer.py](25_deserialization_socket_viewer.py)**: **[이진 패킷 분석 완성판]** 포트 5005로 유통되는 이진 날것의 바이너리 버퍼 타입 정보, 총 데이터 바이트 길이, 전면 20바이트 Hex Dump를 실시간으로 화면에 로깅한 뒤, 2D BGR 프레임으로 수동 캐스팅 역직렬화하여 OpenCV 창에 노출시키는 수신기 노드.

---

## 🛠️ 주요 코드 포인트 (학습 포인트)
### 1. 직렬화(Serialization): 메모리 레이아웃 ➔ 1차원 이진 바이트
```python
# 1. 2D BGR 넘파이 배열 데이터를 [Height * Width * 3] 1차원 이진 바이트 버퍼로 수동 직렬화
serialized_data = image_bgr.tobytes()

# 2. 소켓 통신을 이용한 UDP 이진 전송
sock.sendto(serialized_data, (UDP_IP, UDP_PORT))
```

### 2. 패킷 유통 디버깅: 바이너리 정보 및 20바이트 Hex Dump 로깅
```python
# 역직렬화 직전에 이진 날것의 속성(바이트 타입 및 패킷 크기)을 로깅
self.get_logger().info(f"Packet Received: {type(data)} | Size: {len(data)} Bytes")

# 날것(raw) 상태의 전면 20바이트 데이터를 16진수(Hex Dump)로 터미널에 디버그 출력
hex_dump = " ".join(f"{b:02x}" for b in data[:20])
self.get_logger().info(f"Raw binary 20B Hex Dump: [ {hex_dump} ]")
```

### 3. 역직렬화(Deserialization): 고속 메모리 캐스팅 복구
```python
# 1. 수신 바이트 버퍼를 카피 복사 없이 1차원 UNIT8 배열로 메모리 뷰 캐스팅
flat_arr = np.frombuffer(received_bytes, dtype=np.uint8)
# 2. 송신 측 규격(600, 800, 3)에 일치하도록 차원 재정렬(Reshape) 수행
recovered_image = flat_arr.reshape((height, width, 3))
```

---

## 🚀 실습 실행 순서
1. **바이너리 파일 강제 복구 시험**:
   이전에 저장되었던 라이다 raw 이진 파일을 메모리 캐스팅으로 파싱하여 점구름 렌더링에 성공하는지 확인합니다.
   ```bash
   python3 23_raw_deserialization_viewer.py
   ```
2. **소켓 기반 실시간 직/역직렬화 루프백 기동**:
   터미널 1을 열고 수동 역직렬화 수신 노드를 대기 기동합니다.
   ```bash
   python3 25_deserialization_socket_viewer.py
   ```
   터미널 2를 열고 실시간 회전 직렬화 송신 노드를 기동합니다.
   ```bash
   python3 24_image_processor_node.py
   ```
   수신 측 터미널에 실시간으로 **수신 바이트 크기(예: 1,440,000 바이트)**와 **16진수 Hex Dump**가 실시간으로 흘러가고, 최종 이미지 창에 90도 회전된 카메라 뷰가 올바른 컬러로 렌더링되는지 관찰 및 디버그합니다.

---

## 📖 이론 강좌: 직렬화(Serialization)와 역직렬화(Deserialization)

### 1. 정의 및 기술적 필요성
* **직렬화 (Serialization)**:
  - RAM 메모리상에 퍼져 있거나 다차원 구조(예: Python의 리스트 객체, NumPy의 행렬 구조체)로 보관되어 있는 데이터를 네트워크 전송 혹은 파일 저장이 가능하도록 1차원의 연속적인 **바이트 배열(Byte Array / Byte Stream)**로 변환하는 과정을 말합니다.
* **역직렬화 (Deserialization)**:
  - 수신된 1차원 바이트 스트림 데이터를 특정 오프셋(Offset)과 데이터 타입에 따라 복합 데이터 구조(예: 구조체, 다차원 Numpy Array, ROS 메시지 객체)로 메모리에 재배치하여 복원하는 과정입니다.

### 2. 직렬화/역직렬화가 자율주행 통신에서 필수적인 이유
1. **이기종 통신망의 통일**:
   - CARLA 엔진(C++)에서 생성된 데이터를 파이썬 제어 스크립트(Python)로 전송하고, 이를 다시 ROS 2(C++/Python) 노드가 수신합니다. 언어와 플랫폼 간 메모리 표현 방식이 다르므로, 물리 통신망 상에서는 **바이트 스트림**이라는 단 하나의 표준 언어만 사용해야 합니다.
2. **효율성과 처리 속도 (Latency)**:
   - 고속 자율주행에서는 1초에 기가바이트 단위의 센서 데이터가 생성됩니다. 비효율적인 포맷(예: JSON, XML)으로 직렬화하면 파싱 부하가 매우 큽니다. 따라서 고속 직렬화가 가능한 **바이너리 직렬화(FlatBuffers, Protocol Buffers, ROS CDR serialization)** 기법을 사용합니다.
3. **엔디안(Endianness) 해결**:
   - 시스템마다 데이터를 바이트 단위로 저장하는 순서(Little Endian vs Big Endian)가 다릅니다. 직렬화 포맷은 데이터 송수신 시 바이트 순서를 고정하여 깨짐을 방지합니다.
