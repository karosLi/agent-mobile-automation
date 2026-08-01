"""Performance monitoring for devices and operations"""

import asyncio
import time
from dataclasses import dataclass
from typing import Optional, Dict
from datetime import datetime

from backend.utils.logger import logger


@dataclass
class PerformanceMetrics:
    \"\"\"Performance metrics\"\"\"
    timestamp: datetime
    fps: Optional[float]  # Frames per second
    memory_mb: Optional[float]  # Memory usage in MB
    cpu_percent: Optional[float]  # CPU usage percentage
    operation_time_ms: Optional[float]  # Operation duration
    details: Dict = None


class PerformanceMonitor:
    \"\"\"Monitors device and operation performance\"\"\"
    
    def __init__(self, device):
        self.device = device
        self._metrics_history = []
        self._is_monitoring = False
    
    async def start_monitoring(self):
        \"\"\"Start performance monitoring\"\"\"
        self._is_monitoring = True
        logger.info("Performance monitoring started")
    
    async def stop_monitoring(self):
        \"\"\"Stop performance monitoring\"\"\"
        self._is_monitoring = False
        logger.info("Performance monitoring stopped")
    
    async def get_current_metrics(self) -> PerformanceMetrics:
        \"\"\"Get current performance metrics\"\"\"
        try:
            memory_info = await self.device.get_memory_info()
            cpu_info = await self.device.get_cpu_info()
            
            metrics = PerformanceMetrics(
                timestamp=datetime.now(),
                fps=None,  # Would be extracted from device
                memory_mb=self._parse_memory(memory_info),
                cpu_percent=self._parse_cpu(cpu_info),
                operation_time_ms=None,
                details={
                    'memory_raw': str(memory_info),
                    'cpu_raw': str(cpu_info)
                }
            )
            
            self._metrics_history.append(metrics)
            return metrics
        
        except Exception as e:
            logger.error(f"Failed to get metrics: {e}")
            return PerformanceMetrics(
                timestamp=datetime.now(),
                fps=None,
                memory_mb=None,
                cpu_percent=None,
                operation_time_ms=None,
                details={'error': str(e)}
            )
    
    async def measure_operation(self, operation_name: str):
        \"\"\"Context manager to measure operation time\"\"\"
        return _OperationTimer(self, operation_name)
    
    def _parse_memory(self, memory_info: dict) -> Optional[float]:
        \"\"\"Parse memory info\"\"\"
        try:
            raw = memory_info.get('raw', '')
            # Simple parsing - would be more sophisticated in production
            return None
        except Exception as e:
            logger.error(f"Failed to parse memory info: {e}")
            return None
    
    def _parse_cpu(self, cpu_info: dict) -> Optional[float]:
        \"\"\"Parse CPU info\"\"\"
        try:
            raw = cpu_info.get('raw', '')
            # Simple parsing - would be more sophisticated in production
            return None
        except Exception as e:
            logger.error(f"Failed to parse CPU info: {e}")
            return None
    
    def get_metrics_summary(self) -> dict:
        \"\"\"Get summary of metrics\"\"\"
        if not self._metrics_history:
            return {}
        
        metrics_with_values = [m for m in self._metrics_history if m.memory_mb is not None]
        
        if not metrics_with_values:
            return {}
        
        return {
            'total_samples': len(self._metrics_history),
            'average_memory_mb': sum(m.memory_mb for m in metrics_with_values) / len(metrics_with_values) if metrics_with_values else None,
            'peak_memory_mb': max((m.memory_mb for m in metrics_with_values), default=None)
        }


class _OperationTimer:
    \"\"\"Context manager for measuring operation time\"\"\"
    
    def __init__(self, monitor: PerformanceMonitor, operation_name: str):
        self.monitor = monitor
        self.operation_name = operation_name
        self.start_time = None
    
    async def __aenter__(self):
        self.start_time = time.time()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.start_time:
            duration_ms = (time.time() - self.start_time) * 1000
            logger.debug(f"Operation '{self.operation_name}' took {duration_ms:.2f}ms")
