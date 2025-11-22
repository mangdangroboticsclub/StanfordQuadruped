"""
MCP Tools Configuration for MiniPupper Block Programming Interface
Defines available tools/commands and their validation schemas
"""

TOOLS = [
    {
        "name": "bark",
        "description": "Make the robot bark (play a sound or perform a bark animation)",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "move_forward",
        "description": "Move the robot forward at 0.15m/s for a specified duration",
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
        "description": "Move the robot backward at 0.15m/s for a specified duration",
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
        "description": "Move the robot left at 0.15m/s for a specified duration",
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
        "description": "Move the robot right at 0.15m/s for a specified duration",
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
        "name": "turn_left",
        "description": "Turn the robot left (yaw) at a specified rate for a duration",
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
        "description": "Turn the robot right (yaw) at a specified rate for a duration",
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
        "name": "look_up",
        "description": "Tilt the robot's body to look up (pitch up)",
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
        "description": "Tilt the robot's body to look down (pitch down)",
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
        "name": "sit",
        "description": "Make the robot sit down",
        "inputSchema": {
            "type": "object",
            "properties": {
                "time": {
                    "type": "number",
                    "description": "Duration to stay seated in seconds (default: 2.0)",
                    "minimum": 0.1,
                    "maximum": 10.0
                }
            },
            "required": []
        }
    },
    {
        "name": "stand",
        "description": "Return robot to default standing position",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "hop",
        "description": "Make the robot hop/jump",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "trot",
        "description": "Activate trotting gait mode",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "rest",
        "description": "Put the robot in rest mode (deactivate movement)",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "wake_up",
        "description": "Wake up the robot and keep it active until explicitly rested",
        "inputSchema": {
            "type": "object",
            "properties": {},
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
