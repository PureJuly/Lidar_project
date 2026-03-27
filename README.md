# 🐢 ROS 2 Lidar 모의 주행 및 데이터 수집 프로젝트

## 📌 프로젝트 개요
본 프로젝트는 ROS 2(Humble) 환경에서 Lidar 센서 모의 데이터를 생성하고, 이를 바탕으로 Turtlesim 거북이의 자율 주행을 제어하며 실시간 주행 데이터를 MySQL 데이터베이스에 적재하는 통합 시스템입니다. 수집된 Lidar 배열 데이터는 데이터 분석을 위해 Pandas DataFrame(361개 컬럼)으로 파싱할 수 있도록 구현되었습니다.

## 🛠️ 기술 스택
* **OS:** Ubuntu 22.04 (WSL2) & Windows 11
* **ROS 2:** Humble Hawksbill (Turtlesim, Rosbridge)
* **Language:** Python 3.10
* **Database:** MySQL 8.0
* **Libraries:** `roslibpy`, `rclpy`, `pymysql`, `pandas`, `json`

## ✨ 주요 기능

1. **모의 Lidar 데이터 퍼블리싱 (`lidar_project_publisher.py`)**
   * 2초마다 `front_wall`, `left_wall`, `right_wall`, `no_wall` 4가지 패턴 중 하나를 랜덤으로 생성.
   * `sensor_msgs/LaserScan` 타입으로 `/scan` 토픽에 퍼블리시.
   * 생성된 센서 데이터를 로컬 JSON 파일로도 저장(`lds02_dataset/`).

2. **장애물 회피 제어기 (`ros_connector.py`)**
   * `roslibpy` 웹소켓을 통해 `/scan` 토픽 구독 및 `/turtle1/cmd_vel` 토픽 발행.
   * Lidar 데이터를 3개 구역(정면, 좌, 우)으로 나누어 안전 거리(1.0m) 이내 진입 시 장애물 회피(`turn_left`, `turn_right`, `move_front`) 모션 결정.

3. **DB 실시간 적재 및 데이터 파싱 (`db_connector.py`)**
   * MySQL 데이터베이스와 연동하여 테이블(`lidardata`) 초기화 및 생성.
   * 결정된 액션(action), 시간(when_), Lidar 거리 배열(ranges)을 JSON 형태로 실시간 `INSERT`.
   * DB에 저장된 JSON 데이터를 파이썬으로 불러와 **360개의 거리 컬럼 + 1개의 액션 컬럼(총 361개 컬럼)**의 Pandas DataFrame으로 파싱.

## 📂 파일 구조
```text
📦 project_root
 ┣ 📜 lidar_project_publisher.py # ROS 2 네이티브 퍼블리셔 (rclpy)
 ┣ 📜 ros_connector.py           # 웹소켓 기반 메인 제어기 (roslibpy)
 ┗ 📜 db_connector.py            # MySQL 연동 및 데이터 파싱 모듈 (pymysql, pandas)
```

## 🚀 실행 방법

### 1. 사전 준비
* **ROS 2 패키지 설치:** 우분투 터미널에서 아래 명령어로 필요 패키지를 설치합니다.
  ```bash
  sudo apt install ros-humble-turtlesim ros-humble-rosbridge-server
  ```
* **Python 라이브러리 설치:** 제어 및 DB 연동을 위한 라이브러리를 설치합니다.
  ```bash
  pip install roslibpy pymysql pandas
  ```
* **데이터베이스 세팅:** 윈도우(또는 로컬) MySQL에 `ros` 데이터베이스를 생성하고, `ros_connector.py`, `db_connector.py` 하단 실행문에 입력한 HOST 정보와 IP 주소(vEthernet)가 맞게 설정되어 있는지 확인합니다.

  **확인방법:** `cmd` 명령 실행하여 `ipconfig` 명령 입력 후 `vEthernet IPv4` 주소 확인

  

### 2. 노드 실행 (터미널 4개 분할)
총 4개의 우분투 터미널을 열고, 각각의 터미널에서 ROS 2 환경 세팅(`source /opt/ros/humble/setup.bash`)을 진행한 뒤 아래 명령어를 순서대로 실행합니다.

**Terminal 1: Turtlesim 노드 실행**
거북이 시뮬레이션 화면을 띄웁니다.
```bash
ros2 run turtlesim turtlesim_node
```

**Terminal 2: Rosbridge 서버 실행**
파이썬 제어기가 ROS 2 토픽과 통신할 수 있도록 웹소켓 다리를 놓아줍니다.
```bash
ros2 launch rosbridge_server rosbridge_websocket_launch.xml
```

**Terminal 3: 모의 Lidar 퍼블리셔 실행**
가상의 벽(장애물) 패턴을 생성하여 `/scan` 토픽으로 쏘아줍니다.
```bash
python3 lidar_project_publisher.py
```

**Terminal 4: 메인 자율주행 제어기 실행**
Lidar 데이터를 받아 거북이를 조종하고, 그 기록을 실시간으로 DB에 저장합니다.
```bash
python3 ros_connector.py
```

## 📊 데이터 분석 파싱 결과
`db_connector.py`를 단독으로 실행하면, DB에 쌓인 데이터를 아래와 같은 361개 컬럼의 Pandas DataFrame으로 확인할 수 있습니다.
```python
# DataFrame Shape: (N, 361)
# Columns: angle_0, angle_1, ..., angle_359, action
       angle_0   angle_1  ...  angle_359       action
0          3.5       3.5  ...        3.5   move_front
1          0.4       0.4  ...        0.4   turn_right
2          3.5       3.5  ...        3.5    turn_left
```
