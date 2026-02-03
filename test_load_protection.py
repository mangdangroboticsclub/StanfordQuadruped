#!/usr/bin/env python3
"""
负载保护功能测试程序
模拟高负载情况，测试保护机制是否正常工作
"""

import numpy as np
import time
import math
from MangDang.mini_pupper.HardwareInterface import HardwareInterface
from MangDang.mini_pupper.Config import Configuration
from MangDang.mini_pupper.ESP32Interface import ESP32Interface
from pupper.Kinematics import four_legs_inverse_kinematics

def rad2deg(x):
    return x / math.pi * 180

def deg2rad(x):
    return x / 180 * math.pi

class SimpleLoadMonitor:
    """简化的负载监控器用于测试"""
    def __init__(self, esp32, threshold=900, duration=2.0):
        self.esp32 = esp32
        self.threshold = threshold
        self.duration = duration
        self.high_load_start_times = [None] * 12
        
    def check_loads(self):
        loads = self.esp32.servos_get_load()
        if loads is None:
            return False, None, None
        
        current_time = time.time()
        
        for i in range(12):
            load = loads[i]
            abs_load = abs(load)
            
            if abs_load >= self.threshold:
                if self.high_load_start_times[i] is None:
                    self.high_load_start_times[i] = current_time
                    print(f"⚠️  电机 #{i} 负载: {load} (开始监控)")
                else:
                    elapsed = current_time - self.high_load_start_times[i]
                    if elapsed >= self.duration:
                        return True, i, load
            else:
                self.high_load_start_times[i] = None
        
        return False, None, None

def return_to_calibration(hardware_interface, config, current_angles):
    """返回到校准位置"""
    print("\n" + "="*80)
    print("🛡️  执行保护: 返回校准位置")
    print("="*80)
    
    # 计算校准姿态
    calibration_foot_locations = (
        config.default_stance
        + np.array([0, 0, config.default_z_ref])[:, np.newaxis]
    )
    
    # 计算目标关节角度
    target_angles = four_legs_inverse_kinematics(calibration_foot_locations, config)
    
    print(f"\n当前姿态:")
    print(f"  Motor 1 (Hip):   {rad2deg(current_angles[0][0]):6.1f}° {rad2deg(current_angles[0][1]):6.1f}° {rad2deg(current_angles[0][2]):6.1f}° {rad2deg(current_angles[0][3]):6.1f}°")
    print(f"  Motor 2 (Upper): {rad2deg(current_angles[1][0]):6.1f}° {rad2deg(current_angles[1][1]):6.1f}° {rad2deg(current_angles[1][2]):6.1f}° {rad2deg(current_angles[1][3]):6.1f}°")
    print(f"  Motor 3 (Lower): {rad2deg(current_angles[2][0]):6.1f}° {rad2deg(current_angles[2][1]):6.1f}° {rad2deg(current_angles[2][2]):6.1f}° {rad2deg(current_angles[2][3]):6.1f}°")
    
    print(f"\n目标姿态（校准位置）:")
    print(f"  Motor 1 (Hip):   {rad2deg(target_angles[0][0]):6.1f}° {rad2deg(target_angles[0][1]):6.1f}° {rad2deg(target_angles[0][2]):6.1f}° {rad2deg(target_angles[0][3]):6.1f}°")
    print(f"  Motor 2 (Upper): {rad2deg(target_angles[1][0]):6.1f}° {rad2deg(target_angles[1][1]):6.1f}° {rad2deg(target_angles[1][2]):6.1f}° {rad2deg(target_angles[1][3]):6.1f}°")
    print(f"  Motor 3 (Lower): {rad2deg(target_angles[2][0]):6.1f}° {rad2deg(target_angles[2][1]):6.1f}° {rad2deg(target_angles[2][2]):6.1f}° {rad2deg(target_angles[2][3]):6.1f}°")
    
    print(f"\n缓慢移动中（3秒）...")
    
    # 缓慢移动
    steps = 200
    for step in range(steps + 1):
        ratio = step / steps
        # ease-out曲线
        smooth_ratio = 1 - (1 - ratio) ** 2
        interpolated = current_angles + (target_angles - current_angles) * smooth_ratio
        
        hardware_interface.set_actuator_postions(interpolated)
        
        if step % 40 == 0:
            print(f"  进度: {ratio*100:.0f}%")
        
        time.sleep(0.015)
    
    print("\n✅ 已返回校准位置")
    print("="*80 + "\n")
    
    return target_angles

def test_protection():
    """测试保护功能"""
    print("="*80)
    print("  负载保护功能测试")
    print("="*80)
    print("\n本测试将:")
    print("  1. 移动机器狗到站立姿态")
    print("  2. 持续监控电机负载")
    print("  3. 当检测到负载≥900持续2秒时，自动返回校准位置")
    print("\n⚠️  请确保机器狗周围有足够空间，且没有障碍物阻挡\n")
    
    input("按 Enter 开始测试...")
    
    # 初始化
    config = Configuration()
    hardware_interface = HardwareInterface()
    esp32 = ESP32Interface()
    load_monitor = SimpleLoadMonitor(esp32, threshold=900, duration=2.0)
    
    print("\n✓ 硬件初始化完成")
    
    # 先移动到站立姿态
    print("\n移动到站立姿态...")
    standing_angles = np.array([
        [0.0, 0.0, 0.0, 0.0],
        [0.8, 0.8, 0.8, 0.8],
        [-1.6, -1.6, -1.6, -1.6]
    ])
    
    steps = 100
    for step in range(steps + 1):
        ratio = step / steps
        interpolated = standing_angles * ratio
        hardware_interface.set_actuator_postions(interpolated)
        time.sleep(0.05)
    
    current_angles = np.copy(standing_angles)
    print("✓ 已到达站立姿态\n")
    
    print("="*80)
    print("开始监控负载...")
    print("提示: 你可以尝试用手阻挡机器狗的腿部运动来触发高负载")
    print("      或者等待自然触发（如果有的话）")
    print("      按 Ctrl+C 可以随时退出")
    print("="*80 + "\n")
    
    try:
        # 简单的左右摇摆运动来产生负载
        angle = 0
        while True:
            # 生成轻微的摇摆运动
            angle += 0.05
            sway = math.sin(angle) * 0.2
            
            test_angles = np.copy(standing_angles)
            test_angles[0] = [sway, -sway, sway, -sway]  # Hip左右摇摆
            
            hardware_interface.set_actuator_postions(test_angles)
            current_angles = np.copy(test_angles)
            
            # 检查负载
            triggered, motor_id, load = load_monitor.check_loads()
            
            if triggered:
                print(f"\n🔴 保护触发！电机 #{motor_id} 负载: {load}")
                current_angles = return_to_calibration(hardware_interface, config, current_angles)
                
                # 重置监控器
                load_monitor.high_load_start_times = [None] * 12
                
                print("保护已执行，继续监控...")
                print("如需退出，请按 Ctrl+C\n")
                
                # 短暂暂停
                time.sleep(2)
                
                # 重新站立
                print("返回站立姿态...")
                steps = 100
                for step in range(steps + 1):
                    ratio = step / steps
                    interpolated = current_angles + (standing_angles - current_angles) * ratio
                    hardware_interface.set_actuator_postions(interpolated)
                    time.sleep(0.05)
                current_angles = np.copy(standing_angles)
                print("✓ 已返回站立姿态\n")
                angle = 0
            
            time.sleep(0.05)
    
    except KeyboardInterrupt:
        print("\n\n测试被中断")
        
        # 安全返回校准位置
        print("\n安全关闭: 返回校准位置...")
        return_to_calibration(hardware_interface, config, current_angles)
        
        print("\n✅ 测试完成")
        print("="*80)

if __name__ == "__main__":
    test_protection()
