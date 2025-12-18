"""
MCP Tools Configuration for MiniPupper Block Programming Interface
Defines available tools/commands and their validation schemas
"""

TOOLS = [
    # ===== Basic Commands =====
    {
        "name": "bark",
        "description": "Test command to verify Bluetooth connectivity - prints 'bark' to console",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "wake_up",
        "description": "Activate the robot (equivalent to L1 button). Puts robot in active standing mode.",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "rest",
        "description": "Put robot in rest mode (equivalent to L1 button). Deactivates all movement.",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "self.system.quit",
        "description": "Compatibility command for Block-Xiaozhi stop flag. Deactivates robot (same as rest).",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    
    # ===== Non-Trot Look Commands (Active state, not in trot mode) =====
    {
        "name": "look_up",
        "description": "Tilt robot body to look up (pitch up). Requires active state, not trot mode.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "time": {
                    "type": "number",
                    "description": "Duration to hold the pose in seconds (default: 1.0)",
                    "minimum": 0.1,
                    "maximum": 10.0
                }
            },
            "required": []
        }
    },
    {
        "name": "look_down",
        "description": "Tilt robot body to look down (pitch down). Requires active state, not trot mode.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "time": {
                    "type": "number",
                    "description": "Duration to hold the pose in seconds (default: 1.0)",
                    "minimum": 0.1,
                    "maximum": 10.0
                }
            },
            "required": []
        }
    },
    {
        "name": "look_left",
        "description": "Roll robot body to look left. Requires active state, not trot mode.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "time": {
                    "type": "number",
                    "description": "Duration to hold the pose in seconds (default: 1.0)",
                    "minimum": 0.1,
                    "maximum": 10.0
                }
            },
            "required": []
        }
    },
    {
        "name": "look_right",
        "description": "Roll robot body to look right. Requires active state, not trot mode.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "time": {
                    "type": "number",
                    "description": "Duration to hold the pose in seconds (default: 1.0)",
                    "minimum": 0.1,
                    "maximum": 10.0
                }
            },
            "required": []
        }
    },
    {
        "name": "look_up_right",
        "description": "Tilt robot body up and right (pitch up + roll right). Requires active state, not trot mode.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "time": {
                    "type": "number",
                    "description": "Duration to hold the pose in seconds (default: 1.0)",
                    "minimum": 0.1,
                    "maximum": 10.0
                }
            },
            "required": []
        }
    },
    {
        "name": "look_up_left",
        "description": "Tilt robot body up and left (pitch up + roll left). Requires active state, not trot mode.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "time": {
                    "type": "number",
                    "description": "Duration to hold the pose in seconds (default: 1.0)",
                    "minimum": 0.1,
                    "maximum": 10.0
                }
            },
            "required": []
        }
    },
    {
        "name": "look_down_right",
        "description": "Tilt robot body down and right (pitch down + roll right). Requires active state, not trot mode.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "time": {
                    "type": "number",
                    "description": "Duration to hold the pose in seconds (default: 1.0)",
                    "minimum": 0.1,
                    "maximum": 10.0
                }
            },
            "required": []
        }
    },
    {
        "name": "look_down_left",
        "description": "Tilt robot body down and left (pitch down + roll left). Requires active state, not trot mode.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "time": {
                    "type": "number",
                    "description": "Duration to hold the pose in seconds (default: 1.0)",
                    "minimum": 0.1,
                    "maximum": 10.0
                }
            },
            "required": []
        }
    },
    
    # ===== Movement Commands (Trot mode handled automatically) =====
    {
        "name": "move_forward",
        "description": "Move robot forward. Trot mode is automatically activated.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "time": {
                    "type": "number",
                    "description": "Duration to move forward in seconds (default: 1.0)",
                    "minimum": 0.1,
                    "maximum": 10.0
                }
            },
            "required": []
        }
    },
    {
        "name": "move_backward",
        "description": "Move robot backward. Trot mode is automatically activated.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "time": {
                    "type": "number",
                    "description": "Duration to move backward in seconds (default: 1.0)",
                    "minimum": 0.1,
                    "maximum": 10.0
                }
            },
            "required": []
        }
    },
    {
        "name": "move_left",
        "description": "Move robot left (strafe). Trot mode is automatically activated.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "time": {
                    "type": "number",
                    "description": "Duration to move left in seconds (default: 1.0)",
                    "minimum": 0.1,
                    "maximum": 10.0
                }
            },
            "required": []
        }
    },
    {
        "name": "move_right",
        "description": "Move robot right (strafe). Trot mode is automatically activated.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "time": {
                    "type": "number",
                    "description": "Duration to move right in seconds (default: 1.0)",
                    "minimum": 0.1,
                    "maximum": 10.0
                }
            },
            "required": []
        }
    },
    {
        "name": "move_forward_left",
        "description": "Move robot diagonally forward-left. Trot mode is automatically activated.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "time": {
                    "type": "number",
                    "description": "Duration to move in seconds (default: 1.0)",
                    "minimum": 0.1,
                    "maximum": 10.0
                }
            },
            "required": []
        }
    },
    {
        "name": "move_forward_right",
        "description": "Move robot diagonally forward-right. Trot mode is automatically activated.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "time": {
                    "type": "number",
                    "description": "Duration to move in seconds (default: 1.0)",
                    "minimum": 0.1,
                    "maximum": 10.0
                }
            },
            "required": []
        }
    },
    {
        "name": "move_backward_left",
        "description": "Move robot diagonally backward-left. Trot mode is automatically activated.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "time": {
                    "type": "number",
                    "description": "Duration to move in seconds (default: 1.0)",
                    "minimum": 0.1,
                    "maximum": 10.0
                }
            },
            "required": []
        }
    },
    {
        "name": "move_backward_right",
        "description": "Move robot diagonally backward-right. Trot mode is automatically activated.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "time": {
                    "type": "number",
                    "description": "Duration to move in seconds (default: 1.0)",
                    "minimum": 0.1,
                    "maximum": 10.0
                }
            },
            "required": []
        }
    },
    {
        "name": "turn_left",
        "description": "Turn robot left (yaw). Trot mode is automatically activated.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "time": {
                    "type": "number",
                    "description": "Duration to turn in seconds (default: 1.0)",
                    "minimum": 0.1,
                    "maximum": 10.0
                },
                "rate": {
                    "type": "number",
                    "description": "Yaw rate in rad/s (default: 0.8, max: 1.5)",
                    "minimum": 0.1,
                    "maximum": 1.5
                }
            },
            "required": []
        }
    },
    {
        "name": "turn_right",
        "description": "Turn robot right (yaw). Trot mode is automatically activated.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "time": {
                    "type": "number",
                    "description": "Duration to turn in seconds (default: 1.0)",
                    "minimum": 0.1,
                    "maximum": 10.0
                },
                "rate": {
                    "type": "number",
                    "description": "Yaw rate in rad/s (default: 0.8, max: 1.5)",
                    "minimum": 0.1,
                    "maximum": 1.5
                }
            },
            "required": []
        }
    }
]


def validate_tool_arguments(tool_name: str, arguments: dict) -> tuple:
    """
    Validate tool arguments against the schema
    
    Args:
        tool_name: Name of the tool to validate
        arguments: Dictionary of arguments to validate
        
    Returns:
        Tuple of (is_valid: bool, error_message: str or None)
    """
    # Find the tool
    tool = None
    for t in TOOLS:
        if t["name"] == tool_name:
            tool = t
            break
    
    if not tool:
        return False, f"Tool '{tool_name}' not found"
    
    schema = tool.get("inputSchema", {})
    properties = schema.get("properties", {})
    required = schema.get("required", [])
    
    # Check required parameters
    for req in required:
        if req not in arguments:
            return False, f"Missing required parameter: {req}"
    
    # Validate each provided argument
    for arg_name, arg_value in arguments.items():
        if arg_name not in properties:
            return False, f"Unknown parameter: {arg_name}"
        
        prop = properties[arg_name]
        prop_type = prop.get("type")
        
        # Type checking
        if prop_type == "number":
            if not isinstance(arg_value, (int, float)):
                return False, f"Parameter '{arg_name}' must be a number"
            
            # Range checking
            if "minimum" in prop and arg_value < prop["minimum"]:
                return False, f"Parameter '{arg_name}' must be >= {prop['minimum']}"
            if "maximum" in prop and arg_value > prop["maximum"]:
                return False, f"Parameter '{arg_name}' must be <= {prop['maximum']}"
        
        elif prop_type == "string":
            if not isinstance(arg_value, str):
                return False, f"Parameter '{arg_name}' must be a string"
    
    return True, None
