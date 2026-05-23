"""
Bluetooth Interface for MiniPupper
Provides a unified interface for BLE control, supporting both:
1. Web app joystick simulation (continuous analog control)
2. MCP block programming (discrete commands)

This module mirrors the JoystickInterface API but receives commands via BLE
"""

import numpy as np
import time
import threading
from src.State import BehaviorState, State
from src.Command import Command
from src.Utilities import deadband, clipped_first_order_filter


class BluetoothInterface:
    """
    Bluetooth interface that mimics JoystickInterface but receives commands via BLE
    """
    
    # Constants for look commands (defined here to avoid config dependency issues)
    MAX_YAW_ANGLE = 60.0 * np.pi / 180.0   # ~30 degrees for look left/right
    
    def __init__(self, config):
        self.config = config
        self.previous_gait_toggle = 0
        self.previous_state = BehaviorState.REST
        self.previous_hop_toggle = 0
        self.previous_activate_toggle = 0
        self.previous_dance_activate_toggle = 0
        
        # Shared state for BLE communication
        self.lock = threading.RLock()
        self.current_msg = self._get_default_message()
        self.last_update_time = time.time()
        self.timeout = 0.5  # seconds
        self.deactivation_timeout = 2.0 # seconds, grace period before deactivating
        self.force_active = False # Flag to keep robot active until explicit stop
        
        # Movement command queue for MCP block programming
        self.movement_queue = []
        self.current_movement = None
        self.movement_start_time = None
        
        # Track trot state for automatic trot management
        self.auto_trot_active = False
        self.needs_trot_activation = False
        self.needs_trot_deactivation = False
        
    def _get_default_message(self):
        """Return default message structure (neutral position)"""
        return {
            # Analog stick values (-1.0 to 1.0)
            "lx": 0.0,  # left stick X (strafe left/right)
            "ly": 0.0,  # left stick Y (forward/backward)
            "rx": 0.0,  # right stick X (yaw left/right)
            "ry": 0.0,  # right stick Y (pitch up/down)
            
            # D-pad values (-1, 0, or 1)
            "dpadx": 0,  # D-pad X (roll)
            "dpady": 0,  # D-pad Y (height)
            
            # Button states (0 or 1)
            "R1": 0,      # Trot toggle
            "L1": 0,      # Activate toggle
            "x": 0,       # Hop toggle
            "circle": 0,  # Dance toggle
            "triangle": 0,  # Shutdown
            
            # Metadata
            "message_rate": 50,
            "timestamp": time.time()
        }
    
    def update_message(self, msg_update):
        """
        Update the current message with new values from BLE
        
        Args:
            msg_update: Dictionary with updated values (can be partial)
        """
        with self.lock:
            self.current_msg.update(msg_update)
            self.current_msg["timestamp"] = time.time()
            self.last_update_time = time.time()
    
    def queue_movement_command(self, command_type, duration=1.0, rate=None):
        """
        Queue a timed movement command (for MCP block programming)
        Movement commands automatically activate trot mode.
        
        Args:
            command_type: Type of movement ('forward', 'backward', 'left', 'right', 'turn_left', 'turn_right')
            duration: How long to execute the movement in seconds
            rate: Optional rate parameter (e.g., yaw rate for turns)
        """
        movement = {
            "type": command_type,
            "duration": duration,
            "rate": rate,
            "start_time": None,  # Will be set when movement starts
            "requires_trot": True  # Flag to indicate this needs trot mode
        }
        with self.lock:
            self.movement_queue.append(movement)
            self.last_update_time = time.time()
    
    def queue_pose_command(self, pose_type, duration=1.0):
        """
        Queue a pose/attitude command (look commands)
        
        Args:
            pose_type: Type of pose ('look_up', 'look_down', 'look_left', 'look_right', 
                      'look_up_left', 'look_up_right', 'look_down_left', 'look_down_right')
            duration: How long to hold the pose
        """
        pose = {
            "type": pose_type,
            "duration": duration,
            "start_time": None
        }
        with self.lock:
            self.movement_queue.append(pose)
            self.last_update_time = time.time()
    
    def queue_discrete_command(self, command_type):
        """
        Queue a discrete command (trot, wake_up, rest, etc.)
        
        Args:
            command_type: Type of command ('trot', 'wake_up', 'rest')
        """
        cmd = {
            "type": command_type,
            "discrete": True
        }
        with self.lock:
            self.movement_queue.append(cmd)
            self.last_update_time = time.time()
    
    def _process_movement_queue(self, state, command):
        """
        Process queued movement commands and update the command object.
        Automatically manages trot mode for movement commands.
        
        Args:
            state: Current robot state (for incremental updates)
            command: Command object to update
        
        Returns:
            True if a queued movement is active, False otherwise
        """
        with self.lock:
            current_time = time.time()
            
            # Check if current movement has finished
            if self.current_movement:
                if self.current_movement.get("discrete"):
                    # Discrete commands execute immediately
                    self.current_movement = None
                elif self.current_movement["start_time"] and \
                     (current_time - self.current_movement["start_time"]) >= self.current_movement["duration"]:
                    # Timed movement finished
                    # If this was a trot-requiring movement and no more trot movements queued, deactivate trot
                    if self.current_movement.get("requires_trot"):
                        has_more_trot_movements = any(m.get("requires_trot", False) for m in self.movement_queue)
                        if not has_more_trot_movements and self.auto_trot_active:
                            self.needs_trot_deactivation = True
                    self.current_movement = None
            
            # Handle trot deactivation
            if self.needs_trot_deactivation:
                command.trot_event = True
                self.auto_trot_active = False
                self.needs_trot_deactivation = False
                return True
            
            # Handle trot activation (must happen before starting movement)
            if self.needs_trot_activation:
                command.trot_event = True
                self.auto_trot_active = True
                self.needs_trot_activation = False
                return True
            
            # Start next queued movement if available
            if not self.current_movement and len(self.movement_queue) > 0:
                self.current_movement = self.movement_queue.pop(0)
                
                # If this movement requires trot and trot is not active, schedule activation
                if self.current_movement.get("requires_trot") and not self.auto_trot_active:
                    self.needs_trot_activation = True
                    # Put movement back in queue to execute after trot activates
                    self.movement_queue.insert(0, self.current_movement)
                    self.current_movement = None
                    # Trigger trot activation on next call
                    command.trot_event = True
                    self.auto_trot_active = True
                    self.needs_trot_activation = False
                    return True
                
                if not self.current_movement.get("discrete"):
                    self.current_movement["start_time"] = current_time
            
            # Apply current movement to command
            if self.current_movement:
                mv = self.current_movement
                mv_type = mv["type"]
                
                # Discrete commands
                if mv_type == "wake_up":
                    # Activate robot (one-way, not toggle)
                    command.activate_event = True
                elif mv_type == "rest":
                    # Deactivate robot (one-way, not toggle)
                    # First deactivate trot if active
                    if self.auto_trot_active:
                        self.needs_trot_deactivation = True
                        self.auto_trot_active = False
                    # Set force_active to False to allow deactivation
                    self.set_force_active(False)
                    command.activate_event = True
                
                # Movement commands (trot mode handled automatically)
                elif mv_type == "forward":
                    command.horizontal_velocity = np.array([self.config.max_x_velocity * 0.3, 0.0])
                elif mv_type == "backward":
                    command.horizontal_velocity = np.array([-self.config.max_x_velocity * 0.3, 0.0])
                elif mv_type == "left":
                    command.horizontal_velocity = np.array([0.0, self.config.max_y_velocity * 0.3])
                elif mv_type == "right":
                    command.horizontal_velocity = np.array([0.0, -self.config.max_y_velocity * 0.3])
                elif mv_type == "forward_left":
                    command.horizontal_velocity = np.array([self.config.max_x_velocity * 0.21, self.config.max_y_velocity * 0.21])
                elif mv_type == "forward_right":
                    command.horizontal_velocity = np.array([self.config.max_x_velocity * 0.21, -self.config.max_y_velocity * 0.21])
                elif mv_type == "backward_left":
                    command.horizontal_velocity = np.array([-self.config.max_x_velocity * 0.21, self.config.max_y_velocity * 0.21])
                elif mv_type == "backward_right":
                    command.horizontal_velocity = np.array([-self.config.max_x_velocity * 0.21, -self.config.max_y_velocity * 0.21])
                elif mv_type == "turn_left":
                    rate = mv.get("rate", 0.8)
                    command.yaw_rate = rate
                elif mv_type == "turn_right":
                    rate = mv.get("rate", 0.8)
                    command.yaw_rate = -rate
                
                # Pose/Look commands (require active but not trot mode)
                elif mv_type == "look_up":
                    command.pitch = self.config.max_pitch * 0.8
                elif mv_type == "look_down":
                    command.pitch = -self.config.max_pitch * 0.8
                elif mv_type == "look_left":
                    # Use yaw_rate for head movement in non-trot state (like web joystick rx)
                    command.yaw_rate = self.config.max_yaw_rate * 0.8
                elif mv_type == "look_right":
                    # Use yaw_rate for head movement in non-trot state (like web joystick rx)
                    command.yaw_rate = -self.config.max_yaw_rate * 0.8
                elif mv_type == "look_up_left":
                    command.pitch = self.config.max_pitch * 0.35
                    command.yaw_rate = self.config.max_yaw_rate * 0.35
                elif mv_type == "look_up_right":
                    command.pitch = self.config.max_pitch * 0.35
                    command.yaw_rate = -self.config.max_yaw_rate * 0.35
                elif mv_type == "look_down_left":
                    command.pitch = -self.config.max_pitch * 0.35
                    command.yaw_rate = self.config.max_yaw_rate * 0.35
                elif mv_type == "look_down_right":
                    command.pitch = -self.config.max_pitch * 0.35
                    command.yaw_rate = -self.config.max_yaw_rate * 0.35
                    command.roll = state.roll + self.config.dt * self.config.roll_speed * -1.0
                
                return True
        
        return False
    
    def get_command(self, state, do_print=False):
        """
        Get command from BLE interface, compatible with JoystickInterface API
        
        Args:
            state: Current robot state
            do_print: Whether to print debug info
            
        Returns:
            Command object with movement parameters
        """
        command = Command()
        
        # Check for timeout
        with self.lock:
            # If we have a queued movement, we are "connected" and should process it
            # even if the last joystick message was old
            if self.current_movement or len(self.movement_queue) > 0:
                self._process_movement_queue(state, command)
                return command

            if (time.time() - self.last_update_time) > self.timeout:
                if do_print:
                    print("BLE Timed out")
                return command
            
            msg = self.current_msg.copy()
        
        # If there are queued movements, process them first
        if self._process_movement_queue(state, command):
            # Queued movement is active, return that command
            return command
        
        ####### Handle discrete commands ########
        
        # Check if requesting a state transition to trotting
        gait_toggle = msg["R1"]
        command.trot_event = (gait_toggle == 1 and self.previous_gait_toggle == 0)
        
        # Check if requesting a state transition to hopping
        # Optional: web joystick doesn't send these (future features)
        hop_toggle = msg.get("x", 0)
        command.hop_event = (hop_toggle == 1 and self.previous_hop_toggle == 0)
        
        # L1 is optional (web joystick doesn't send it, uses auto-activation instead)
        activate_toggle = msg.get("L1", 0)
        command.activate_event = (activate_toggle == 1 and self.previous_activate_toggle == 0)
        
        # Dance is optional (web joystick doesn't send it, future feature)
        dance_activate_toggle = msg.get("circle", 0)
        command.dance_activate_event = (dance_activate_toggle == 1 and self.previous_dance_activate_toggle == 0)
        
        # Update previous values for toggles
        self.previous_gait_toggle = gait_toggle
        self.previous_hop_toggle = hop_toggle
        self.previous_activate_toggle = activate_toggle
        self.previous_dance_activate_toggle = dance_activate_toggle
        
        ####### Handle continuous commands ########
        x_vel = msg["ly"] * self.config.max_x_velocity
        y_vel = msg["lx"] * -self.config.max_y_velocity
        command.horizontal_velocity = np.array([x_vel, y_vel])
        command.yaw_rate = msg["rx"] * -self.config.max_yaw_rate
        
        message_rate = msg["message_rate"]
        message_dt = 1.0 / message_rate
        
        pitch = msg["ry"] * self.config.max_pitch
        deadbanded_pitch = deadband(pitch, self.config.pitch_deadband)
        pitch_rate = clipped_first_order_filter(
            state.pitch,
            deadbanded_pitch,
            self.config.max_pitch_rate,
            self.config.pitch_time_constant,
        )
        command.pitch = state.pitch + message_dt * pitch_rate
        
        height_movement = msg["dpady"]
        command.height = state.height - message_dt * self.config.z_speed * height_movement
        
        roll_movement = -msg["dpadx"]
        command.roll = state.roll + message_dt * self.config.roll_speed * roll_movement
        
        return command
    
    def set_color(self, color):
        """
        Set LED color (for compatibility with JoystickInterface)
        Can be implemented to send BLE notification back to client
        """
        # TODO: Implement BLE notification to update client UI color
        pass
    
    def is_connected(self):
        """Check if BLE client is connected (based on recent updates or active queue)"""
        with self.lock:
            if self.force_active:
                return True
                
            # Use deactivation_timeout (grace period) to prevent flickering
            is_active = (time.time() - self.last_update_time) < self.deactivation_timeout
            is_executing = self.current_movement is not None or len(self.movement_queue) > 0
            return is_active or is_executing
            
    def set_force_active(self, active):
        """Set the force active flag to keep robot awake"""
        with self.lock:
            self.force_active = active
            if active:
                self.last_update_time = time.time()
    
    def clear_all_queues(self):
        """
        Clear all movement queues and stop current movement.
        Used as an emergency stop / failsafe when system quit is received.
        """
        with self.lock:
            # Clear the movement queue
            self.movement_queue.clear()
            
            # Stop current movement
            self.current_movement = None
            self.movement_start_time = None
            
            # Reset trot state flags
            self.auto_trot_active = False
            self.needs_trot_activation = False
            self.needs_trot_deactivation = False
            
            # Disable force active mode
            self.force_active = False
            
            # Reset to default neutral message
            self.current_msg = self._get_default_message()
            
            print("[BluetoothInterface] All queues cleared - emergency stop")
