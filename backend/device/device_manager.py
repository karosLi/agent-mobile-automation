"""Device manager for handling multiple devices"""

import asyncio
from typing import Dict, List, Optional
from datetime import datetime

from backend.device.base_device import BaseDevice, DeviceInfo
from backend.device.android_device import AndroidDevice
from backend.utils.logger import logger


class DeviceManager:
    """Manages multiple device connections and operations"""
    
    def __init__(self, max_concurrent: int = 10):
        self.devices: Dict[str, BaseDevice] = {}
        self.max_concurrent = max_concurrent
        self._semaphore = asyncio.Semaphore(max_concurrent)
        self._lock = asyncio.Lock()
    
    async def register_device(self, device_id: str, device_type: str = 'android') -> bool:
        """Register and connect to a device"""
        async with self._lock:
            if device_id in self.devices:
                logger.warning(f"Device {device_id} already registered")
                return True
            
            try:
                # Create device instance based on type
                if device_type.lower() == 'android':
                    device = AndroidDevice(device_id)
                else:
                    logger.error(f"Unsupported device type: {device_type}")
                    return False
                
                # Connect to device
                if await device.connect():
                    self.devices[device_id] = device
                    logger.info(f"Device registered: {device_id}")
                    return True
                else:
                    logger.error(f"Failed to connect to device: {device_id}")
                    return False
            except Exception as e:
                logger.error(f"Failed to register device: {e}")
                return False
    
    async def unregister_device(self, device_id: str) -> bool:
        """Unregister and disconnect from a device"""
        async with self._lock:
            if device_id not in self.devices:
                logger.warning(f"Device {device_id} not found")
                return False
            
            try:
                device = self.devices[device_id]
                await device.disconnect()
                del self.devices[device_id]
                logger.info(f"Device unregistered: {device_id}")
                return True
            except Exception as e:
                logger.error(f"Failed to unregister device: {e}")
                return False
    
    async def get_device(self, device_id: str) -> Optional[BaseDevice]:
        """Get device instance"""
        return self.devices.get(device_id)
    
    async def list_devices(self) -> List[DeviceInfo]:
        """List all connected devices"""
        devices_info = []
        for device in self.devices.values():
            try:
                if await device.is_connected():
                    info = await device.get_info()
                    devices_info.append(info)
            except Exception as e:
                logger.error(f"Failed to get device info: {e}")
        return devices_info
    
    async def execute_on_device(
        self,
        device_id: str,
        action: str,
        **kwargs
    ) -> dict:
        """Execute an action on a specific device with concurrency control"""
        async with self._semaphore:
            device = await self.get_device(device_id)
            if not device:
                return {'success': False, 'error': 'Device not found'}
            
            try:
                if action == 'click':
                    result = await device.click(kwargs['x'], kwargs['y'])
                    return {'success': result, 'action': action}
                
                elif action == 'input_text':
                    result = await device.input_text(kwargs['text'])
                    return {'success': result, 'action': action}
                
                elif action == 'long_press':
                    result = await device.long_press(
                        kwargs['x'],
                        kwargs['y'],
                        kwargs.get('duration', 500)
                    )
                    return {'success': result, 'action': action}
                
                elif action == 'swipe':
                    result = await device.swipe(
                        kwargs['x1'],
                        kwargs['y1'],
                        kwargs['x2'],
                        kwargs['y2'],
                        kwargs.get('duration', 500)
                    )
                    return {'success': result, 'action': action}
                
                elif action == 'screenshot':
                    screenshot = await device.get_screenshot()
                    return {
                        'success': True,
                        'action': action,
                        'timestamp': screenshot.timestamp.isoformat(),
                        'width': screenshot.width,
                        'height': screenshot.height
                    }
                
                else:
                    return {'success': False, 'error': f'Unknown action: {action}'}
            
            except Exception as e:
                logger.error(f"Failed to execute action: {e}")
                return {'success': False, 'error': str(e)}
    
    async def batch_execute(
        self,
        actions: List[dict]
    ) -> List[dict]:
        """Execute multiple actions concurrently"""
        tasks = []
        for action in actions:
            device_id = action.pop('device_id')
            action_type = action.pop('action')
            tasks.append(
                self.execute_on_device(device_id, action_type, **action)
            )
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return [
            {'success': False, 'error': str(r)} if isinstance(r, Exception) else r
            for r in results
        ]
