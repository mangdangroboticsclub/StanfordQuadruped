#!/usr/bin/env python3
"""
BLE MCP Server for Minipupper-v2
Implements the Block-Xiaozhi BLE API specification using BlueZ D-Bus
"""

import json
import sys
import os
import time
import threading
import dbus
import dbus.exceptions
import dbus.mainloop.glib
import dbus.service
from gi.repository import GLib
from tools_config import TOOLS, validate_tool_arguments

# Add StanfordQuadruped project root to path so `src` package imports resolve
# MovementGroup.py expects to import `src.MovementScheme`, so the project root
# (one level above `src`) must be on sys.path.
project_root = '/home/ubuntu/StanfordQuadruped'
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Try multiple import strategies for robustness:
MOVEMENT_API_AVAILABLE = False
try:
    # Prefer the package import that MovementGroup expects
    from src.MovementGroup import MovementGroups
    MOVEMENT_API_AVAILABLE = True
    print("✓ MovementGroup API loaded via 'src.MovementGroup'")
except Exception:
    try:
        # Fallback: import module directly if src isn't a package on the Pi
        from MovementGroup import MovementGroups
        MOVEMENT_API_AVAILABLE = True
        print("✓ MovementGroup API loaded via 'MovementGroup'")
    except Exception as e:
        print(f"✗ Warning: Could not import MovementGroup API: {e}")
        print("  Movement commands will only print to console")
        MOVEMENT_API_AVAILABLE = False

# BLE Service and Characteristic UUIDs (from specification)
SERVICE_UUID = "0d9be2a0-4757-43d9-83df-704ae274b8df"
CHARACTERISTIC_UUID = "8116d8c0-d45d-4fdf-998e-33ab8c471d59"
DEVICE_NAME = "Minipupper-v2"

# D-Bus constants
BLUEZ_SERVICE_NAME = 'org.bluez'
GATT_MANAGER_IFACE = 'org.bluez.GattManager1'
DBUS_OM_IFACE = 'org.freedesktop.DBus.ObjectManager'
DBUS_PROP_IFACE = 'org.freedesktop.DBus.Properties'
GATT_SERVICE_IFACE = 'org.bluez.GattService1'
GATT_CHRC_IFACE = 'org.bluez.GattCharacteristic1'
LE_ADVERTISING_MANAGER_IFACE = 'org.bluez.LEAdvertisingManager1'
LE_ADVERTISEMENT_IFACE = 'org.bluez.LEAdvertisement1'


class InvalidArgsException(dbus.exceptions.DBusException):
    _dbus_error_name = 'org.freedesktop.DBus.Error.InvalidArgs'


class NotSupportedException(dbus.exceptions.DBusException):
    _dbus_error_name = 'org.bluez.Error.NotSupported'


class NotPermittedException(dbus.exceptions.DBusException):
    _dbus_error_name = 'org.bluez.Error.NotPermitted'


class Application(dbus.service.Object):
    """
    org.bluez.GattApplication1 interface implementation
    """
    def __init__(self, bus):
        self.path = '/'
        self.services = []
        dbus.service.Object.__init__(self, bus, self.path)

    def get_path(self):
        return dbus.ObjectPath(self.path)

    def add_service(self, service):
        self.services.append(service)

    @dbus.service.method(DBUS_OM_IFACE, out_signature='a{oa{sa{sv}}}')
    def GetManagedObjects(self):
        response = {}
        for service in self.services:
            response[service.get_path()] = service.get_properties()
            chrcs = service.get_characteristics()
            for chrc in chrcs:
                response[chrc.get_path()] = chrc.get_properties()
        return response


class Service(dbus.service.Object):
    """
    org.bluez.GattService1 interface implementation
    """
    PATH_BASE = '/org/bluez/minipupper/service'

    def __init__(self, bus, index, uuid, primary):
        self.path = self.PATH_BASE + str(index)
        self.bus = bus
        self.uuid = uuid
        self.primary = primary
        self.characteristics = []
        dbus.service.Object.__init__(self, bus, self.path)

    def get_properties(self):
        return {
            GATT_SERVICE_IFACE: {
                'UUID': self.uuid,
                'Primary': self.primary,
                'Characteristics': dbus.Array(
                    self.get_characteristic_paths(),
                    signature='o')
            }
        }

    def get_path(self):
        return dbus.ObjectPath(self.path)

    def add_characteristic(self, characteristic):
        self.characteristics.append(characteristic)

    def get_characteristic_paths(self):
        result = []
        for chrc in self.characteristics:
            result.append(chrc.get_path())
        return result

    def get_characteristics(self):
        return self.characteristics

    @dbus.service.method(DBUS_PROP_IFACE,
                         in_signature='s',
                         out_signature='a{sv}')
    def GetAll(self, interface):
        if interface != GATT_SERVICE_IFACE:
            raise InvalidArgsException()
        return self.get_properties()[GATT_SERVICE_IFACE]


class Characteristic(dbus.service.Object):
    """
    org.bluez.GattCharacteristic1 interface implementation
    """
    def __init__(self, bus, index, uuid, flags, service):
        self.path = service.path + '/char' + str(index)
        self.bus = bus
        self.uuid = uuid
        self.service = service
        self.flags = flags
        self.value = []
        dbus.service.Object.__init__(self, bus, self.path)

    def get_properties(self):
        return {
            GATT_CHRC_IFACE: {
                'Service': self.service.get_path(),
                'UUID': self.uuid,
                'Flags': self.flags,
            }
        }

    def get_path(self):
        return dbus.ObjectPath(self.path)

    @dbus.service.method(DBUS_PROP_IFACE,
                         in_signature='s',
                         out_signature='a{sv}')
    def GetAll(self, interface):
        if interface != GATT_CHRC_IFACE:
            raise InvalidArgsException()
        return self.get_properties()[GATT_CHRC_IFACE]

    @dbus.service.method(GATT_CHRC_IFACE,
                         in_signature='a{sv}',
                         out_signature='ay')
    def ReadValue(self, options):
        print('[Read Request]')
        return self.value

    @dbus.service.method(GATT_CHRC_IFACE, in_signature='aya{sv}')
    def WriteValue(self, value, options):
        print('[Write Request]')
        self.value = value

    @dbus.service.method(GATT_CHRC_IFACE)
    def StartNotify(self):
        print('[Start Notify]')

    @dbus.service.method(GATT_CHRC_IFACE)
    def StopNotify(self):
        print('[Stop Notify]')

    @dbus.service.signal(DBUS_PROP_IFACE,
                        signature='sa{sv}as')
    def PropertiesChanged(self, interface, changed, invalidated):
        pass


class MinipupperCharacteristic(Characteristic):
    """
    MCP Protocol Characteristic with READ, WRITE, NOTIFY
    Supports both MCP block programming and joystick simulation
    """
    def __init__(self, bus, index, service, bluetooth_interface=None):
        Characteristic.__init__(
            self, bus, index, CHARACTERISTIC_UUID,
            ['read', 'write', 'notify'],
            service)
        self.notifying = False
        self.value = list(b'Ready')
        
        # Reference to BluetoothInterface for joystick simulation and MCP commands
        self.bluetooth_interface = bluetooth_interface
        
        # Track last movement duration and timer
        self.last_movement_duration = 0.0
        self.movement_timer = None
        self.movement_lock = threading.Lock()
        
        # Initialize MovementGroup API if available
        if MOVEMENT_API_AVAILABLE:
            try:
                self.movement = MovementGroups()
                print("✓ MovementGroups initialized")
                print("ℹ Movement API: Velocity-based (0.15 m/s), auto-stop after duration")
            except Exception as e:
                print(f"✗ Failed to initialize MovementGroups: {e}")
                self.movement = None
        else:
            self.movement = None

    def schedule_stop(self, duration):
        """
        Schedule a stop command after the specified duration.
        Cancels any existing scheduled stop.
        """
        with self.movement_lock:
            # Cancel any existing timer
            if self.movement_timer:
                self.movement_timer.cancel()
            
            # Schedule new stop command
            def stop_movement():
                print(f"[Timer] Stopping movement after {duration}s")
                with self.movement_lock:
                    if self.movement:
                        self.movement.stop()
                        print("[Timer] Stop command queued to MovementLib")
            
            self.movement_timer = threading.Timer(duration, stop_movement)
            self.movement_timer.start()
            print(f"[Timer] Scheduled stop in {duration}s")

    def chunk_message(self, message: str, max_ble_packet: int = 512) -> list:
        """
        Split large messages into chunks for BLE transmission.
        Each chunk must be a complete JSON object that fits within max_ble_packet bytes.
        Properly handles UTF-8 encoding to avoid splitting multi-byte characters.
        """
        # Encode message to bytes first to handle UTF-8 properly
        message_bytes = message.encode('utf-8')
        
        if len(message_bytes) <= max_ble_packet:
            return [message]
        
        chunks = []
        chunk_id = f"msg-{id(message)}"
        
        # Calculate overhead for chunk JSON structure
        # {"chunk":{"id":"msg-XXXXXXXXXX","index":XX,"total":XX,"data":""}}
        # Account for variable index/total digit counts
        overhead_estimate = 120
        max_data_per_chunk = max_ble_packet - overhead_estimate
        
        # Calculate total chunks needed (working with bytes)
        total_chunks = (len(message_bytes) + max_data_per_chunk - 1) // max_data_per_chunk
        
        offset = 0
        chunk_index = 0
        
        while offset < len(message_bytes):
            # Calculate how many bytes we can fit in this chunk
            remaining = len(message_bytes) - offset
            target_size = min(max_data_per_chunk, remaining)
            
            # Find a valid UTF-8 boundary by decoding and checking
            chunk_data_bytes = message_bytes[offset:offset + target_size]
            
            # Ensure we don't split a multi-byte UTF-8 character
            # Try to decode, if it fails, reduce size until it works
            while target_size > 0:
                try:
                    chunk_data = chunk_data_bytes.decode('utf-8')
                    break
                except UnicodeDecodeError:
                    # Reduce by one byte and try again
                    target_size -= 1
                    chunk_data_bytes = message_bytes[offset:offset + target_size]
            
            if target_size == 0:
                raise Exception("Cannot find valid UTF-8 boundary")
            
            # Create chunk object
            chunk = {
                "chunk": {
                    "id": chunk_id,
                    "index": chunk_index,
                    "total": total_chunks,
                    "data": chunk_data
                }
            }
            
            # Serialize to JSON with minimal spacing
            chunk_json = json.dumps(chunk, separators=(',', ':'), ensure_ascii=False)
            
            # Verify this chunk fits within max_ble_packet
            chunk_bytes = chunk_json.encode('utf-8')
            
            # If it's too big, reduce the data size
            attempts = 0
            while len(chunk_bytes) > max_ble_packet and target_size > 0 and attempts < 10:
                # Reduce data size by 10%
                target_size = int(target_size * 0.9)
                if target_size == 0:
                    break
                
                # Re-extract data ensuring UTF-8 boundary
                chunk_data_bytes = message_bytes[offset:offset + target_size]
                while target_size > 0:
                    try:
                        chunk_data = chunk_data_bytes.decode('utf-8')
                        break
                    except UnicodeDecodeError:
                        target_size -= 1
                        chunk_data_bytes = message_bytes[offset:offset + target_size]
                
                chunk["chunk"]["data"] = chunk_data
                chunk_json = json.dumps(chunk, separators=(',', ':'), ensure_ascii=False)
                chunk_bytes = chunk_json.encode('utf-8')
                attempts += 1
            
            if target_size == 0 or len(chunk_bytes) > max_ble_packet:
                raise Exception(f"Cannot fit chunk into BLE packet size (attempted {attempts} times)")
            
            chunks.append(chunk_json)
            offset += target_size
            chunk_index += 1
        
        # Update all chunks with correct total count
        actual_total = len(chunks)
        if actual_total != total_chunks:
            for i, chunk_str in enumerate(chunks):
                chunk_obj = json.loads(chunk_str)
                chunk_obj["chunk"]["total"] = actual_total
                chunks[i] = json.dumps(chunk_obj, separators=(',', ':'), ensure_ascii=False)
        
        return chunks

    def handle_tools_list(self) -> str:
        """Handle tools/list request"""
        response = {
            "type": "mcp_response",
            "payload": {
                "result": {
                    "tools": TOOLS
                }
            }
        }
        return json.dumps(response)

    def handle_tools_call(self, params: dict) -> str:
        """Handle tools/call request"""
        tool_name = params.get("name", "")
        arguments = params.get("arguments", {})
        
        print(f"\n[Tool Call] {tool_name}", flush=True)
        print(f"[Arguments] {arguments}", flush=True)
        
        # Validate arguments
        is_valid, error_msg = validate_tool_arguments(tool_name, arguments)
        if not is_valid:
            print(f"[Validation Error] {error_msg}", flush=True)
            return json.dumps({
                "type": "mcp_response",
                "payload": {
                    "error": {
                        "code": -32602,
                        "message": f"Invalid parameters: {error_msg}"
                    }
                }
            })
        
        # Execute the tool
        try:
            if tool_name == "bark":
                print("Bark", flush=True)
                result_text = "Bark executed successfully"
                
            elif tool_name == "move_forward":
                time_duration = arguments.get("time", 1.0)
                print(f"Moving forward for {time_duration} seconds", flush=True)
                
                # Queue command via BluetoothInterface
                if self.bluetooth_interface:
                    self.bluetooth_interface.queue_movement_command("forward", time_duration)
                    result_text = f"Queued: move forward for {time_duration}s"
                else:
                    result_text = f"BluetoothInterface not available"
                
            elif tool_name == "move_backward":
                time_duration = arguments.get("time", 1.0)
                print(f"Moving backward for {time_duration} seconds", flush=True)
                
                if self.bluetooth_interface:
                    self.bluetooth_interface.queue_movement_command("backward", time_duration)
                    result_text = f"Queued: move backward for {time_duration}s"
                else:
                    result_text = f"BluetoothInterface not available"
                
            elif tool_name == "move_left":
                time_duration = arguments.get("time", 1.0)
                print(f"Moving left for {time_duration} seconds", flush=True)
                
                if self.bluetooth_interface:
                    self.bluetooth_interface.queue_movement_command("left", time_duration)
                    result_text = f"Queued: move left for {time_duration}s"
                else:
                    result_text = f"BluetoothInterface not available"
                
            elif tool_name == "move_right":
                time_duration = arguments.get("time", 1.0)
                print(f"Moving right for {time_duration} seconds", flush=True)
                
                if self.bluetooth_interface:
                    self.bluetooth_interface.queue_movement_command("right", time_duration)
                    result_text = f"Queued: move right for {time_duration}s"
                else:
                    result_text = f"BluetoothInterface not available"
            
            elif tool_name == "turn_left":
                time_duration = arguments.get("time", 1.0)
                rate = arguments.get("rate", 0.8)
                print(f"Turning left for {time_duration} seconds at rate {rate}", flush=True)
                
                if self.bluetooth_interface:
                    self.bluetooth_interface.queue_movement_command("turn_left", time_duration, rate)
                    result_text = f"Queued: turn left for {time_duration}s at {rate} rad/s"
                else:
                    result_text = f"BluetoothInterface not available"
            
            elif tool_name == "turn_right":
                time_duration = arguments.get("time", 1.0)
                rate = arguments.get("rate", 0.8)
                print(f"Turning right for {time_duration} seconds at rate {rate}", flush=True)
                
                if self.bluetooth_interface:
                    self.bluetooth_interface.queue_movement_command("turn_right", time_duration, rate)
                    result_text = f"Queued: turn right for {time_duration}s at {rate} rad/s"
                else:
                    result_text = f"BluetoothInterface not available"
            
            elif tool_name == "look_up":
                time_duration = arguments.get("time", 1.0)
                print(f"Looking up for {time_duration} seconds", flush=True)
                
                if self.bluetooth_interface:
                    self.bluetooth_interface.queue_pose_command("look_up", time_duration)
                    result_text = f"Queued: look up for {time_duration}s"
                else:
                    result_text = f"BluetoothInterface not available"
            
            elif tool_name == "look_down":
                time_duration = arguments.get("time", 1.0)
                print(f"Looking down for {time_duration} seconds", flush=True)
                
                if self.bluetooth_interface:
                    self.bluetooth_interface.queue_pose_command("look_down", time_duration)
                    result_text = f"Queued: look down for {time_duration}s"
                else:
                    result_text = f"BluetoothInterface not available"
            
            elif tool_name == "sit":
                time_duration = arguments.get("time", 2.0)
                print(f"Sitting for {time_duration} seconds", flush=True)
                
                if self.bluetooth_interface:
                    self.bluetooth_interface.queue_pose_command("sit", time_duration)
                    result_text = f"Queued: sit for {time_duration}s"
                else:
                    result_text = f"BluetoothInterface not available"
            
            elif tool_name == "stand":
                print("Standing", flush=True)
                
                if self.bluetooth_interface:
                    self.bluetooth_interface.queue_discrete_command("stand")
                    result_text = "Queued: stand"
                else:
                    result_text = "BluetoothInterface not available"
            
            elif tool_name == "hop":
                print("Hopping", flush=True)
                
                if self.bluetooth_interface:
                    self.bluetooth_interface.queue_discrete_command("hop")
                    result_text = "Queued: hop"
                else:
                    result_text = "BluetoothInterface not available"
            
            elif tool_name == "trot":
                print("Trotting", flush=True)
                
                if self.bluetooth_interface:
                    self.bluetooth_interface.queue_discrete_command("trot")
                    result_text = "Queued: trot"
                else:
                    result_text = "BluetoothInterface not available"
            
            elif tool_name == "rest":
                print("Resting", flush=True)
                
                if self.bluetooth_interface:
                    self.bluetooth_interface.queue_discrete_command("rest")
                    # Also disable force active mode
                    self.bluetooth_interface.set_force_active(False)
                    result_text = "Queued: rest"
                else:
                    result_text = "BluetoothInterface not available"
            
            elif tool_name == "wake_up":
                print("Waking Up", flush=True)
                
                if self.bluetooth_interface:
                    # Enable force active mode
                    self.bluetooth_interface.set_force_active(True)
                    result_text = "Robot is now awake and active"
                else:
                    result_text = "BluetoothInterface not available"
                
            else:
                # Tool not found
                return json.dumps({
                    "type": "mcp_response",
                    "payload": {
                        "error": {
                            "code": -32601,
                            "message": f"Tool not found: {tool_name}"
                        }
                    }
                })
            
            # Success response
            return json.dumps({
                "type": "mcp_response",
                "payload": {
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": result_text
                            }
                        ]
                    }
                }
            })
            
        except Exception as e:
            print(f"[Execution Error] {e}", flush=True)
            import traceback
            traceback.print_exc()
            return json.dumps({
                "type": "mcp_response",
                "payload": {
                    "error": {
                        "code": -32603,
                        "message": f"Execution error: {str(e)}"
                    }
                }
            })

    def handle_joystick_message(self, joystick_data: dict):
        """
        Handle joystick simulation messages from web app
        Updates the BluetoothInterface with analog stick and button values
        """
        if self.bluetooth_interface:
            # Update the bluetooth interface with new joystick data
            self.bluetooth_interface.update_message(joystick_data)
            print(f"[Joystick] Updated: lx={joystick_data.get('lx', 0):.2f}, ly={joystick_data.get('ly', 0):.2f}", flush=True)
    
    def handle_mcp_request(self, request_data: str) -> list:
        """Parse and handle MCP request, return list of response messages"""
        try:
            request = json.loads(request_data)
            print(f"\n[Received] {request}", flush=True)
            
            # Check if this is a joystick message (web app)
            if request.get("type") == "joystick":
                self.handle_joystick_message(request.get("data", {}))
                # Send acknowledgment
                return [json.dumps({"type": "joystick_ack", "status": "ok"})]
            
            if request.get("type") != "mcp":
                return [json.dumps({
                    "type": "mcp_response",
                    "payload": {
                        "error": {
                            "code": -32600,
                            "message": "Invalid request type"
                        }
                    }
                })]
            
            payload = request.get("payload", {})
            method = payload.get("method", "")
            params = payload.get("params", {})
            
            if method == "tools/list":
                response = self.handle_tools_list()
            elif method == "tools/call":
                response = self.handle_tools_call(params)
            else:
                response = json.dumps({
                    "type": "mcp_response",
                    "payload": {
                        "error": {
                            "code": -32601,
                            "message": f"Method not found: {method}"
                        }
                    }
                })
            
            # Chunk the response if needed
            return self.chunk_message(response)
            
        except json.JSONDecodeError as e:
            print(f"[Error] JSON parse error: {e}")
            return [json.dumps({
                "type": "mcp_response",
                "payload": {
                    "error": {
                        "code": -32700,
                        "message": f"Parse error: {str(e)}"
                    }
                }
            })]
        except Exception as e:
            print(f"[Error] Internal error: {e}")
            return [json.dumps({
                "type": "mcp_response",
                "payload": {
                    "error": {
                        "code": -32603,
                        "message": f"Internal error: {str(e)}"
                    }
                }
            })]

    def ReadValue(self, options):
        print('[Read Request]')
        return self.value

    def WriteValue(self, value, options):
        """Handle incoming MCP requests"""
        request_data = bytes(value).decode('utf-8')
        print(f"\n[Write Request] Received {len(request_data)} bytes")
        
        # Process the request and get response(s)
        responses = self.handle_mcp_request(request_data)
        
        # Send each response (or chunk) via notification
        for response in responses:
            response_bytes = response.encode('utf-8')
            print(f"[Sending] {len(response_bytes)} bytes")
            
            if self.notifying:
                self.value = list(response_bytes)
                self.PropertiesChanged(
                    GATT_CHRC_IFACE,
                    {'Value': dbus.Array(self.value, signature='y')},
                    []
                )

    def StartNotify(self):
        if self.notifying:
            print('[Already Notifying]')
            return
        
        self.notifying = True
        print('[Notifications Enabled]')

    def StopNotify(self):
        if not self.notifying:
            print('[Not Notifying]')
            return
        
        self.notifying = False
        print('[Notifications Disabled]')


class Advertisement(dbus.service.Object):
    """
    org.bluez.LEAdvertisement1 interface implementation
    """
    PATH_BASE = '/org/bluez/minipupper/advertisement'

    def __init__(self, bus, index, advertising_type):
        self.path = self.PATH_BASE + str(index)
        self.bus = bus
        self.ad_type = advertising_type
        self.service_uuids = None
        self.manufacturer_data = None
        self.solicit_uuids = None
        self.service_data = None
        self.local_name = DEVICE_NAME
        self.include_tx_power = False
        dbus.service.Object.__init__(self, bus, self.path)

    def get_properties(self):
        properties = dict()
        properties['Type'] = self.ad_type
        if self.service_uuids is not None:
            properties['ServiceUUIDs'] = dbus.Array(self.service_uuids,
                                                    signature='s')
        if self.solicit_uuids is not None:
            properties['SolicitUUIDs'] = dbus.Array(self.solicit_uuids,
                                                    signature='s')
        if self.manufacturer_data is not None:
            properties['ManufacturerData'] = dbus.Dictionary(
                self.manufacturer_data, signature='qv')
        if self.service_data is not None:
            properties['ServiceData'] = dbus.Dictionary(self.service_data,
                                                       signature='sv')
        if self.local_name is not None:
            properties['LocalName'] = dbus.String(self.local_name)
        if self.include_tx_power:
            properties['IncludeTxPower'] = dbus.Boolean(self.include_tx_power)
        return {LE_ADVERTISEMENT_IFACE: properties}

    def get_path(self):
        return dbus.ObjectPath(self.path)

    @dbus.service.method(DBUS_PROP_IFACE,
                         in_signature='s',
                         out_signature='a{sv}')
    def GetAll(self, interface):
        if interface != LE_ADVERTISEMENT_IFACE:
            raise InvalidArgsException()
        return self.get_properties()[LE_ADVERTISEMENT_IFACE]

    @dbus.service.method(LE_ADVERTISEMENT_IFACE,
                         in_signature='',
                         out_signature='')
    def Release(self):
        print('[Advertisement Released]')


class MinipupperAdvertisement(Advertisement):
    def __init__(self, bus, index):
        Advertisement.__init__(self, bus, index, 'peripheral')
        self.service_uuids = [SERVICE_UUID]
        self.local_name = DEVICE_NAME
        self.include_tx_power = True


def find_adapter(bus):
    """Find the first available Bluetooth adapter"""
    remote_om = dbus.Interface(bus.get_object(BLUEZ_SERVICE_NAME, '/'),
                               DBUS_OM_IFACE)
    objects = remote_om.GetManagedObjects()

    for o, props in objects.items():
        if GATT_MANAGER_IFACE in props.keys():
            return o

    return None


def main(bluetooth_interface=None):
    """
    Main entry point
    
    Args:
        bluetooth_interface: Optional BluetoothInterface instance to integrate with robot control
    """
    print(f"Starting BLE server: {DEVICE_NAME}")
    print(f"Service UUID: {SERVICE_UUID}")
    print(f"Characteristic UUID: {CHARACTERISTIC_UUID}")
    
    if bluetooth_interface:
        print("✓ BluetoothInterface provided - MCP commands will control robot")
    else:
        print("⚠ No BluetoothInterface - running in standalone mode")
    
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

    bus = dbus.SystemBus()

    adapter = find_adapter(bus)
    if not adapter:
        print('[Error] GattManager1 interface not found')
        return

    print(f'[Adapter] {adapter}')

    # Create GATT application
    app = Application(bus)
    service = Service(bus, 0, SERVICE_UUID, True)
    characteristic = MinipupperCharacteristic(bus, 0, service, bluetooth_interface)
    service.add_characteristic(characteristic)
    app.add_service(service)

    # Register GATT application
    service_manager = dbus.Interface(
        bus.get_object(BLUEZ_SERVICE_NAME, adapter),
        GATT_MANAGER_IFACE)

    ad_manager = dbus.Interface(bus.get_object(BLUEZ_SERVICE_NAME, adapter),
                                LE_ADVERTISING_MANAGER_IFACE)

    # Create and register advertisement
    advertisement = MinipupperAdvertisement(bus, 0)

    mainloop = GLib.MainLoop()

    print('[Registering GATT Application...]')
    service_manager.RegisterApplication(app.get_path(), {},
                                       reply_handler=lambda: print('[GATT Application Registered]'),
                                       error_handler=lambda e: print(f'[Error] Failed to register application: {e}'))

    print('[Registering Advertisement...]')
    ad_manager.RegisterAdvertisement(advertisement.get_path(), {},
                                    reply_handler=lambda: print('[Advertisement Registered]'),
                                    error_handler=lambda e: print(f'[Error] Failed to register advertisement: {e}'))

    print("\n" + "="*50)
    print("Minipupper-v2 BLE Server Running")
    print("="*50)
    print("Available tools:")
    for tool in TOOLS:
        print(f"  - {tool['name']}: {tool['description']}")
    print("\nWaiting for connections...")
    print("="*50 + "\n")

    try:
        mainloop.run()
    except KeyboardInterrupt:
        print("\n\nShutting down server...")
        ad_manager.UnregisterAdvertisement(advertisement.get_path())
        service_manager.UnregisterApplication(app.get_path())


if __name__ == '__main__':
    main()
