#!/usr/bin/env python3
"""
单关节安全测试程序
专门用于测试单个关节的角度限制，避免多关节同时移动导致断电
"""

import numpy as np
import time
import math
import sys
from MangDang.mini_pupper.HardwareInterface import HardwareInterface, Joint_checker
from MangDang.mini_pupper.Config import Configuration, ENABLE_JOINT_LIMITS

def deg2rad(x):
    return x / 180 * math.pi

def rad2deg(x):
    return x / math.pi * 180

def read_current_angles(hardware_interface):
    """
    读取当前所有关节的实际角度
    注意：这个函数返回的是从servo_params读取的理论角度
    实际硬件角度需要通过其他方式获取
    """
    # 由于硬件限制，我们使用上一次设置的角度作为参考
    # 实际应用中，如果有编码器可以读取真实角度
    return None

def display_all_angles(joint_angles, title="当前关节角度"):
    """显示所有关节的角度"""
    print(f"\n{'='*60}")
    print(f"{title}")
    print(f"{'='*60}")
    
    motor_names = ["Motor 1 (Hip)      ", "Motor 2 (Upper leg)", "Motor 3 (Lower leg)"]
    leg_names = ["FR(前右)", "FL(前左)", "BR(后右)", "BL(后左)"]
    
    print(f"\n{'':20} {leg_names[0]:>12} {leg_names[1]:>12} {leg_names[2]:>12} {leg_names[3]:>12}")
    print("-" * 60)
    
    for i in range(3):
        angles = [f"{rad2deg(joint_angles[i][j]):7.2f}°" for j in range(4)]
        print(f"{motor_names[i]}:  {angles[0]:>12} {angles[1]:>12} {angles[2]:>12} {angles[3]:>12}")
    
    print("="*60)

def safe_test_single_motor():
    """安全地测试单个电机的角度限制"""
    print("="*60)
    print("单关节安全测试程序 - 实时角度监控版")
    print("="*60)
    
    # 显示角度限制状态（从全局配置读取）
    print(f"\n全局配置: ENABLE_JOINT_LIMITS = {ENABLE_JOINT_LIMITS}")
    
    config = Configuration()
    hardware_interface = HardwareInterface()
    joint_checker = Joint_checker()
    
    if joint_checker.enabled:
        print("✅ 角度限制: 已启用 (全局配置)")
    else:
        print("⚠️  角度限制: 已关闭 (全局配置) - 请小心操作！")
    
    print("\n⚠️  重要说明：")
    print("   由于硬件限制，程序无法读取舵机的当前实际角度")
    print("   为避免机器狗突然跳变，需要先移动到一个已知的安全姿态\n")
    
    # 提供几种预设姿态
    print("请选择起始姿态:")
    print("1. 站立姿态（默认站立）")
    print("2. 趴下姿态（腿收起）")
    print("3. 零位姿态（所有关节0度 - 不推荐，可能不稳定）")
    print("4. 跳过初始化（危险！仅当机器狗已在零位时使用）\n")
    
    choice = input("请选择 (1-4，默认1): ").strip() or "1"
    
    if choice == "1":
        # 站立姿态
        current_angles = np.array([
            [0.0, 0.0, 0.0, 0.0],           # Hip 中立
            [0.8, 0.8, 0.8, 0.8],           # 大腿稍微向后
            [-1.6, -1.6, -1.6, -1.6]        # 小腿弯曲，站立
        ])
        print("\n将缓慢移动到站立姿态（10秒）...")
    elif choice == "2":
        # 趴下姿态
        current_angles = np.array([
            [0.0, 0.0, 0.0, 0.0],           # Hip 中立
            [0.5, 0.5, 0.5, 0.5],           # 大腿稍微抬起
            [-0.8, -0.8, -0.8, -0.8]        # 小腿收起，趴下
        ])
        print("\n将缓慢移动到趴下姿态（10秒）...")
    elif choice == "3":
        # 零位
        current_angles = np.array([
            [0.0, 0.0, 0.0, 0.0],
            [0.0, 0.0, 0.0, 0.0],
            [0.0, 0.0, 0.0, 0.0]
        ])
        print("\n将缓慢移动到零位（10秒）...")
    elif choice == "4":
        # 跳过初始化
        current_angles = np.array([
            [0.0, 0.0, 0.0, 0.0],
            [0.0, 0.0, 0.0, 0.0],
            [0.0, 0.0, 0.0, 0.0]
        ])
        print("\n⚠️  跳过初始化，假设机器狗已在零位")
        print("如果不在零位，可能会突然跳变！\n")
        # 直接跳到后面，不移动
        joint_checker.update(current_angles)
        display_all_angles(current_angles, "当前理论角度（零位）")
    else:
        print("无效选择，使用站立姿态")
        current_angles = np.array([
            [0.0, 0.0, 0.0, 0.0],
            [0.8, 0.8, 0.8, 0.8],
            [-1.6, -1.6, -1.6, -1.6]
        ])
        print("\n将缓慢移动到站立姿态（10秒）...")
    
    if choice != "4":
        input("按 Enter 开始移动到起始姿态...")
        
        # 非常缓慢地移动到起始姿态
        steps = 100
        print("移动中", end="", flush=True)
        for step in range(steps + 1):
            ratio = step / steps
            interpolated = current_angles * ratio
            hardware_interface.set_actuator_postions(interpolated)
            if step % 10 == 0:
                print(".", end="", flush=True)
            time.sleep(0.1)
        
        print(" 完成！")
        joint_checker.update(current_angles)
        time.sleep(1)
        display_all_angles(current_angles, "当前姿态角度")
    
    print("\n现在可以安全地测试单个关节了")
    print("其他关节将保持在当前姿态\n")
    
    # 选择要测试的关节
    print("电机编号说明:")
    print("  0 = Motor 1 (Hip/髋关节) - 左右摆动")
    print("  1 = Motor 2 (Upper leg/大腿) - 向后抬起")
    print("  2 = Motor 3 (Lower leg/小腿) - 弯曲")
    print("\n腿部编号说明:")
    print("  0 = FR (前右腿)")
    print("  1 = FL (前左腿)")
    print("  2 = BR (后右腿)")
    print("  3 = BL (后左腿)\n")
    
    try:
        motor_idx = int(input("选择要测试的电机 (0-2): "))
        leg_idx = int(input("选择要测试的腿 (0-3): "))
        
        if not (0 <= motor_idx <= 2 and 0 <= leg_idx <= 3):
            print("❌ 无效的输入")
            return
        
        motor_names = ["Motor 1 (Hip)", "Motor 2 (Upper leg)", "Motor 3 (Lower leg)"]
        leg_names = ["前右腿", "前左腿", "后右腿", "后左腿"]
        
        print(f"\n将测试: {leg_names[leg_idx]} 的 {motor_names[motor_idx]}")
        print("\n测试方式:")
        print("  A. 测试正向移动（逐步增加角度直到被限制）")
        print("  B. 测试负向移动（逐步减少角度直到被限制）")
        print("  C. 手动输入角度测试")
        
        choice = input("\n请选择 (A/B/C): ").upper()
        
        if choice == 'A':
            # 正向测试
            print(f"\n开始正向测试 {motor_names[motor_idx]}...")
            print("将从当前角度开始，每次增加 5°，直到被限制")
            input("按 Enter 开始...")
            
            current_deg = rad2deg(current_angles[motor_idx][leg_idx])
            print(f"\n起始角度: {current_deg:.1f}°")
            print("\n【实时角度监控 - 包含限制检测】")
            print("-" * 60)
            print(f"Motor 1 限制: {rad2deg(joint_checker.joint_angles_minLimit[0][leg_idx]):.1f}° ~ {rad2deg(joint_checker.joint_angles_maxLimit[0][leg_idx]):.1f}°")
            print(f"Motor 2 限制: {rad2deg(joint_checker.joint_angles_maxLimit[1][leg_idx]):.1f}° ~ {rad2deg(joint_checker.joint_angles_minLimit[1][leg_idx]):.1f}°")
            print(f"Motor 3 限制: {rad2deg(joint_checker.joint_angles_maxLimit[2][leg_idx]):.1f}° ~ {rad2deg(joint_checker.joint_angles_minLimit[2][leg_idx]):.1f}°")
            print("-" * 60)
            print(f"提示: 正向测试将增加角度，预计在 {rad2deg(joint_checker.joint_angles_minLimit[motor_idx][leg_idx]):.1f}° 处被限制")
            print("-" * 60)
            
            for i in range(50):  # 增加到 50 次 (250度范围)，确保能触发限制
                target_deg = current_deg + 5
                target_angles = np.copy(current_angles)
                target_angles[motor_idx][leg_idx] = deg2rad(target_deg)
                
                # 记录限制前的次数
                prev_cnt = joint_checker.cnt
                
                # 平滑移动
                steps = 10
                for step in range(steps + 1):
                    ratio = step / steps
                    interpolated = current_angles + (target_angles - current_angles) * ratio
                    joint_checker.check_limit(interpolated)
                    hardware_interface.set_actuator_postions(interpolated)
                    time.sleep(0.05)
                
                current_angles = np.copy(interpolated)
                joint_checker.update(current_angles)
                
                actual_deg = rad2deg(current_angles[motor_idx][leg_idx])
                
                # 检查是否触发了限制
                was_blocked = joint_checker.cnt > prev_cnt
                
                # 实时显示所有关节角度
                print(f"\n步骤 {i+1}: 目标 {target_deg:6.1f}° -> 实际 {actual_deg:6.1f}° ", end="")
                
                if abs(actual_deg - target_deg) > 0.5:
                    if was_blocked:
                        print("【被限制！触发了 check_limit() 保护】⚠️")
                    else:
                        print("【被限制！】")
                    print(f"    限制触发次数: {joint_checker.cnt}")
                    print("\n当前所有关节状态:")
                    display_all_angles(current_angles, "最终角度状态")
                    break
                else:
                    if was_blocked:
                        print(f"✓ (警告: check_limit 被调用了 {joint_checker.cnt - prev_cnt} 次)")
                    else:
                        print("✓")
                    # 每5步显示一次完整角度
                    if (i + 1) % 5 == 0:
                        display_all_angles(current_angles, f"第 {i+1} 步后的角度状态")
                
                current_deg = actual_deg
                time.sleep(0.3)
        
        elif choice == 'B':
            # 负向测试
            print(f"\n开始负向测试 {motor_names[motor_idx]}...")
            print("将从当前角度开始，每次减少 5°，直到被限制")
            input("按 Enter 开始...")
            
            current_deg = rad2deg(current_angles[motor_idx][leg_idx])
            print(f"\n起始角度: {current_deg:.1f}°")
            print("\n【实时角度监控 - 包含限制检测】")
            print("-" * 60)
            print(f"Motor 1 限制: {rad2deg(joint_checker.joint_angles_minLimit[0][leg_idx]):.1f}° ~ {rad2deg(joint_checker.joint_angles_maxLimit[0][leg_idx]):.1f}°")
            print(f"Motor 2 限制: {rad2deg(joint_checker.joint_angles_maxLimit[1][leg_idx]):.1f}° ~ {rad2deg(joint_checker.joint_angles_minLimit[1][leg_idx]):.1f}°")
            print(f"Motor 3 限制: {rad2deg(joint_checker.joint_angles_maxLimit[2][leg_idx]):.1f}° ~ {rad2deg(joint_checker.joint_angles_minLimit[2][leg_idx]):.1f}°")
            print("-" * 60)
            print(f"提示: 负向测试将减少角度，预计在 {rad2deg(joint_checker.joint_angles_maxLimit[motor_idx][leg_idx]):.1f}° 处被限制")
            print("-" * 60)
            
            for i in range(50):  # 增加到 50 次，确保能触发限制
                target_deg = current_deg - 5
                target_angles = np.copy(current_angles)
                target_angles[motor_idx][leg_idx] = deg2rad(target_deg)
                
                # 记录限制前的次数
                prev_cnt = joint_checker.cnt
                
                # 平滑移动
                steps = 10
                for step in range(steps + 1):
                    ratio = step / steps
                    interpolated = current_angles + (target_angles - current_angles) * ratio
                    joint_checker.check_limit(interpolated)
                    hardware_interface.set_actuator_postions(interpolated)
                    time.sleep(0.05)
                
                current_angles = np.copy(interpolated)
                joint_checker.update(current_angles)
                
                actual_deg = rad2deg(current_angles[motor_idx][leg_idx])
                
                # 检查是否触发了限制
                was_blocked = joint_checker.cnt > prev_cnt
                
                print(f"\n步骤 {i+1}: 目标 {target_deg:6.1f}° -> 实际 {actual_deg:6.1f}° ", end="")
                
                if abs(actual_deg - target_deg) > 0.5:
                    if was_blocked:
                        print("【被限制！触发了 check_limit() 保护】⚠️")
                    else:
                        print("【被限制！】")
                    print(f"    限制触发次数: {joint_checker.cnt}")
                    print("\n当前所有关节状态:")
                    display_all_angles(current_angles, "最终角度状态")
                    break
                else:
                    if was_blocked:
                        print(f"✓ (警告: check_limit 被调用了 {joint_checker.cnt - prev_cnt} 次)")
                    else:
                        print("✓")
                    if (i + 1) % 5 == 0:
                        display_all_angles(current_angles, f"第 {i+1} 步后的角度状态")
                
                current_deg = actual_deg
                time.sleep(0.3)
        
        elif choice == 'C':
            # 手动输入
            print("\n进入手动模式，可以随时查看所有角度")
            print("\n当前关节的角度限制:")
            print(f"Motor 1: {rad2deg(joint_checker.joint_angles_minLimit[0][leg_idx]):.1f}° ~ {rad2deg(joint_checker.joint_angles_maxLimit[0][leg_idx]):.1f}°")
            print(f"Motor 2: {rad2deg(joint_checker.joint_angles_maxLimit[1][leg_idx]):.1f}° ~ {rad2deg(joint_checker.joint_angles_minLimit[1][leg_idx]):.1f}°")
            print(f"Motor 3: {rad2deg(joint_checker.joint_angles_maxLimit[2][leg_idx]):.1f}° ~ {rad2deg(joint_checker.joint_angles_minLimit[2][leg_idx]):.1f}°")
            
            while True:
                # 显示当前状态
                print(f"\n当前测试关节角度: {rad2deg(current_angles[motor_idx][leg_idx]):.2f}°")
                angle_input = input("输入目标角度 或 's'显示所有角度 或 'q'退出: ")
                
                if angle_input.lower() == 'q':
                    break
                
                if angle_input.lower() == 's':
                    display_all_angles(current_angles, "当前所有关节角度")
                    print(f"\n当前限制触发总次数: {joint_checker.cnt}")
                    continue
                
                try:
                    target_deg = float(angle_input)
                    target_angles = np.copy(current_angles)
                    target_angles[motor_idx][leg_idx] = deg2rad(target_deg)
                    
                    # 记录限制前的次数
                    prev_cnt = joint_checker.cnt
                    
                    print(f"正在缓慢移动到 {target_deg:.1f}°...")
                    
                    # 平滑移动
                    steps = 20
                    for step in range(steps + 1):
                        ratio = step / steps
                        interpolated = current_angles + (target_angles - current_angles) * ratio
                        joint_checker.check_limit(interpolated)
                        hardware_interface.set_actuator_postions(interpolated)
                        time.sleep(0.05)
                    
                    current_angles = np.copy(interpolated)
                    joint_checker.update(current_angles)
                    
                    actual_deg = rad2deg(current_angles[motor_idx][leg_idx])
                    
                    # 检查是否触发了限制
                    was_blocked = joint_checker.cnt > prev_cnt
                    
                    print(f"\n结果: 目标 {target_deg:.1f}° -> 实际 {actual_deg:.1f}°")
                    
                    if abs(actual_deg - target_deg) > 0.5:
                        if was_blocked:
                            print(f"⚠️  角度被 check_limit() 限制了！触发次数: {joint_checker.cnt - prev_cnt}")
                            print(f"    总限制次数: {joint_checker.cnt}")
                        else:
                            print("⚠️  角度被限制了！")
                    else:
                        if was_blocked:
                            print(f"✓ 成功移动 (但触发了 {joint_checker.cnt - prev_cnt} 次限制检查)")
                        else:
                            print("✓ 成功移动")
                    
                    # 显示移动后的所有角度
                    display_all_angles(current_angles, "移动后的角度状态")
                    
                except ValueError:
                    print("❌ 无效的角度输入")
        
        else:
            print("❌ 无效的选择")
            return
        
    except KeyboardInterrupt:
        print("\n\n测试被中断")
    except ValueError:
        print("\n❌ 输入格式错误")
        return
    
    print(f"\n测试完成！")
    print(f"总限制次数: {joint_checker.cnt}")
    print("="*60)

if __name__ == "__main__":
    # 显示全局角度限制配置状态
    print("\n" + "="*60)
    print("  单关节安全测试 - 不会让机器狗突然站立")
    print("="*60)
    print(f"\n全局配置: ENABLE_JOINT_LIMITS = {ENABLE_JOINT_LIMITS}")
    if not ENABLE_JOINT_LIMITS:
        print("⚠️⚠️⚠️  警告: 角度限制已在全局配置中禁用！⚠️⚠️⚠️")
        print("要启用限制，请修改 /home/ubuntu/mini_pupper_bsp/Python_Module/MangDang/mini_pupper/Config.py")
        print("将 ENABLE_JOINT_LIMITS 设置为 True\n")
    
    safe_test_single_motor()
