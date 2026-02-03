import numpy as np
import time
import math
import sys
import os
from src.IMU import IMU
from src.Controller import Controller
from src.JoystickInterface import JoystickInterface
from src.State import BehaviorState, State
from MangDang.mini_pupper.HardwareInterface import HardwareInterface, Joint_checker
from MangDang.mini_pupper.Config import Configuration, ENABLE_JOINT_LIMITS
from pupper.Kinematics import four_legs_inverse_kinematics
from MangDang.mini_pupper.display import Display
from src.MovementScheme import MovementScheme
from src.createDanceActionListSample import MovementLib
from src.Command import Command

def rad2deg(x):
    return x / math.pi * 180

def display_angles_compact(joint_angles, joint_checker, loop_count):
    """Display joint angles and limit information in compact format"""
    # Display every 10 loops to avoid screen flooding
    if loop_count % 10 != 0:
        return
    
    print("\n" + "="*80)
    print(f"Loop #{loop_count} - Joint Angle Monitor (Limit triggers: {joint_checker.cnt})")
    print("="*80)
    
    motor_names = ["M1(Hip)  ", "M2(Upper)", "M3(Lower)"]
    leg_names = ["FR(FrontR)", "FL(FrontL)", "BR(BackR)", "BL(BackL)"]
    
    print(f"{'Joint':12} {leg_names[0]:>12} {leg_names[1]:>12} {leg_names[2]:>12} {leg_names[3]:>12}")
    print("-"*80)
    
    for i in range(3):
        angles = [f"{rad2deg(joint_angles[i][j]):7.2f}°" for j in range(4)]
        print(f"{motor_names[i]:12} {angles[0]:>12} {angles[1]:>12} {angles[2]:>12} {angles[3]:>12}")
    
    # Check if any joint is approaching limits
    warnings = []
    for i in range(3):
        for j in range(4):
            current = rad2deg(joint_angles[i][j])
            min_limit = rad2deg(joint_checker.joint_angles_minLimit[i][j])
            max_limit = rad2deg(joint_checker.joint_angles_maxLimit[i][j])
            
            # Check if within 10 degrees of limit
            if abs(current - min_limit) < 10 or abs(current - max_limit) < 10:
                warnings.append(f"⚠️  {motor_names[i]} {leg_names[j]}: {current:.1f}° (approaching limit)")
    
    if warnings:
        print("\nWarnings:")
        for w in warnings:
            print(f"  {w}")
    
    print("="*80)

def main(use_imu=False, show_angles=True):
    """Main program
    """

    # Create config
    config = Configuration()
    hardware_interface = HardwareInterface()
    joint_checker = Joint_checker()
    disp = Display()
    disp.show_ip()
    
    # Display angle limit status (read from global config)
    if joint_checker.enabled:
        print("✅ Angle Limits: ENABLED (global config)")
    else:
        print("⚠️  Angle Limits: DISABLED (global config) - Use with caution!")

    # Create imu handle
    if use_imu:
        imu = IMU(port="/dev/ttyACM0")
        imu.flush_buffer()

    # Create controller and user input handles
    controller = Controller(
        config,
        four_legs_inverse_kinematics,
    )
    state = State()
    print("Creating joystick listener...")
    joystick_interface = JoystickInterface(config)
    print("Done.")

    #Create movement group scheme instance and set a default false state
    movementCtl = MovementScheme(MovementLib)
    dance_active_state = False

    last_loop = time.time()
    loop_count = 0  # Loop counter for controlling display frequency

    print("Summary of gait parameters:")
    print("overlap time: ", config.overlap_time)
    print("swing time: ", config.swing_time)
    print("z clearance: ", config.z_clearance)
    print("x shift: ", config.x_shift)

    # Wait until the activate button has been pressed
    while True:
        print("Waiting for L1 to activate robot.")
        while True:
            command = joystick_interface.get_command(state, disp)
            joystick_interface.set_color(config.ps4_deactivated_color)
            if command.activate_event == 1:
                break
            time.sleep(0.1)
        print("Robot activated.")
        joystick_interface.set_color(config.ps4_color)

        while True:
            now = time.time()
            if now - last_loop < config.dt:
                continue
            last_loop = time.time()

            # Parse the udp joystick commands and then update the robot controller's parameters
            command = joystick_interface.get_command(state, disp)
            if command.activate_event == 1:
                print("Deactivating Robot")
                disp.show_state(BehaviorState.DEACTIVATED)
                break

            # Read imu data. Orientation will be None if no data was available
            quat_orientation = (
                imu.read_orientation() if use_imu else np.array([1, 0, 0, 0])
            )
            state.quat_orientation = quat_orientation

            # If "circle" button is clicked, switch dance_active_state between False/True.
            if command.dance_activate_event == True:
                if dance_active_state == False:
                    dance_active_state = True
                else:
                    dance_active_state = False

            # Step the controller forward by dt
            if dance_active_state == True:
            	# Caculate legsLocation, attitudes and speed using custom movement script
                movementCtl.runMovementScheme()
                command.horizontal_velocity = movementCtl.getMovemenSpeed()
                command.legslocation        = movementCtl.getMovemenLegsLocation()
                command.roll                = movementCtl.attitude_now[0]
                command.pitch               = movementCtl.attitude_now[1]
                command.yaw                 = movementCtl.attitude_now[2]
                command.yaw_rate            = movementCtl.getMovemenTurn()
                controller.run(state, command, disp)
            else:
                controller.run(state, command, disp)

            # Check joint angle limits before applying
            joint_checker.check_limit(state.joint_angles)

            # Update the pwm widths going to the servos
            hardware_interface.set_actuator_postions(state.joint_angles)

            # Update joint checker state
            joint_checker.update(state.joint_angles)

            # Display angles and limits info
            if show_angles:
                loop_count += 1
                display_angles_compact(state.joint_angles, joint_checker, loop_count)


if __name__ == "__main__":
    # Control angle display via command line arguments
    show_angles = True
    
    if len(sys.argv) > 1 and "--no-display" in sys.argv:
        show_angles = False
    
    # Display global angle limit configuration status
    print(f"\nGlobal Config: ENABLE_JOINT_LIMITS = {ENABLE_JOINT_LIMITS}")
    if not ENABLE_JOINT_LIMITS:
        print("⚠️⚠️⚠️  WARNING: Angle limits are DISABLED in global config! ⚠️⚠️⚠️")
        print("To enable limits, modify /home/ubuntu/mini_pupper_bsp/Python_Module/MangDang/mini_pupper/Config.py")
        print("Set ENABLE_JOINT_LIMITS to True\n")
    
    main(show_angles=show_angles)
