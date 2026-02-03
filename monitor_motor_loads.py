#!/usr/bin/env python3
"""
电机负载监控脚本
实时显示12个电机的负载状态
"""

from MangDang.mini_pupper.ESP32Interface import ESP32Interface
import time
import os

def clear_screen():
    """清屏"""
    os.system('clear' if os.name == 'posix' else 'cls')

def get_status_icon(load):
    """根据负载返回状态图标"""
    abs_load = abs(load)
    if abs_load >= 900:
        return "🔴"
    elif abs_load >= 700:
        return "🟠"
    elif abs_load >= 500:
        return "🟡"
    elif abs_load >= 300:
        return "🟢"
    elif abs_load > 0:
        return "⚪"
    else:
        return "⚫"

def display_motors(loads, power_status, max_loads):
    """显示所有电机状态"""
    clear_screen()
    
    print("=" * 80)
    print(f"{'🔌 电机负载监控':^80}")
    print("=" * 80)
    
    # 显示总电流
    if power_status:
        current = power_status.get('current', 0)
        print(f"\n🔋 总电流: {current:.2f} A")
    else:
        print(f"\n🔋 总电流: 无法读取")
    
    print("-" * 80)
    
    # 电机映射
    motor_names = [
        "FR前右-Hip", "FR前右-Upper", "FR前右-Lower",
        "FL前左-Hip", "FL前左-Upper", "FL前左-Lower",
        "BR后右-Hip", "BR后右-Upper", "BR后右-Lower",
        "BL后左-Hip", "BL后左-Upper", "BL后左-Lower"
    ]
    
    print(f"\n{'':3} {'#':>2} {'电机位置':>14} {'负载':>6} {'最大':>6} {'状态'}")
    print("-" * 80)
    
    for i in range(12):
        load = loads[i] if loads else 0
        max_load = max_loads[i]
        icon = get_status_icon(load)
        
        # 更新最大负载
        if abs(load) > abs(max_load):
            max_loads[i] = load
        
        status = ""
        if abs(load) >= 900:
            status = "严重"
        elif abs(load) >= 700:
            status = "偏高"
        elif abs(load) >= 500:
            status = "高"
        elif abs(load) >= 300:
            status = "正常"
        elif abs(load) > 0:
            status = "空闲"
        else:
            status = "未激活"
        
        print(f"{icon:3} {i+1:2d} {motor_names[i]:>14} {load:6d} {max_loads[i]:6d} {status}")
    
    print("-" * 80)
    
    # 统计
    total_load = sum(abs(l) for l in loads) if loads else 0
    active = sum(1 for l in loads if abs(l) > 50) if loads else 0
    
    print(f"\n📊 统计: 活跃 {active}/12  |  总负载 {total_load}")
    print("=" * 80)
    print("\n💡 按 Ctrl+C 退出")

def monitor():
    """监控主函数"""
    print("=" * 80)
    print("  🔌 电机负载监控")
    print("=" * 80)
    print("\n正在连接...")
    
    try:
        esp32 = ESP32Interface()
        max_loads = [0] * 12
        
        print("✅ 连接成功！开始监控...\n")
        time.sleep(1)
        
        while True:
            # 获取电机负载
            loads = esp32.servos_get_load()
            
            # 获取电源状态
            power_status = esp32.get_power_status()
            
            # 显示
            display_motors(loads, power_status, max_loads)
            
            # 等待
            time.sleep(0.1)
    
    except KeyboardInterrupt:
        print("\n\n👋 监控已停止")
        return
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    monitor()
