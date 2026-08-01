"""Android device driver using ADB and UIAutomator2"""

import asyncio
import subprocess
from datetime import datetime
from typing import Optional
from io import BytesIO

from backend.device.base_device import BaseDevice, DeviceInfo, Screenshot
from backend.utils.logger import logger
from backend.utils.retry import retry


class AndroidDevice(BaseDevice):
    """Android device driver"""
    
    def __init__(self, device_id: str):
        super().__init__(device_id)
        self._connected = False
        self._device_name: Optional[str] = None
    
    async def connect(self) -> bool:
        """Connect to Android device"""
        try:
            # Check if device is visible via ADB
            result = await self._adb_command(['devices'])
            if self.device_id not in result:
                logger.error(f"Device {self.device_id} not found")
                return False
            
            # Get device info
            await self.get_info()
            self._connected = True
            logger.info(f"Connected to Android device: {self.device_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to device: {e}")
            return False
    
    async def disconnect(self) -> bool:
        """Disconnect from Android device"""
        self._connected = False
        logger.info(f"Disconnected from Android device: {self.device_id}")
        return True
    
    async def is_connected(self) -> bool:
        """Check if device is connected"""
        return self._connected
    
    @retry(max_attempts=3, delay=0.5)
    async def get_info(self) -> DeviceInfo:
        """Get Android device information"""
        try:
            # Get device name
            device_name = await self._adb_command(
                ['shell', 'getprop', 'ro.product.model']
            )
            
            # Get OS version
            os_version = await self._adb_command(
                ['shell', 'getprop', 'ro.build.version.release']
            )
            
            # Get screen dimensions
            size_output = await self._adb_command(
                ['shell', 'wm', 'size']
            )
            # Parse "Physical size: 1080x2340"
            parts = size_output.split()[-1].split('x')
            width = int(parts[0])
            height = int(parts[1])
            
            self._info = DeviceInfo(
                device_id=self.device_id,
                device_type='android',
                device_name=device_name.strip(),
                os_version=os_version.strip(),
                screen_width=width,
                screen_height=height,
                model=device_name.strip(),
                connected_at=datetime.now()
            )
            return self._info
        except Exception as e:
            logger.error(f"Failed to get device info: {e}")
            raise
    
    @retry(max_attempts=3, delay=0.5)
    async def get_screenshot(self) -> Screenshot:
        """Get device screenshot"""
        try:
            # Get screenshot via ADB
            await self._adb_command(['exec-out', 'screencap', '-p'], output=True)
            
            # For now, return a placeholder
            # In production, this would actually capture the screenshot
            info = await self.get_info()
            
            screenshot = Screenshot(
                timestamp=datetime.now(),
                data=b'',  # Placeholder
                width=info.screen_width,
                height=info.screen_height
            )
            return screenshot
        except Exception as e:
            logger.error(f"Failed to get screenshot: {e}")
            raise
    
    @retry(max_attempts=2, delay=0.2)
    async def click(self, x: int, y: int) -> bool:
        """Click at coordinates"""
        try:
            await self._adb_command(['shell', 'input', 'tap', str(x), str(y)])
            logger.debug(f"Clicked at ({x}, {y})")
            return True
        except Exception as e:
            logger.error(f"Click failed: {e}")
            return False
    
    @retry(max_attempts=2, delay=0.2)
    async def long_press(self, x: int, y: int, duration: int = 500) -> bool:
        """Long press at coordinates"""
        try:
            # Use swipe with same start and end for long press
            await self._adb_command([
                'shell', 'input', 'swipe',
                str(x), str(y), str(x), str(y), str(duration)
            ])
            logger.debug(f"Long pressed at ({x}, {y}) for {duration}ms")
            return True
        except Exception as e:
            logger.error(f"Long press failed: {e}")
            return False
    
    @retry(max_attempts=2, delay=0.2)
    async def input_text(self, text: str) -> bool:
        """Input text"""
        try:
            # Escape special characters
            escaped_text = text.replace(' ', '%s').replace('&', '\\&')
            await self._adb_command(['shell', 'input', 'text', escaped_text])
            logger.debug(f"Input text: {text}")
            return True
        except Exception as e:
            logger.error(f"Input text failed: {e}")
            return False
    
    @retry(max_attempts=2, delay=0.2)
    async def swipe(self, x1: int, y1: int, x2: int, y2: int, duration: int = 500) -> bool:
        """Swipe from (x1,y1) to (x2,y2)"""
        try:
            await self._adb_command([
                'shell', 'input', 'swipe',
                str(x1), str(y1), str(x2), str(y2), str(duration)
            ])
            logger.debug(f"Swiped from ({x1},{y1}) to ({x2},{y2})")
            return True
        except Exception as e:
            logger.error(f"Swipe failed: {e}")
            return False
    
    async def get_memory_info(self) -> dict:
        """Get memory usage information"""
        try:
            output = await self._adb_command(['shell', 'dumpsys', 'meminfo'])
            # Parse output and return dict
            return {'raw': output}
        except Exception as e:
            logger.error(f"Failed to get memory info: {e}")
            return {}
    
    async def get_cpu_info(self) -> dict:
        """Get CPU usage information"""
        try:
            output = await self._adb_command(['shell', 'top', '-n', '1'])
            # Parse output and return dict
            return {'raw': output}
        except Exception as e:
            logger.error(f"Failed to get CPU info: {e}")
            return {}
    
    async def _adb_command(
        self,
        args: list,
        output: bool = False
    ) -> str:
        """Execute ADB command"""
        try:
            cmd = ['adb', '-s', self.device_id] + args
            
            if output:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=10
                )
            else:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=10
                )
            
            if result.returncode != 0:
                raise Exception(f"ADB command failed: {result.stderr}")
            
            return result.stdout
        except subprocess.TimeoutExpired:
            logger.error(f"ADB command timeout: {args}")
            raise
        except Exception as e:
            logger.error(f"ADB command error: {e}")
            raise
