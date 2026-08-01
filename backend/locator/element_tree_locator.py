"""Element tree-based locator for Android/iOS"""

import asyncio
import re
from typing import List, Optional

from backend.locator.base_locator import BaseLocator, Element
from backend.utils.logger import logger


class ElementTreeLocator(BaseLocator):
    \"\"\"Locates elements using UIAutomator2 element tree\"\"\""
    
    def __init__(self, device):
        self.device = device
        self._element_cache = {}
    
    async def locate(
        self,
        selector: str,
        timeout: float = 5.0
    ) -> Optional[Element]:
        \"\"\"Locate a single element using selector\"\"\""
        try:
            # Parse selector format: "resource_id:xxx" or "text:xxx" or "xpath://..."
            elements = await self.locate_all(selector, timeout)
            return elements[0] if elements else None
        except Exception as e:
            logger.error(f"Failed to locate element: {e}")
            return None
    
    async def locate_all(
        self,
        selector: str,
        timeout: float = 5.0
    ) -> List[Element]:
        \"\"\"Locate all matching elements\"\"\""
        try:
            start_time = asyncio.get_event_loop().time()
            
            while (asyncio.get_event_loop().time() - start_time) < timeout:
                elements = await self._parse_selector(selector)
                if elements:
                    return elements
                await asyncio.sleep(0.5)
            
            return []
        except Exception as e:
            logger.error(f"Failed to locate elements: {e}")
            return []
    
    async def locate_by_text(
        self,
        text: str,
        timeout: float = 5.0
    ) -> Optional[Element]:
        \"\"\"Locate element by text content\"\"\""
        return await self.locate(f"text:{text}", timeout)
    
    async def wait_for_element(
        self,
        selector: str,
        timeout: float = 5.0
    ) -> bool:
        \"\"\"Wait for element to appear\"\"\""
        element = await self.locate(selector, timeout)
        return element is not None
    
    async def _parse_selector(self, selector: str) -> List[Element]:
        \"\"\"Parse selector and return matching elements\"\"\"
        if selector.startswith('resource_id:'):
            resource_id = selector.replace('resource_id:', '')
            return await self._locate_by_resource_id(resource_id)
        
        elif selector.startswith('text:'):
            text = selector.replace('text:', '')
            return await self._locate_by_text(text)
        
        elif selector.startswith('xpath:'):
            xpath = selector.replace('xpath:', '')
            return await self._locate_by_xpath(xpath)
        
        elif selector.startswith('desc:'):
            desc = selector.replace('desc:', '')
            return await self._locate_by_desc(desc)
        
        else:
            # Try to detect selector type
            if '//' in selector:
                return await self._locate_by_xpath(selector)
            else:
                return await self._locate_by_text(selector)
    
    async def _locate_by_resource_id(self, resource_id: str) -> List[Element]:
        \"\"\"Locate elements by resource ID\"\"\"
        # This is a placeholder - actual implementation would use UIAutomator2
        logger.debug(f"Locating by resource_id: {resource_id}")
        return []
    
    async def _locate_by_text(self, text: str) -> List[Element]:
        \"\"\"Locate elements by text\"\"\"
        logger.debug(f"Locating by text: {text}")
        return []
    
    async def _locate_by_xpath(self, xpath: str) -> List[Element]:
        \"\"\"Locate elements by XPath\"\"\"
        logger.debug(f"Locating by xpath: {xpath}")
        return []
    
    async def _locate_by_desc(self, desc: str) -> List[Element]:
        \"\"\"Locate elements by content description\"\"\"
        logger.debug(f"Locating by desc: {desc}")
        return []
