"""Retry mechanism with exponential backoff"""

import asyncio
import time
from functools import wraps
from typing import Callable, Type, Tuple, Any

from backend.utils.logger import logger


def retry(
    max_attempts: int = 3,
    backoff_factor: float = 2.0,
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
    delay: float = 1.0
):
    """
    Retry decorator with exponential backoff
    
    Args:
        max_attempts: Maximum number of attempts
        backoff_factor: Backoff multiplier (exponential)
        exceptions: Tuple of exceptions to catch
        delay: Initial delay between retries in seconds
    """
    def decorator(func: Callable) -> Callable:
        if asyncio.iscoroutinefunction(func):
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                current_delay = delay
                for attempt in range(1, max_attempts + 1):
                    try:
                        return await func(*args, **kwargs)
                    except exceptions as e:
                        if attempt == max_attempts:
                            logger.error(
                                f"Max retries reached for {func.__name__}: {e}"
                            )
                            raise
                        logger.warning(
                            f"Attempt {attempt}/{max_attempts} failed for "
                            f"{func.__name__}, retrying in {current_delay}s: {e}"
                        )
                        await asyncio.sleep(current_delay)
                        current_delay *= backoff_factor
            return async_wrapper
        else:
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                current_delay = delay
                for attempt in range(1, max_attempts + 1):
                    try:
                        return func(*args, **kwargs)
                    except exceptions as e:
                        if attempt == max_attempts:
                            logger.error(
                                f"Max retries reached for {func.__name__}: {e}"
                            )
                            raise
                        logger.warning(
                            f"Attempt {attempt}/{max_attempts} failed for "
                            f"{func.__name__}, retrying in {current_delay}s: {e}"
                        )
                        time.sleep(current_delay)
                        current_delay *= backoff_factor
            return sync_wrapper
    return decorator
