import numpy as np
import time
from src.IMU import IMU
from src.Controller import Controller
from src.JoystickInterface import JoystickInterface
from src.State import BehaviorState, State
from MangDang.mini_pupper.HardwareInterface import HardwareInterface
from MangDang.mini_pupper.Config import Configuration
from pupper.Kinematics import four_legs_inverse_kinematics
from MangDang.mini_pupper.display import Display
from src.MovementScheme import MovementScheme
from src.createDanceActionListSample import MovementLib
from src.Command import Command

def main(use_imu=False):
    """Main program
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

            # Update the pwm widths going to the servos
            hardware_interface.set_actuator_postions(state.joint_angles)


main()
