"""Execute UI actions on devices"""

from dataclasses import dataclass
from typing import Optional
from datetime import datetime

from backend.device.base_device import BaseDevice
from backend.utils.logger import logger


@dataclass
class Action:
    """Represents a UI action"""
    action_type: str  # 'click', 'input', 'swipe', etc.
    target: str  # Element selector or coordinates
    params: dict  # Action parameters


@dataclass
class ActionResult:
    """Result of executing an action"""
    success: bool
    action_type: str
    timestamp: datetime
    duration_ms: float
    error: Optional[str] = None
    screenshot_path: Optional[str] = None
    details: Optional[dict] = None


class ActionExecutor:
    \"\"\"Executes actions on devices\"\"\""
    
    def __init__(self, device: BaseDevice):
        self.device = device
    
    async def execute(
        self,
        action: Action,
        wait_for_stable: bool = True
    ) -> ActionResult:
        \"\"\"Execute an action\"\"\"
        import time as time_module
        start_time = time_module.time()
        
        try:
            if action.action_type == 'click':
                success = await self._execute_click(action)
            
            elif action.action_type == 'input':
                success = await self._execute_input(action)
            
            elif action.action_type == 'swipe':
                success = await self._execute_swipe(action)
            
            elif action.action_type == 'long_press':
                success = await self._execute_long_press(action)
            
            else:
                success = False
                raise ValueError(f"Unknown action type: {action.action_type}")
            
            duration_ms = (time_module.time() - start_time) * 1000
            
            if wait_for_stable:
                await self._wait_for_stable()
            
            return ActionResult(
                success=success,
                action_type=action.action_type,
                timestamp=datetime.now(),
                duration_ms=duration_ms
            )
        
        except Exception as e:
            duration_ms = (time_module.time() - start_time) * 1000
            logger.error(f"Action execution failed: {e}")
            return ActionResult(
                success=False,
                action_type=action.action_type,
                timestamp=datetime.now(),
                duration_ms=duration_ms,
                error=str(e)
            )
    
    async def _execute_click(self, action: Action) -> bool:
        \"\"\"Execute click action\"\"\"
        params = action.params
        x = int(params.get('x', 0))
        y = int(params.get('y', 0))
        
        logger.debug(f"Executing click at ({x}, {y})")
        return await self.device.click(x, y)
    
    async def _execute_input(self, action: Action) -> bool:
        \"\"\"Execute input text action\"\"\"
        params = action.params
        text = params.get('text', '')
        
        logger.debug(f"Executing input: {text}")
        return await self.device.input_text(text)
    
    async def _execute_swipe(self, action: Action) -> bool:
        \"\"\"Execute swipe action\"\"\"
        params = action.params
        x1 = int(params.get('x1', 0))
        y1 = int(params.get('y1', 0))
        x2 = int(params.get('x2', 0))
        y2 = int(params.get('y2', 0))
        duration = int(params.get('duration', 500))
        
        logger.debug(f"Executing swipe from ({x1},{y1}) to ({x2},{y2})")
        return await self.device.swipe(x1, y1, x2, y2, duration)
    
    async def _execute_long_press(self, action: Action) -> bool:
        \"\"\"Execute long press action\"\"\"
        params = action.params
        x = int(params.get('x', 0))
        y = int(params.get('y', 0))
        duration = int(params.get('duration', 500))
        
        logger.debug(f"Executing long press at ({x}, {y}) for {duration}ms")
        return await self.device.long_press(x, y, duration)
    
    async def _wait_for_stable(self, timeout: float = 2.0):
        \"\"\"Wait for screen to stabilize\"\"\"
        import asyncio
        await asyncio.sleep(0.5)  # Simple wait, can be enhanced
