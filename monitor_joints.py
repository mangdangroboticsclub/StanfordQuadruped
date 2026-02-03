#!/usr/bin/env python3
"""
实时关节角度监控程序
注意：由于舵机没有角度反馈，此程序需要与 run_robot.py 配合使用
或者作为测试工具单独运行
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

def display_joint_angles(joint_angles, joint_checker=None, title="实时关节角度监控"):
    """
    以表格形式显示所有关节的角度
    """
    clear_screen()
    
    print("=" * 80)
    print(f"{title:^80}")
    print("=" * 80)
    print(f"\n更新时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 80)
    
    motor_names = ["Motor 1 (Hip/髋关节)      ", 
                   "Motor 2 (Upper leg/大腿)  ", 
                   "Motor 3 (Lower leg/小腿)  "]
    leg_names = ["FR(前右)", "FL(前左)", "BR(后右)", "BL(后左)"]
    
    # 表头
    print(f"\n{'关节类型':25} {leg_names[0]:>12} {leg_names[1]:>12} {leg_names[2]:>12} {leg_names[3]:>12}")
    print("-" * 80)
    
    # 显示每个电机的角度
    for i in range(3):
        angles_deg = [rad2deg(joint_angles[i][j]) for j in range(4)]
        angles_str = [f"{angle:7.2f}°" for angle in angles_deg]
        print(f"{motor_names[i]}:  {angles_str[0]:>12} {angles_str[1]:>12} {angles_str[2]:>12} {angles_str[3]:>12}")
    
    print("-" * 80)
    
    # 如果有 joint_checker，显示限制信息
    if joint_checker is not None:
        print(f"\n角度限制信息:")
        print("-" * 80)
        
        for leg_idx in range(4):
            print(f"\n{leg_names[leg_idx]}:")
            for motor_idx in range(3):
                min_limit = rad2deg(joint_checker.joint_angles_minLimit[motor_idx][leg_idx])
                max_limit = rad2deg(joint_checker.joint_angles_maxLimit[motor_idx][leg_idx])
                current = rad2deg(joint_angles[motor_idx][leg_idx])
                
                # 检查是否接近限制
                warning = ""
                if abs(current - min_limit) < 10 or abs(current - max_limit) < 10:
                    warning = " ⚠️"
                
                print(f"  {motor_names[motor_idx]}: {min_limit:7.2f}° ~ {max_limit:7.2f}° (当前: {current:7.2f}°){warning}")
        
        print(f"\n限制触发总次数: {joint_checker.cnt}")
    
    print("=" * 80)
    print("\n按 Ctrl+C 退出")

def monitor_realtime():
    """实时监控关节角度"""
    print("=" * 80)
    print("  关节角度实时监控程序")
    print("=" * 80)
    print("\n正在初始化硬件接口...")
    
    try:
        config = Configuration()
        hardware_interface = HardwareInterface()
        joint_checker = Joint_checker()
        state = State()
        
        print("✓ 硬件接口初始化成功")
        
        # 移动到站立姿态以便监控
        print("\n⚠️  注意：舵机没有角度反馈功能，程序将先移动到站立姿态")
        print("然后开始监控角度变化\n")
        
        print("选择初始姿态:")
        print("  1. 站立姿态（默认）")
        print("  2. 趴下姿态")
        print("  3. 零位姿态")
        
        posture_choice = input("\n请选择 (1-3，默认1): ").strip() or "1"
        
        if posture_choice == "1":
            state.joint_angles = np.array([
                [0.0, 0.0, 0.0, 0.0],
                [0.8, 0.8, 0.8, 0.8],
                [-1.6, -1.6, -1.6, -1.6]
            ])
            print("\n正在缓慢移动到站立姿态...")
        elif posture_choice == "2":
            state.joint_angles = np.array([
                [0.0, 0.0, 0.0, 0.0],
                [0.5, 0.5, 0.5, 0.5],
                [-0.8, -0.8, -0.8, -0.8]
            ])
            print("\n正在缓慢移动到趴下姿态...")
        else:
            state.joint_angles = np.array([
                [0.0, 0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0, 0.0]
            ])
            print("\n正在缓慢移动到零位姿态...")
        
        # 平滑移动到目标姿态
        target_angles = np.copy(state.joint_angles)
        current_angles = np.zeros_like(target_angles)
        
        steps = 50
        for step in range(steps + 1):
            ratio = step / steps
            current_angles = target_angles * ratio
            hardware_interface.set_actuator_postions(current_angles)
            time.sleep(0.1)
        
        state.joint_angles = np.copy(current_angles)
        joint_checker.update(state.joint_angles)
        
        print("✓ 姿态设置完成")
        print("\n📊 开始实时监控当前姿态角度...")
        print("💡 提示：这个程序显示的是最后一次设置的角度")
        print("   如果要监控机器人运动，请在另一个终端运行 run_robot.py")
        print("   或使用测试程序（如 test_single_joint.py）来改变角度\n")
        time.sleep(2)
        
        update_interval = 0.5  # 500ms 更新一次
        last_update = time.time()
        
        while True:
            now = time.time()
            if now - last_update >= update_interval:
                last_update = now
                
                # 显示当前角度（注意：这是程序记录的角度，不是从硬件读取的）
                display_joint_angles(state.joint_angles, joint_checker)
            
            time.sleep(0.05)
    
    except KeyboardInterrupt:
        print("\n\n监控已停止")
        print("=" * 80)
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()

def monitor_with_stats():
    """带统计信息的监控模式"""
    print("=" * 80)
    print("  关节角度监控 - 统计模式")
    print("=" * 80)
    print("\n正在初始化...")
    
    try:
        config = Configuration()
        hardware_interface = HardwareInterface()
        joint_checker = Joint_checker()
        state = State()
        
        print("✓ 初始化成功")
        
        # 移动到站立姿态
        print("\n⚠️  舵机没有角度反馈，将先移动到站立姿态")
        
        state.joint_angles = np.array([
            [0.0, 0.0, 0.0, 0.0],
            [0.8, 0.8, 0.8, 0.8],
            [-1.6, -1.6, -1.6, -1.6]
        ])
        
        print("正在移动...")
        target_angles = np.copy(state.joint_angles)
        current_angles = np.zeros_like(target_angles)
        
        steps = 50
        for step in range(steps + 1):
            ratio = step / steps
            current_angles = target_angles * ratio
            hardware_interface.set_actuator_postions(current_angles)
            time.sleep(0.1)
        
        state.joint_angles = np.copy(current_angles)
        joint_checker.update(state.joint_angles)
        
        print("✓ 姿态设置完成")
        print("\n开始监控（将记录最大/最小角度）...")
        print("提示：运行 run_robot.py 来移动机器人，此程序将监控角度变化")
        time.sleep(2)
        
        # 记录最大最小值
        max_angles = np.copy(state.joint_angles)
        min_angles = np.copy(state.joint_angles)
        start_time = time.time()
        
        update_interval = 0.2
        last_update = time.time()
        
        while True:
            now = time.time()
            if now - last_update >= update_interval:
                last_update = now
                
                # 更新最大最小值
                max_angles = np.maximum(max_angles, state.joint_angles)
                min_angles = np.minimum(min_angles, state.joint_angles)
                
                # 显示
                clear_screen()
                print("=" * 80)
                print(f"{'关节角度监控 - 统计模式':^80}")
                print("=" * 80)
                print(f"\n运行时间: {now - start_time:.1f}秒")
                print(f"更新时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
                print("-" * 80)
                
                motor_names = ["Motor 1 (Hip)", "Motor 2 (Upper)", "Motor 3 (Lower)"]
                leg_names = ["FR(前右)", "FL(前左)", "BR(后右)", "BL(后左)"]
                
                print(f"\n当前角度:")
                print(f"{'':20} {leg_names[0]:>12} {leg_names[1]:>12} {leg_names[2]:>12} {leg_names[3]:>12}")
                print("-" * 80)
                for i in range(3):
                    angles = [f"{rad2deg(state.joint_angles[i][j]):7.2f}°" for j in range(4)]
                    print(f"{motor_names[i]:20} {angles[0]:>12} {angles[1]:>12} {angles[2]:>12} {angles[3]:>12}")
                
                print(f"\n最大角度:")
                print(f"{'':20} {leg_names[0]:>12} {leg_names[1]:>12} {leg_names[2]:>12} {leg_names[3]:>12}")
                print("-" * 80)
                for i in range(3):
                    angles = [f"{rad2deg(max_angles[i][j]):7.2f}°" for j in range(4)]
                    print(f"{motor_names[i]:20} {angles[0]:>12} {angles[1]:>12} {angles[2]:>12} {angles[3]:>12}")
                
                print(f"\n最小角度:")
                print(f"{'':20} {leg_names[0]:>12} {leg_names[1]:>12} {leg_names[2]:>12} {leg_names[3]:>12}")
                print("-" * 80)
                for i in range(3):
                    angles = [f"{rad2deg(min_angles[i][j]):7.2f}°" for j in range(4)]
                    print(f"{motor_names[i]:20} {angles[0]:>12} {angles[1]:>12} {angles[2]:>12} {angles[3]:>12}")
                
                print(f"\n角度范围:")
                print(f"{'':20} {leg_names[0]:>12} {leg_names[1]:>12} {leg_names[2]:>12} {leg_names[3]:>12}")
                print("-" * 80)
                for i in range(3):
                    ranges = [f"{rad2deg(max_angles[i][j] - min_angles[i][j]):7.2f}°" for j in range(4)]
                    print(f"{motor_names[i]:20} {ranges[0]:>12} {ranges[1]:>12} {ranges[2]:>12} {ranges[3]:>12}")
                
                print("=" * 80)
                print("\n按 Ctrl+C 退出")
            
            time.sleep(0.05)
    
    except KeyboardInterrupt:
        print("\n\n监控已停止")
        print("=" * 80)
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("  关节角度实时监控")
    print("=" * 80)
    print("\n选择监控模式:")
    print("  1. 实时监控（显示当前角度和限制信息）")
    print("  2. 统计模式（记录最大/最小角度）")
    print()
    
    choice = input("请选择 (1/2，默认1): ").strip() or "1"
    
    if choice == "2":
        monitor_with_stats()
    else:
        monitor_realtime()
