"""Base locator interface"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Element:
    """Represents a UI element"""
    element_id: str
    x: int  # Normalized 0-1000
    y: int  # Normalized 0-1000
    width: int  # Normalized 0-1000
    height: int  # Normalized 0-1000
    text: str
    resource_id: Optional[str]
    class_name: str
    package: Optional[str]
    content_desc: Optional[str]
    clickable: bool
    enabled: bool
    visible: bool
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            'element_id': self.element_id,
            'x': self.x,
            'y': self.y,
            'width': self.width,
            'height': self.height,
            'text': self.text,
            'resource_id': self.resource_id,
            'class_name': self.class_name,
            'package': self.package,
            'content_desc': self.content_desc,
            'clickable': self.clickable,
            'enabled': self.enabled,
            'visible': self.visible
        }


class BaseLocator(ABC):
    """Abstract base class for element locators"""
    
    @abstractmethod
    async def locate(
        self,
        selector: str,
        timeout: float = 5.0
    ) -> Optional[Element]:
        """Locate a single element"""
        pass
    
    @abstractmethod
    async def locate_all(
        self,
        selector: str,
        timeout: float = 5.0
    ) -> List[Element]:
        """Locate all matching elements"""
        pass
    
    @abstractmethod
    async def locate_by_text(
        self,
        text: str,
        timeout: float = 5.0
    ) -> Optional[Element]:
        """Locate element by text content"""
        pass
    
    @abstractmethod
    async def wait_for_element(
        self,
        selector: str,
        timeout: float = 5.0
    ) -> bool:
        """Wait for element to appear"""
        pass
