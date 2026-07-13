#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
실습 17: 자동 비상 제동 (AEB) 시뮬레이션 (고급 - 단독형)

이 스크립트는 차량을 전방에 장애물로 배치하고, 주행 중인 에고 차량의 현재 속도 정보를 
추출하여 장애물 차량과의 Euclidean 3차원 거리를 실시간으로 연산한 뒤,
충돌 임계 제동 구간(안전 마진 7m) 안으로 진입 시 즉각 비상 자동 제동(brake=1.0)을 수행하는 실습입니다.
"""

import sys
import time
import math

try:
    import carla
except ImportError:
    print("Error: 'carla' python module is not installed. Please check your CARLA setup.", file=sys.stderr)
    sys.exit(1)

def get_distance(loc1, loc2):
    return math.sqrt((loc1.x - loc2.x)**2 + (loc1.y - loc2.y)**2 + (loc1.z - loc2.z)**2)

def main():
    actor_list = []
    print("Connecting to CARLA Server on localhost:2000...")
    client = carla.Client('127.0.0.1', 2000)
    client.set_timeout(10.0)
    
    try:
        world = client.get_world()
        blueprint_library = world.get_blueprint_library()
        
        # 에고 차량 스폰
        vehicle_bp = blueprint_library.find('vehicle.dodge.charger_police_2020')
        spawn_points = world.get_map().get_spawn_points()
        ego_spawn_point = spawn_points[0]
        
        print("Spawning Ego Vehicle...")
        ego_vehicle = world.spawn_actor(vehicle_bp, ego_spawn_point)
        actor_list.append(ego_vehicle)
        
        # 25m 전방 Tesla 장애물 차량 스폰
        obstacle_bp = blueprint_library.find('vehicle.tesla.model3')
        forward_vector = ego_spawn_point.get_forward_vector()
        obstacle_location = ego_spawn_point.location + (forward_vector * 25.0)
        obstacle_spawn_point = carla.Transform(obstacle_location, ego_spawn_point.rotation)
        
        print("Spawning Obstacle Vehicle 25m ahead...")
        obstacle_vehicle = world.spawn_actor(obstacle_bp, obstacle_spawn_point)
        actor_list.append(obstacle_vehicle)
        
        obstacle_vehicle.set_target_velocity(carla.Vector3D(0, 0, 0))
        
        # 출발 제어
        print("Ego Vehicle starting to accelerate forward...")
        ego_vehicle.apply_control(carla.VehicleControl(throttle=0.4))
        
        safety_threshold = 7.0
        aeb_triggered = False
        
        while True:
            time.sleep(0.05)
            
            ego_loc = ego_vehicle.get_location()
            obs_loc = obstacle_vehicle.get_location()
            
            distance = get_distance(ego_loc, obs_loc)
            ego_speed = ego_vehicle.get_velocity()
            speed_kmh = 3.6 * math.sqrt(ego_speed.x**2 + ego_speed.y**2 + ego_speed.z**2)
            
            print(f"Current Distance: {distance:.2f} m | Ego Speed: {speed_kmh:.1f} km/h")
            
            if distance < safety_threshold and not aeb_triggered:
                print("\n=======================================================")
                print("🚨🚨 WARNING: COLLISION IMMINENT! AEB TRIGGERED! 🚨🚨")
                print("=======================================================")
                ego_vehicle.apply_control(carla.VehicleControl(throttle=0.0, brake=1.0, hand_brake=True))
                aeb_triggered = True
            
            if aeb_triggered:
                if speed_kmh < 0.1:
                    print("\nVehicle successfully stopped safely before collision.")
                    break
                    
    except KeyboardInterrupt:
        print("\nCancelled by user.")
    except Exception as e:
        print(f"Error occurred: {e}", file=sys.stderr)
    finally:
        print("Cleaning up spawned actors...")
        for actor in actor_list:
            if actor.is_alive:
                actor.destroy()
        print("Cleanup completed. Exiting.")

if __name__ == '__main__':
    main()
