# hardware/controller.py
"""
Hardware control system following SOLID principles.
Single responsibility: control hardware devices with permission checks.
"""

from typing import Dict, Any, Optional
from abc import ABC, abstractmethod
import logging
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    requests = None
    REQUESTS_AVAILABLE = False

try:
    import serial
    SERIAL_AVAILABLE = True
except ImportError:
    SERIAL_AVAILABLE = False

logger = logging.getLogger(__name__)

class HardwareDevice(ABC):
    """Abstract base class for hardware devices."""

    @abstractmethod
    def control(self, operation: Dict[str, Any]) -> str:
        """Control the hardware device."""
        pass

class FlashlightDevice(HardwareDevice):
    """Controls flashlight/torch functionality."""

    def control(self, operation: Dict[str, Any]) -> str:
        state = operation.get("state")
        if state is None:
            return "Please specify whether to turn the flashlight 'on' or 'off'."
        return f"Flashlight turned {state}."

class CameraDevice(HardwareDevice):
    """Controls camera functionality."""

    def control(self, operation: Dict[str, Any]) -> str:
        action = operation.get("state", "capture")
        return f"Camera {action}."

class VolumeDevice(HardwareDevice):
    """Controls audio volume."""

    def control(self, operation: Dict[str, Any]) -> str:
        level = operation.get("level", 50)
        return f"Volume set to {level}%."

class BrightnessDevice(HardwareDevice):
    """Controls screen brightness."""

    def control(self, operation: Dict[str, Any]) -> str:
        level = operation.get("level", 50)
        return f"Brightness set to {level}%."

class MemoryDevice(HardwareDevice):
    """Controls memory scanning."""

    def control(self, operation: Dict[str, Any]) -> str:
        return "Memory status: healthy (mock)."

class RemoteComputerDevice(HardwareDevice):
    """Sends instructions to another computer running OMNI-AI remote_agent.py."""

    def control(self, operation: Dict[str, Any]) -> str:
        ip = operation.get("ip")
        instruction = operation.get("instruction")
        if not ip or not instruction:
            return "Missing IP or instruction for remote control."
        
        try:
            url = f"http://{ip}:5050/api/execute"
            if REQUESTS_AVAILABLE and requests:
                response = requests.post(url, json={"instruction": instruction}, timeout=5)
                if response.status_code == 200:
                    return f"Remote PC ({ip}): {response.json().get('message', 'Success')}"
                return f"Remote PC ({ip}) returned error: {response.status_code}"
            else:
                import urllib.request
                import json
                req_data = json.dumps({"instruction": instruction}).encode('utf-8')
                req = urllib.request.Request(url, data=req_data, headers={'Content-Type': 'application/json'})
                with urllib.request.urlopen(req, timeout=5) as resp:
                    res_json = json.loads(resp.read().decode('utf-8'))
                    return f"Remote PC ({ip}): {res_json.get('message', 'Success')}"
        except Exception as e:
            return f"Failed to reach remote PC at {ip}: {str(e)}"

class MicrocontrollerDevice(HardwareDevice):
    """Sends instructions to a microcontroller via USB COM port."""

    def control(self, operation: Dict[str, Any]) -> str:
        port = operation.get("port")
        instruction = operation.get("instruction")
        
        if not port or not instruction:
            return "Missing COM port or instruction for microcontroller."
            
        if not SERIAL_AVAILABLE:
            return "pyserial is not installed. Cannot communicate via USB."

        try:
            # Common default baudrate is 9600 for Arduinos
            baudrate = operation.get("baudrate", 9600)
            with serial.Serial(port, baudrate, timeout=2) as ser:
                # Send the instruction with a newline
                ser.write(f"{instruction}\n".encode('utf-8'))
                # Read response
                response = ser.readline().decode('utf-8').strip()
                if response:
                    return f"Microcontroller ({port}) says: {response}"
                return f"Instruction '{instruction}' sent to microcontroller on {port} (no response)."
        except Exception as e:
            return f"Failed to communicate with microcontroller on {port}: {str(e)}"

class HardwareController:
    """
    Controls hardware devices with permission checks.
    Uses factory pattern for device creation.
    """

    def __init__(self, permissions):
        self.permissions = permissions
        self.devices = self._create_devices()

    def _create_devices(self) -> Dict[str, HardwareDevice]:
        """Factory method to create hardware devices."""
        return {
            "flashlight": FlashlightDevice(),
            "camera": CameraDevice(),
            "volume": VolumeDevice(),
            "brightness": BrightnessDevice(),
            "memory": MemoryDevice(),
            "remote": RemoteComputerDevice(),
            "microcontroller": MicrocontrollerDevice()
        }

    def flashlight(self, state: str) -> str:
        """Control flashlight."""
        if not self.permissions.request("hardware.flashlight"):
            return "Permission denied for flashlight."
        return self.devices["flashlight"].control({"state": state})

    def camera(self, action: str) -> str:
        """Control camera."""
        if not self.permissions.request("hardware.camera"):
            return "Permission denied for camera."
        return self.devices["camera"].control({"state": action})

    def volume(self, level: int) -> str:
        """Control volume."""
        if not self.permissions.request("hardware.volume"):
            return "Permission denied for volume."
        return self.devices["volume"].control({"level": level})

    def brightness(self, level: int) -> str:
        """Control brightness."""
        if not self.permissions.request("hardware.brightness"):
            return "Permission denied for brightness."
        return self.devices["brightness"].control({"level": level})

    def memory_scan(self) -> str:
        """Scan memory."""
        if not self.permissions.request("hardware.memory"):
            return "Permission denied for memory access."
        return self.devices["memory"].control({"scan": True})

    def remote_control(self, ip: str, instruction: str) -> str:
        """Send instruction to a remote PC."""
        if not self.permissions.request("network.remote_control"):
            return "Permission denied for remote network control."
        return self.devices["remote"].control({"ip": ip, "instruction": instruction})

    def microcontroller_control(self, port: str, instruction: str) -> str:
        """Send instruction to a microcontroller."""
        if not self.permissions.request("hardware.usb"):
            return "Permission denied for USB access."
        return self.devices["microcontroller"].control({"port": port, "instruction": instruction})