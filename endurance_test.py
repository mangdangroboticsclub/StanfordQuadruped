#!/usr/bin/env python3
"""
机器人耐久性测试脚本
循环运行：动作10次（约60秒） -> 休息10秒 -> 重复
记录运行次数、时长和任何错误
"""

import subprocess
import time
import signal
import sys
from datetime import datetime, timedelta
import os


# 全局变量用于统计
test_stats = {
    'cycles_completed': 0,
    'total_runtime': 0,
    'start_time': None,
    'errors': []
}

# 测试配置
DANCE_REPETITIONS = 10  # 每轮跳舞次数（每次约6秒）
REST_DURATION = 10      # 休息时间（秒）
SCRIPT_PATH = "/home/ubuntu/StanfordQuadruped/run_danceActionList.py"


def signal_handler(sig, frame):
    """处理 Ctrl+C 中断，显示统计信息"""
    print("\n" + "="*60)
    print("🛑 测试被用户中断")
    print_statistics()
    sys.exit(0)


def print_statistics():
    """打印测试统计信息"""
    print("="*60)
    print("📊 耐久性测试统计")
    print("="*60)
    print(f"开始时间: {test_stats['start_time'].strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"完成周期数: {test_stats['cycles_completed']}")
    print(f"总运行时长: {timedelta(seconds=int(test_stats['total_runtime']))}")
    print(f"总动作次数: {test_stats['cycles_completed'] * DANCE_REPETITIONS}")
    print(f"总休息时长: {timedelta(seconds=test_stats['cycles_completed'] * REST_DURATION)}")
    
    if test_stats['errors']:
        print(f"\n⚠️  错误次数: {len(test_stats['errors'])}")
        for i, error in enumerate(test_stats['errors'][-5:], 1):  # 只显示最后5个错误
            print(f"  {i}. {error}")
    else:
        print("\n✅ 无错误记录")
    print("="*60)


def run_dance_once():
    """运行一次舞蹈动作"""
    try:
        result = subprocess.run(
            ["python3", SCRIPT_PATH],
            capture_output=True,
            timeout=15  # 超时保护，避免卡死
        )
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print("⚠", end='', flush=True)
        return False
    except Exception as e:
        print(f"✗({e})", end='', flush=True)
        return False


def run_movement_cycle():
    """运行一个动作周期（10次舞蹈动作）"""
    
    start_time = time.time()
    
    print(f"  🤖 动作中 ({DANCE_REPETITIONS}次)... ", end='', flush=True)
    
    success_count = 0
    for i in range(DANCE_REPETITIONS):
        if run_dance_once():
            print("✓", end='', flush=True)
            success_count += 1
        else:
            print("✗", end='', flush=True)
    
    actual_duration = time.time() - start_time
    print(f" [{success_count}/{DANCE_REPETITIONS}成功, {actual_duration:.1f}秒]")
    return actual_duration, success_count


def rest_period(duration):
    """休息期间"""
    print(f"  😴 休息中 ({duration}秒)... ", end='', flush=True)
    time.sleep(duration)
    print("✓")


def main():
    """主程序 - 耐久性测试循环"""
    
    # 注册信号处理器
    signal.signal(signal.SIGINT, signal_handler)
    
    print("="*60)
    print("🔋 机器人耐久性测试程序")
    print("="*60)
    print(f"配置: 跳舞 {DANCE_REPETITIONS} 次 -> 休息 {REST_DURATION} 秒 -> 循环")
    print("按 Ctrl+C 停止测试并查看统计")
    print("="*60)
    
    # 检查脚本是否存在
    if not os.path.exists(SCRIPT_PATH):
        print(f"❌ 错误: 找不到脚本 {SCRIPT_PATH}")
        sys.exit(1)
    
    # 记录开始时间
    test_stats['start_time'] = datetime.now()
    overall_start = time.time()
    
    print("\n🚀 开始测试...\n")
    
    cycle = 0
    try:
        while True:
            cycle += 1
            print(f"━━━ 周期 #{cycle} ━━━ [{datetime.now().strftime('%H:%M:%S')}]")
            
            try:
                # 运行10次舞蹈动作
                actual_duration, success_count = run_movement_cycle()
                
                # 更新统计
                test_stats['cycles_completed'] += 1
                test_stats['total_runtime'] = time.time() - overall_start
                
                if success_count < DANCE_REPETITIONS:
                    error_msg = f"周期 #{cycle}: 只成功 {success_count}/{DANCE_REPETITIONS} 次"
                    test_stats['errors'].append(error_msg)
                
                # 休息
                rest_period(REST_DURATION)
                
                # 显示进度摘要
                elapsed = timedelta(seconds=int(test_stats['total_runtime']))
                total_dances = test_stats['cycles_completed'] * DANCE_REPETITIONS
                print(f"  📈 已完成: {cycle} 周期, {total_dances} 次动作, 总时长: {elapsed}\n")
                
            except Exception as e:
                error_msg = f"周期 #{cycle} 出错: {type(e).__name__}: {str(e)}"
                print(f"\n❌ {error_msg}")
                test_stats['errors'].append(error_msg)
                
                # 出错后休息一下再继续
                print(f"  ⏸️  错误恢复中，等待 {REST_DURATION} 秒...")
                time.sleep(REST_DURATION)
                continue
    
    except KeyboardInterrupt:
        # 这个异常会被信号处理器捕获
        pass
    
    except Exception as e:
        print(f"\n💥 致命错误: {type(e).__name__}: {str(e)}")
        test_stats['errors'].append(f"致命错误: {str(e)}")
        print_statistics()
        sys.exit(1)


if __name__ == "__main__":
    main()
