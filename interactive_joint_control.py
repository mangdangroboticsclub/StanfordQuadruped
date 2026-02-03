#!/usr/bin/env python3
"""
交互式关节控制和实时角度显示
可以手动控制任意关节，并实时查看所有关节的角度
"""

import numpy as np
import time
import math
import os
import sys
from MangDang.mini_pupper.HardwareInterface import HardwareInterface, Joint_checker
from MangDang.mini_pupper.Config import Configuration
from src.State import State

def deg2rad(x):
    return x / 180 * math.pi

def rad2deg(x):
    return x / math.pi * 180

def clear_screen():
    """清屏"""
    os.system('clear' if os.name == 'posix' else 'cls')

def display_compact(joint_angles, joint_checker, title=""):
    """紧凑型显示所有关节角度"""
    clear_screen()
    print("=" * 90)
    print(f"  交互式关节控制 - 实时角度显示  {title}")
    print("=" * 90)
    
    motor_names = ["Motor 1 (Hip)   ", "Motor 2 (Upper) ", "Motor 3 (Lower) "]
    leg_names = ["FR(前右)", "FL(前左)", "BR(后右)", "BL(后左)"]
    
    print(f"\n{'关节':18} {leg_names[0]:>13} {leg_names[1]:>13} {leg_names[2]:>13} {leg_names[3]:>13}")
    print("-" * 90)
    
    for i in range(3):
        angles = [f"{rad2deg(joint_angles[i][j]):7.2f}°" for j in range(4)]
        print(f"{motor_names[i]:18} {angles[0]:>13} {angles[1]:>13} {angles[2]:>13} {angles[3]:>13}")
    
    print("-" * 90)
    print(f"限制触发次数: {joint_checker.cnt}")
    print("=" * 90)

def interactive_control():
    """交互式控制模式"""
    print("=" * 90)
    print("  交互式关节控制 - 实时角度监控")
    print("=" * 90)
    print("\n正在初始化...")
    
    try:
        config = Configuration()
        hardware_interface = HardwareInterface()
        joint_checker = Joint_checker()
        state = State()
        
        print("✓ 硬件初始化成功")
        
        # 选择初始姿态
        print("\n选择初始姿态:")
        print("  1. 站立姿态")
        print("  2. 趴下姿态")
        print("  3. 零位姿态")
        
        choice = input("\n请选择 (1-3，默认1): ").strip() or "1"
        
        if choice == "1":
            state.joint_angles = np.array([
                [0.0, 0.0, 0.0, 0.0],
                [0.8, 0.8, 0.8, 0.8],
                [-1.6, -1.6, -1.6, -1.6]
            ])
            posture_name = "站立姿态"
        elif choice == "2":
            state.joint_angles = np.array([
                [0.0, 0.0, 0.0, 0.0],
                [0.5, 0.5, 0.5, 0.5],
                [-0.8, -0.8, -0.8, -0.8]
            ])
            posture_name = "趴下姿态"
        else:
            state.joint_angles = np.array([
                [0.0, 0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0, 0.0]
            ])
            posture_name = "零位姿态"
        
        print(f"\n正在缓慢移动到{posture_name}...")
        
        # 平滑移动
        target = np.copy(state.joint_angles)
        current = np.zeros_like(target)
        
        for step in range(51):
            ratio = step / 50
            current = target * ratio
            hardware_interface.set_actuator_postions(current)
            time.sleep(0.1)
        
        state.joint_angles = np.copy(current)
        joint_checker.update(state.joint_angles)
        
        print("✓ 完成！")
        time.sleep(1)
        
        # 主控制循环
        motor_names = ["Motor 1 (Hip/髋关节)", "Motor 2 (Upper leg/大腿)", "Motor 3 (Lower leg/小腿)"]
        leg_names = ["FR(前右腿)", "FL(前左腿)", "BR(后右腿)", "BL(后左腿)"]
        
        while True:
            display_compact(state.joint_angles, joint_checker)
            
            print("\n操作菜单:")
            print("  1. 调整单个关节角度")
            print("  2. 调整整条腿的某个关节（4个电机同时）")
            print("  3. 恢复到初始姿态")
            print("  4. 查看角度限制范围")
            print("  q. 退出")
            
            cmd = input("\n请选择: ").strip().lower()
            
            if cmd == 'q':
                break
            
            elif cmd == '1':
                # 单个关节
                print("\n选择要控制的关节:")
                print("  电机: 0=Hip, 1=Upper, 2=Lower")
                print("  腿:   0=FR前右, 1=FL前左, 2=BR后右, 3=BL后左")
                
                try:
                    motor = int(input("电机编号 (0-2): "))
                    leg = int(input("腿编号 (0-3): "))
                    
                    if not (0 <= motor <= 2 and 0 <= leg <= 3):
                        print("❌ 无效输入")
                        time.sleep(1)
                        continue
                    
                    current_deg = rad2deg(state.joint_angles[motor][leg])
                    min_deg = rad2deg(joint_checker.joint_angles_minLimit[motor][leg])
                    max_deg = rad2deg(joint_checker.joint_angles_maxLimit[motor][leg])
                    
                    print(f"\n当前角度: {current_deg:.2f}°")
                    print(f"限制范围: {min_deg:.2f}° ~ {max_deg:.2f}°")
                    
                    target_deg = float(input("目标角度 (度): "))
                    
                    # 平滑移动
                    target_angles = np.copy(state.joint_angles)
                    target_angles[motor][leg] = deg2rad(target_deg)
                    
                    for step in range(21):
                        ratio = step / 20
                        interpolated = state.joint_angles + (target_angles - state.joint_angles) * ratio
                        joint_checker.check_limit(interpolated)
                        hardware_interface.set_actuator_postions(interpolated)
                        time.sleep(0.05)
                    
                    state.joint_angles = np.copy(interpolated)
                    joint_checker.update(state.joint_angles)
                    
                    actual_deg = rad2deg(state.joint_angles[motor][leg])
                    if abs(actual_deg - target_deg) > 0.5:
                        print(f"\n⚠️  角度被限制: {target_deg:.2f}° → {actual_deg:.2f}°")
                        time.sleep(2)
                    
                except ValueError:
                    print("❌ 输入错误")
                    time.sleep(1)
            
            elif cmd == '2':
                # 整条腿的某个关节
                print("\n选择电机类型:")
                print("  0 = Motor 1 (Hip/髋关节)")
                print("  1 = Motor 2 (Upper leg/大腿)")
                print("  2 = Motor 3 (Lower leg/小腿)")
                
                try:
                    motor = int(input("电机编号 (0-2): "))
                    
                    if not (0 <= motor <= 2):
                        print("❌ 无效输入")
                        time.sleep(1)
                        continue
                    
                    print(f"\n当前所有腿的 {motor_names[motor]} 角度:")
                    for leg in range(4):
                        deg = rad2deg(state.joint_angles[motor][leg])
                        print(f"  {leg_names[leg]}: {deg:7.2f}°")
                    
                    target_deg = float(input("\n目标角度 (度，应用到所有4条腿): "))
                    
                    # 平滑移动所有腿
                    target_angles = np.copy(state.joint_angles)
                    for leg in range(4):
                        target_angles[motor][leg] = deg2rad(target_deg)
                    
                    for step in range(21):
                        ratio = step / 20
                        interpolated = state.joint_angles + (target_angles - state.joint_angles) * ratio
                        joint_checker.check_limit(interpolated)
                        hardware_interface.set_actuator_postions(interpolated)
                        time.sleep(0.05)
                    
                    state.joint_angles = np.copy(interpolated)
                    joint_checker.update(state.joint_angles)
                    
                    print("\n✓ 完成")
                    time.sleep(1)
                    
                except ValueError:
                    print("❌ 输入错误")
                    time.sleep(1)
            
            elif cmd == '3':
                # 恢复初始姿态
                print("\n正在恢复初始姿态...")
                
                for step in range(21):
                    ratio = step / 20
                    interpolated = state.joint_angles + (target - state.joint_angles) * ratio
                    hardware_interface.set_actuator_postions(interpolated)
                    time.sleep(0.05)
                
                state.joint_angles = np.copy(target)
                joint_checker.update(state.joint_angles)
                
                print("✓ 完成")
                time.sleep(1)
            
            elif cmd == '4':
                # 显示限制
                clear_screen()
                print("=" * 90)
                print("  关节角度限制范围")
                print("=" * 90)
                
                for leg in range(4):
                    print(f"\n{leg_names[leg]}:")
                    for motor in range(3):
                        min_deg = rad2deg(joint_checker.joint_angles_minLimit[motor][leg])
                        max_deg = rad2deg(joint_checker.joint_angles_maxLimit[motor][leg])
                        current_deg = rad2deg(state.joint_angles[motor][leg])
                        print(f"  {motor_names[motor]:25}: {min_deg:7.2f}° ~ {max_deg:7.2f}°  (当前: {current_deg:7.2f}°)")
                
                input("\n按 Enter 继续...")
        
        print("\n退出程序")
    
    except KeyboardInterrupt:
        print("\n\n程序被中断")
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    interactive_control()
