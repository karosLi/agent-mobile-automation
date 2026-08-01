"""Base device driver interface"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, List, Tuple
from datetime import datetime


@dataclass
class DeviceInfo:
    """Device information"""
    device_id: str
    device_type: str  # 'android' or 'ios'
    device_name: str
    os_version: str
    screen_width: int
    screen_height: int
    model: str
    connected_at: datetime


@dataclass
class Screenshot:
    """Screenshot data"""
    timestamp: datetime
    data: bytes  # PNG data
    width: int
    height: int


class BaseDevice(ABC):
    """Abstract base class for device drivers"""
    
    def __init__(self, device_id: str):
        self.device_id = device_id
        self._info: Optional[DeviceInfo] = None
    
    @abstractmethod
    async def connect(self) -> bool:
        """Connect to device"""
        pass
    
    @abstractmethod
    async def disconnect(self) -> bool:
        """Disconnect from device"""
        pass
    
    @abstractmethod
    async def is_connected(self) -> bool:
        """Check if device is connected"""
        pass
    
    @abstractmethod
    async def get_info(self) -> DeviceInfo:
        """Get device information"""
        pass
    
    @abstractmethod
    async def get_screenshot(self) -> Screenshot:
        """Get current screen screenshot"""
        pass
    
    @abstractmethod
    async def click(self, x: int, y: int) -> bool:
        """Click at coordinates"""
        pass
    
    @abstractmethod
    async def long_press(self, x: int, y: int, duration: int = 500) -> bool:
        """Long press at coordinates"""
        pass
    
    @abstractmethod
    async def input_text(self, text: str) -> bool:
        """Input text"""
        pass
    
    @abstractmethod
    async def swipe(self, x1: int, y1: int, x2: int, y2: int, duration: int = 500) -> bool:
        """Swipe from (x1,y1) to (x2,y2)"""
        pass
    
    @abstractmethod
    async def get_memory_info(self) -> dict:
        """Get memory usage information"""
        pass
    
    @abstractmethod
    async def get_cpu_info(self) -> dict:
        """Get CPU usage information"""
        pass
    
    @property
    def info(self) -> Optional[DeviceInfo]:
        """Get cached device info"""
        return self._info
