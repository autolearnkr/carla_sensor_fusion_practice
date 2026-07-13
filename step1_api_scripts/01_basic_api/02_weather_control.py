#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
실습 02: 시뮬레이터 날씨 및 시간 동적 변경 (초급)

이 스크립트는 시뮬레이션 환경의 날씨(구름, 비, 바람, 노면 물 고임 등)와 
태양의 고도/방위각(시간대 변경)을 API를 사용하여 동적으로 변경해 보는 실습입니다.
"""

import sys
import time

try:
    import carla
except ImportError:
    print("Error: 'carla' python module is not installed. Please check your CARLA setup.", file=sys.stderr)
    sys.exit(1)

def main():
    print("Connecting to CARLA Server...")
    client = carla.Client('localhost', 2000)
    client.set_timeout(10.0)

    try:
        world = client.get_world()
        
        # 1. 현재 날씨 상태 조회
        current_weather = world.get_weather()
        print(f"Current weather details: Cloudiness={current_weather.cloudiness}, Precipitation={current_weather.precipitation}")

        # 2. 프리셋 기후 변경
        print("\nChanging weather to [WetNoon] preset...")
        world.set_weather(carla.WeatherParameters.WetNoon)
        time.sleep(2.0)

        print("Changing weather to [ClearSunset] preset...")
        world.set_weather(carla.WeatherParameters.ClearSunset)
        time.sleep(2.0)

        # 3. 사용자 정의 파라미터 조작
        print("\nConfiguring custom weather parameters...")
        custom_weather = carla.WeatherParameters(
            cloudiness=80.0,
            precipitation=50.0,
            precipitation_deposits=40.0,
            wind_intensity=60.0,
            sun_azimuth_angle=0.0,
            sun_altitude_angle=15.0
        )
        world.set_weather(custom_weather)
        print("Custom weather set.")
        
        # 4. 실시간 시간 변이 에뮬레이션
        print("\nSimulating real-time sunset transition for 5 seconds...")
        for step in range(50):
            custom_weather.sun_altitude_angle -= 0.5
            world.set_weather(custom_weather)
            time.sleep(0.1)
            
        print("Sunset transition simulation finished. Restoring default clear weather...")
        world.set_weather(carla.WeatherParameters.Default)

    except Exception as e:
        print(f"Error occurred: {e}", file=sys.stderr)

if __name__ == '__main__':
    main()
