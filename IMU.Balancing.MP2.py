import numpy as np
import time
from src.IMU import IMU
from src.Controller import Controller
from src.State import State
from MangDang.mini_pupper.HardwareInterface import HardwareInterface
from MangDang.mini_pupper.Config import Configuration
from pupper.Kinematics import four_legs_inverse_kinematics
from MangDang.mini_pupper.display import Display
from src.MovementScheme import MovementScheme
from src.Command import Command
from src.MovementGroup import MovementGroups
from MangDang.mini_pupper.ESP32Interface import ESP32Interface
import math
import csv
from threading import Thread
import queue

# Initialize movement groups
Move = MovementGroups()

def add_movement(desired_roll_angle, desired_pitch_angle):
    """Add a balance correction movement to the queue.
    
    Args:
        desired_roll_angle: Target roll angle in degrees
        desired_pitch_angle: Target pitch angle in degrees
    """
    Move.balance(desired_roll_angle, desired_pitch_angle, 0.015, 0)  # 0.015, 0.015

class IIRLowPassFilter:
    """IIR Low Pass Filter implementation with configurable order."""
    
    def __init__(self, cutoff_freq, sample_rate, order):
        """
        Initialize IIR low pass filter.
        
        Args:
            cutoff_freq: Cutoff frequency in Hz
            sample_rate: Sampling frequency in Hz
            order: Filter order (1 or 2)
        """
        self.cutoff = cutoff_freq
        self.fs = sample_rate
        self.order = order
        
        # Calculate filter coefficients
        nyquist = 0.5 * sample_rate
        normal_cutoff = cutoff_freq / nyquist
        
        if order == 1:
            # First order Butterworth coefficients
            self.b = [normal_cutoff, normal_cutoff]
            self.a = [1, normal_cutoff - 1]
        else:
            # Second order Butterworth coefficients
            sqrt2 = np.sqrt(2)
            self.b = [normal_cutoff**2, 2*normal_cutoff**2, normal_cutoff**2]
            self.a = [1, 2*(normal_cutoff**2 - 1), 1 - sqrt2*normal_cutoff + normal_cutoff**2]
            
        self.x_hist = [0] * (order + 1)
        self.y_hist = [0] * (order + 1)
    
    def update(self, new_value):
        """
        Update the filter with a new measurement.
        
        Returns:
            The filtered value
        """
        # Shift history
        self.x_hist.pop()
        self.x_hist.insert(0, new_value)
        self.y_hist.pop()
        
        # Compute new output
        y = 0
        for i in range(len(self.b)):
            y += self.b[i] * self.x_hist[i]
        for i in range(1, len(self.a)):
            y -= self.a[i] * self.y_hist[i-1]
        
        y /= self.a[0]
        self.y_hist.insert(0, y)
        
        return y

class RealTimeEKF:
    """Thread-safe Extended Kalman Filter implementation for real-time sensor fusion."""
    
    def __init__(self, initial_state, initial_covariance, process_noise, measurement_noise):
        """
        Initialize the Real-Time EKF.
        
        Args:
            initial_state: Initial state vector [ax, ay, vx, vy]
            initial_covariance: Initial covariance matrix (4x4)
            process_noise: Process noise covariance matrix (4x4)
            measurement_noise: Measurement noise covariance matrix (2x2)
        """
        self.state = initial_state
        self.covariance = initial_covariance
        self.Q = process_noise
        self.R = measurement_noise
        self.last_time = time.time()
        
        # Thread-safe queue for incoming measurements
        self.measurement_queue = queue.Queue()
        
        # Flag for controlling the filter thread
        self.running = False
        self.filter_thread = None
    
    def predict(self, current_time=None):
        """Perform prediction step of the EKF."""
        if current_time is None:
            current_time = time.time()
            
        dt = current_time - self.last_time
        self.last_time = current_time
        
        # State transition matrix
        F = np.eye(4)
        F[0, 2] = dt
        F[1, 3] = dt
        
        # Process noise matrix (scaled by dt)
        Q = self.Q * dt
        
        # Predict state and covariance
        self.state = F @ self.state
        self.covariance = F @ self.covariance @ F.T + Q
    
    def update(self, measurement):
        """Perform update step of the EKF."""
        H = np.array([[1, 0, 0, 0],
                      [0, 1, 0, 0]])
        
        # Calculate Kalman gain
        S = H @ self.covariance @ H.T + self.R
        K = self.covariance @ H.T @ np.linalg.inv(S)
        
        # Update state and covariance
        measurement_residual = measurement - H @ self.state
        self.state = self.state + K @ measurement_residual
        self.covariance = (np.eye(4) - K @ H) @ self.covariance
    
    def filter_loop(self):
        """Main filtering loop to run in a separate thread."""
        while self.running:
            try:
                # Get the latest measurement with timeout
                measurement = self.measurement_queue.get(timeout=0.1)
                self.filter_measurement(measurement)
            except queue.Empty:
                continue
                
    def filter_measurement(self, measurement):
        """Process a single measurement through the EKF."""
        current_time = time.time()
        self.predict(current_time)
        self.update(measurement)
        return self.state[:2]  # Return filtered ax, ay
        
    def start(self):
        """Start the real-time filtering thread."""
        if not self.running:
            self.running = True
            self.filter_thread = Thread(target=self.filter_loop)
            self.filter_thread.start()
            
    def stop(self):
        """Stop the filtering thread."""
        self.running = False
        if self.filter_thread is not None:
            self.filter_thread.join()
            
    def add_measurement(self, ax, ay):
        """Add a new measurement to the queue (thread-safe)."""
        self.measurement_queue.put(np.array([ax, ay]))
        
    def get_filtered_output(self):
        """Get the current filtered state (thread-safe)."""
        return self.state[:2].copy()  # Return a copy to avoid thread issues

class PIDController:
    """Standard PID controller implementation."""
    
    def __init__(self, Kp, Ki, Kd, setpoint):
        """
        Initialize PID controller.
        
        Args:
            Kp: Proportional gain
            Ki: Integral gain
            Kd: Derivative gain
            setpoint: Target value
        """
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd
        self.setpoint = setpoint
        self.previous_error = 0
        self.integral = 0

    def compute(self, process_variable, dt):
        """
        Compute PID output.
        
        Args:
            process_variable: Current measured value
            dt: Time step since last computation
            
        Returns:
            PID control output
        """
        # Calculate error
        error = self.setpoint - process_variable
        
        # Proportional term
        P_out = self.Kp * error
        
        # Integral term
        self.integral += error * dt
        I_out = self.Ki * self.integral
        
        # Derivative term
        derivative = (error - self.previous_error) / dt
        D_out = self.Kd * derivative
        
        # Compute total output
        output = P_out + I_out + D_out
        
        # Update previous error
        self.previous_error = error
        
        return output

def angle_converter_roll(ax, ay, az):
    """Convert accelerometer readings to roll angle in degrees."""
    return math.degrees(math.atan(ax / math.sqrt(ay * ay + az * az)))

def angle_converter_pitch(ax, ay, az):
    """Convert accelerometer readings to pitch angle in degrees."""
    return math.degrees(math.atan(ay / math.sqrt(ax * ax + az * az)))

def main(use_imu=False):
    """Main control loop for the quadruped robot.
    
    Args:
        use_imu: Boolean flag to enable/disable IMU usage
    """
    # Parameter configuration
    angle_pitch = []
    angle_roll = []
    
    # Create config
    config = Configuration()
    hardware_interface = HardwareInterface()
    disp = Display()
    disp.show_ip()

    # Create imu handle
    if use_imu:
        imu = IMU(port="/dev/ttyACM0")
        imu.flush_buffer()
    esp32 = ESP32Interface()

    # Create controller and user input handles
    controller = Controller(
        config,
        four_legs_inverse_kinematics,
    )
    state = State()

    # Create movement group scheme instance and set a default True state
    Move.balance(0, 0, 0.02, 0)
    MovementLib = Move.MovementLib
    movementCtl = MovementScheme(MovementLib)
    lib_length = len(MovementLib)
    
    last_loop = time.time()

    command = Command()
    command.pseudo_dance_event = True

    # Measure original roll and pitch angle
    original = esp32.imu_get_data()
    original_roll =  angle_converter_roll(original['ax'], original['ay'], original['az'])
    original_pitch = angle_converter_pitch(original['ax'], original['ay'], original['az'])

    # Create PID controller 
    # Parameters can be tuned to be suitable with the need
    kp = 0.8
    ki = 0.01
    kd = 0.01
    pid_roll = PIDController(kp, ki, kd, original_roll)
    pid_pitch = PIDController(kp, ki, kd, original_pitch)

    # Low-pass filter initializer
    # Parameters can be tuned to be suitable with the need
    sample_rate = 1 / 0.005  # Hz
    cutoff_freq = 6   # Hz
    ax_filtered_lowpass = IIRLowPassFilter(cutoff_freq, sample_rate, order=1)
    ay_filtered_lowpass = IIRLowPassFilter(cutoff_freq, sample_rate, order=1)

    # Kalman filter initializer
    # Parameters can be tuned to be suitable with the need
    initial_state = np.array([0, 0, 0, 0])  # [ax, ay, vx, vy]
    initial_covariance = np.eye(4) * 0.1
    process_noise = np.eye(4) * 0.01
    measurement_noise = np.eye(2) * 0.1

    ekf = RealTimeEKF(initial_state, initial_covariance, process_noise, measurement_noise)
    ekf.start()  # Start the filtering thread

    # Other Variable Initializer
    previous_time = time.time()
    error_roll = 0
    error_pitch = 0 

    # Main control loop
    while True:
        now = time.time()
        if now - last_loop < 0.005:  # config.dt (200Hz control loop)
            continue
        last_loop = time.time()

        # Read imu data
        quat_orientation = (
            imu.read_orientation() if use_imu else np.array([1, 0, 0, 0])
        )
        state.quat_orientation = quat_orientation
        
        # IMU data processing
        imu_data = esp32.imu_get_data()
        roll_angle = angle_converter_roll(imu_data['ax'], imu_data['ay'], imu_data['az'])
        pitch_angle = angle_converter_pitch(imu_data['ax'], imu_data['ay'], imu_data['az'])
        
        # Sensor fusion pipeline
        ekf.add_measurement(ax_filtered_lowpass.update(roll_angle), 
                           ay_filtered_lowpass.update(pitch_angle)) #update ekf data 
        filtered = ekf.get_filtered_output() #get filtered angle data
        filtered_roll_angle = filtered[0]
        filtered_pitch_angle = filtered[1]
        
        # Balance correction logic
        if (abs(filtered_roll_angle) > 1 or abs(filtered_pitch_angle) > 1): #Threshold for the change of roll and pitch angle 
            if movementCtl.movement_now_number >= lib_length - 1 and movementCtl.tick >= movementCtl.now_ticks: #Finish the previous movement
                elapsed = time.time() - previous_time
                #Calculate driven angles by PID controller
                error_roll = pid_roll.compute(filtered_roll_angle, elapsed)
                error_pitch = pid_pitch.compute(-filtered_pitch_angle, elapsed)
                previous_time = time.time()
                #Create the movement
                add_movement(error_roll, error_pitch)
        
        # Movement control
        movementCtl.runMovementScheme()
        command.legslocation = movementCtl.getMovemenLegsLocation()
        command.horizontal_velocity = movementCtl.getMovemenSpeed()
        command.roll = movementCtl.attitude_now[0]
        command.pitch = movementCtl.attitude_now[1]
        command.yaw = movementCtl.attitude_now[2]
        command.yaw_rate = movementCtl.getMovemenTurn()
        
        # Run controller and update hardware
        controller.run(state, command, disp)
        hardware_interface.set_actuator_postions(state.joint_angles)
        command = Command()

if __name__ == "__main__":
    main()
