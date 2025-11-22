#!/usr/bin/env python3
"""
MiniPupper Robot Control with Bluetooth Interface
Integrates BLE server for both web joystick and MCP block programming
"""

import numpy as np
import time
import threading
from src.IMU import IMU
from src.Controller import Controller
from src.BluetoothInterface import BluetoothInterface
from src.State import BehaviorState, State
from MangDang.mini_pupper.HardwareInterface import HardwareInterface
from MangDang.mini_pupper.Config import Configuration
from pupper.Kinematics import four_legs_inverse_kinematics
from MangDang.mini_pupper.display import Display
from src.Command import Command


def start_ble_server(bluetooth_interface):
    """
    Start the BLE server in a separate thread
    
    Args:
        bluetooth_interface: BluetoothInterface instance to integrate
    """
    print("[BLE] Starting BLE server thread...")
    
    # Import here to avoid issues if running without BLE
    try:
        import minipupper_ble_server_bluez
        minipupper_ble_server_bluez.main(bluetooth_interface)
    except Exception as e:
        print(f"[BLE] Error starting BLE server: {e}")
        import traceback
        traceback.print_exc()


def main(use_imu=False, use_ble=True):
    """
    Main program with Bluetooth interface
    
    Args:
        use_imu: Whether to use IMU for orientation sensing
        use_ble: Whether to enable BLE interface (if False, runs in demo mode)
    """
    
    # Create config
    config = Configuration()
    hardware_interface = HardwareInterface()
    disp = Display()
    disp.show_ip()
    
    # Create imu handle
    if use_imu:
        imu = IMU(port="/dev/ttyACM0")
        imu.flush_buffer()
    
    # Create controller
    controller = Controller(
        config,
        four_legs_inverse_kinematics,
    )
    state = State()
    
    # Create Bluetooth interface
    print("Creating Bluetooth interface...")
    bluetooth_interface = BluetoothInterface(config)
    print("Done.")
    
    # Start BLE server in separate thread
    if use_ble:
        ble_thread = threading.Thread(target=start_ble_server, args=(bluetooth_interface,), daemon=True)
        ble_thread.start()
        print("[BLE] Server thread started")
        time.sleep(2)  # Give BLE server time to initialize
    
    last_loop = time.time()
    last_debug_print = time.time()
    
    print("\n" + "="*60)
    print("MiniPupper Bluetooth Control Ready")
    print("="*60)
    print("Control methods:")
    print("  1. Web App: Connect via browser for virtual joystick")
    print("  2. Block Programming: Use MCP tools for programmatic control")
    print("\nRobot will activate automatically when commands are received")
    print("="*60 + "\n")
    
    print("Summary of gait parameters:")
    print("overlap time: ", config.overlap_time)
    print("swing time: ", config.swing_time)
    print("z clearance: ", config.z_clearance)
    print("x shift: ", config.x_shift)
    
    # Limit the angle of each servo motor
    joint_angles_maxLimit = [[1.2,  0.6, 1,  0.5], [1.3, 1.3, 1.6, 1.6], [0.7,  0.7,   0,    0]]
    joint_angles_minLimit = [[-0.5, -1, -0.6, -1], [0,  0,  -0.6, -0.6], [-1.5, -1.5, -1.2, -1.2]]
    
    robot_active = False
    
    # Main control loop
    while True:
        now = time.time()
        if now - last_loop < config.dt:
            continue
        last_loop = time.time()
        
        # Debug heartbeat
        if now - last_debug_print > 2.0:
            is_conn = bluetooth_interface.is_connected()
            if is_conn or robot_active:
                print(f"[Debug] Connected: {is_conn}, Active: {robot_active}", flush=True)
            last_debug_print = now
        
        # Get command from Bluetooth interface
        command = bluetooth_interface.get_command(state, do_print=False)
        
        # Check if BLE is connected
        is_connected = bluetooth_interface.is_connected()
        
        # Auto-activate when commands are received
        if is_connected and not robot_active:
            print("\n[BLE] Connection detected - Activating robot", flush=True)
            robot_active = True
            disp.show_state(BehaviorState.REST)
        
        # Deactivate if connection is lost
        if not is_connected and robot_active:
            print("\n[BLE] Connection lost - Deactivating robot", flush=True)
            robot_active = False
            command = Command()  # Reset to default
            disp.show_state(BehaviorState.DEACTIVATED)
        
        # Handle activation toggle from command
        if command.activate_event:
            robot_active = not robot_active
            if robot_active:
                print("[Control] Robot activated", flush=True)
                disp.show_state(BehaviorState.REST)
            else:
                print("[Control] Robot deactivated", flush=True)
                disp.show_state(BehaviorState.DEACTIVATED)
                command = Command()
        
        if not robot_active:
            time.sleep(0.05)
            continue
        
        # Read imu data
        quat_orientation = (
            imu.read_orientation() if use_imu else np.array([1, 0, 0, 0])
        )
        state.quat_orientation = quat_orientation
        
        # Step the controller forward (handles all state transitions)
        controller.run(state, command, disp)
        
        # Update state
        state.horizontal_velocity = command.horizontal_velocity.copy()
        state.yaw_rate = command.yaw_rate
        
        # Apply joint angles with limits
        for leg_index in range(4):
            for axis_index in range(3):
                joint_angle = state.joint_angles[axis_index, leg_index]
                joint_angle = max(joint_angles_minLimit[axis_index][leg_index], 
                                 min(joint_angles_maxLimit[axis_index][leg_index], joint_angle))
                state.joint_angles[axis_index, leg_index] = joint_angle
        
        # Send commands to hardware
        hardware_interface.set_actuator_postions(state.joint_angles)


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Run MiniPupper with Bluetooth control')
    parser.add_argument('--use-imu', action='store_true', help='Use IMU for orientation sensing')
    parser.add_argument('--no-ble', action='store_true', help='Disable BLE server (demo mode)')
    
    args = parser.parse_args()
    
    try:
        main(use_imu=args.use_imu, use_ble=not args.no_ble)
    except KeyboardInterrupt:
        print("\nShutting down...")
