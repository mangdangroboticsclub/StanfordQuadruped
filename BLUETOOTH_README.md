# MiniPupper Bluetooth Interface Documentation

This document describes the Bluetooth Low Energy (BLE) interface implemented for the MiniPupper robot. This interface enables control via:
1.  **Web Joystick**: Continuous analog control for manual driving.
2.  **MCP Block Programming**: Discrete command execution for programmatic control (e.g., Scratch/Blockly).

## Architecture

The system consists of three main components:

1.  **BLE Server (`minipupper_ble_server_bluez.py`)**:
    *   Uses `dbus` and `BlueZ` to host a GATT server.
    *   Exposes a custom Service and Characteristic.
    *   Handles the MCP protocol (JSON-RPC over BLE) for tool calls.
    *   Handles chunked message reassembly for large payloads.

2.  **Bluetooth Interface (`src/BluetoothInterface.py`)**:
    *   Acts as a bridge between the BLE server and the robot controller.
    *   Mimics the API of the original `JoystickInterface`.
    *   Manages a thread-safe queue for movement commands.
    *   Handles the "Wake Up" / "Rest" state machine to keep the robot active during block execution.

3.  **Main Runner (`run_robot_bluetooth.py`)**:
    *   Initializes the robot hardware, controller, and state.
    *   Starts the BLE server in a background thread.
    *   Runs the main control loop, fetching commands from the `BluetoothInterface`.

## BLE Specification

*   **Service UUID**: `0d9be2a0-4757-43d9-83df-704ae274b8df`
*   **Characteristic UUID**: `8116d8c0-d45d-4fdf-998e-33ab8c471d59`
    *   Properties: `Read`, `Write`, `Notify`

### Protocol
The interface uses the Model Context Protocol (MCP) over BLE. Messages are JSON objects.

**Example Tool Call (Client -> Robot):**
```json
{
  "type": "mcp",
  "payload": {
    "method": "tools/call",
    "params": {
      "name": "move_forward",
      "arguments": {
        "time": 2.0
      }
    }
  }
}
```

**Example Joystick Data (Client -> Robot):**
```json
{
  "type": "joystick",
  "data": {
    "lx": 0.5,
    "ly": 1.0,
    "rx": 0.0,
    "ry": 0.0,
    "message_rate": 50
  }
}
```

## Available Tools

The following tools are exposed to the MCP client:

| Tool Name | Arguments | Description |
| :--- | :--- | :--- |
| `wake_up` | None | **Crucial**: Wakes the robot and keeps it active indefinitely. Must be called at the start of a block program. |
| `rest` | None | Puts the robot to sleep and disables the "force active" mode. |
| `move_forward` | `time` (sec) | Moves forward at 0.15 m/s. |
| `move_backward` | `time` (sec) | Moves backward at 0.15 m/s. |
| `move_left` | `time` (sec) | Strafes left. |
| `move_right` | `time` (sec) | Strafes right. |
| `turn_left` | `time` (sec), `rate` (rad/s) | Turns left in place. |
| `turn_right` | `time` (sec), `rate` (rad/s) | Turns right in place. |
| `look_up` | `time` (sec) | Pitches the body up. |
| `look_down` | `time` (sec) | Pitches the body down. |
| `sit` | `time` (sec) | Lowers the body height. |
| `stand` | None | Resets to neutral standing pose. |
| `trot` | None | Activates trotting gait. |
| `hop` | None | Activates hopping gait. |
| `bark` | None | Plays a bark sound/animation (placeholder). |

## Usage

### 1. Running the Robot
Run the Bluetooth runner with root privileges (required for BlueZ access):
```bash
sudo python3 run_robot_bluetooth.py
```

### 2. Connecting
*   **Web App**: Open the compatible web joystick app in a BLE-supported browser (Chrome/Edge).
*   **Block Programming**: Connect via the MCP-enabled block interface.


