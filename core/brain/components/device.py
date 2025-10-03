"""
Device detection and management utilities
"""

import os
import platform
import socket
import uuid
from typing import List, Optional

from ..models import DeviceContext, DeviceTier


class DeviceManager:
    """Handles device detection and management"""

    @staticmethod
    def generate_device_id(hostname: Optional[str] = None) -> str:
        """Generate a unique device ID"""
        hostname = hostname or platform.node() or "unknown"
        try:
            # Get MAC address of first network interface
            mac = uuid.getnode()
            mac_hex = ':'.join(['{:02x}'.format((mac >> elements) & 0xff)
                               for elements in range(0, 8*6, 8)][::-1])
            return f"{hostname}_{mac_hex}"
        except:
            # Fallback to hostname + random
            return f"{hostname}_{str(uuid.uuid4())[:8]}"

    @staticmethod
    def detect_hardware_tier() -> DeviceTier:
        """Auto-detect hardware tier based on system capabilities"""
        try:
            # Check CPU count
            cpu_count = len(os.sched_getaffinity(0)) if hasattr(os, 'sched_getaffinity') else os.cpu_count() or 1

            # Check memory
            import psutil
            memory_gb = psutil.virtual_memory().total / (1024**3)

            # Simple heuristics
            if memory_gb >= 32 and cpu_count >= 8:
                return DeviceTier.SERVER
            elif memory_gb >= 16 and cpu_count >= 4:
                return DeviceTier.WORKSTATION
            elif memory_gb >= 8 and cpu_count >= 2:
                return DeviceTier.LAPTOP
            else:
                return DeviceTier.RASPBERRY_PI

        except ImportError:
            # psutil not available, use basic detection
            return DeviceTier.LAPTOP

    @staticmethod
    def detect_capabilities() -> List[str]:
        """Auto-detect device capabilities"""
        capabilities = []

        try:
            import psutil

            # Memory capability
            memory_gb = psutil.virtual_memory().total / (1024**3)
            if memory_gb >= 16:
                capabilities.append('high_memory')
            elif memory_gb >= 8:
                capabilities.append('medium_memory')
            else:
                capabilities.append('low_memory')

            # CPU capability
            cpu_count = psutil.cpu_count(logical=True)
            if cpu_count >= 8:
                capabilities.append('multi_core')
            elif cpu_count >= 4:
                capabilities.append('quad_core')
            else:
                capabilities.append('low_core')

        except ImportError:
            capabilities.extend(['unknown_memory', 'unknown_cpu'])

        # GPU detection (simplified)
        try:
            import torch
            if torch.cuda.is_available():
                capabilities.append('gpu')
                capabilities.append('cuda')
        except ImportError:
            pass

        # Network capability (assume all have basic network)
        capabilities.append('network')

        return capabilities

    @staticmethod
    def get_hostname() -> str:
        """Get system hostname"""
        return platform.node() or "unknown"

    @staticmethod
    def get_ip_address() -> Optional[str]:
        """Get local IP address"""
        try:
            # Get the local IP address
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))  # Connect to Google DNS
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return None

    @classmethod
    def create_device_context(cls, device_id: Optional[str] = None,
                            device_name: Optional[str] = None,
                            location: str = "unknown",
                            hardware_tier: Optional[DeviceTier] = None,
                            capabilities: Optional[List[str]] = None) -> DeviceContext:
        """Create a device context with auto-detection"""
        hostname = device_name or cls.get_hostname()
        device_id = device_id or cls.generate_device_id(hostname)

        return DeviceContext(
            device_id=device_id,
            hardware_tier=hardware_tier or cls.detect_hardware_tier(),
            capabilities=capabilities or cls.detect_capabilities(),
            location=location,
            hostname=hostname,
            ip_address=cls.get_ip_address()
        )