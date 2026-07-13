#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
실습 21: 공식 manual_control.py 구동 및 제어 매핑 분석 (고급)

이 스크립트는 시뮬레이션 환경에서 차량을 키보드로 안전하고 정교하게 주행시킬 수 있도록,
CARLA 공식 수동제어 스크립트인 [manual_control.py]를 서브프로세스 연동을 통해 구동하고
해당 코드 내부의 키 매핑 클래스(`KeyboardControl`)와 HUD 정보 출력 원리를 분석합니다.
"""

import sys
import subprocess
import os

def main():
    print("--- 실습 21: 공식 manual_control.py 구동 및 연동 ---")

    workspace_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    official_script_path = os.path.join(workspace_dir, "PythonAPI", "examples", "manual_control.py")
    
    print(f"Target official script path:\n {official_script_path}")
    
    if not os.path.exists(official_script_path):
        print(f"\n[Error] Official manual_control.py not found at expected path!", file=sys.stderr)
        return

    print("\n=======================================================")
    print("      CARLA 공식 수동 제어 키 매핑 조작법 (학습용)")
    print("=======================================================")
    print("  [차량 주행 제어]")
    print("    - W : 가속 (Throttle)")
    print("    - S : 제동 / 감속 (Brake)")
    print("    - A / D : 좌측 / 우측 조향 (Steer)")
    print("    - Q : 후진 변속 토글 (Q를 누르고 W를 누르면 후진)")
    print("    - Space : 핸드 브레이크")
    print("  [카메라 뷰 변경]")
    print("    - Tab : 카메라 위치 변경 (3인칭 -> 1인칭 -> 대시보드)")
    print("  [시뮬레이터 제어]")
    print("    - P : Autopilot 모드 활성화")
    print("    - ESC : 프로그램 종료")
    print("=======================================================")

    print(f"\nLaunching official manual_control.py process...")
    try:
        python_executable = sys.executable
        process = subprocess.Popen([python_executable, official_script_path], cwd=os.path.join(workspace_dir, "PythonAPI", "examples"))
        process.wait()
        print("\nManual control process closed.")
    except KeyboardInterrupt:
        process.terminate()
    except Exception as e:
        print(f"Failed to launch process: {e}", file=sys.stderr)

if __name__ == '__main__':
    main()
