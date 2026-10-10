# hardware/permissions.py
"""
Permission management system following SOLID principles.
Single responsibility: manage user permissions for hardware access.
"""

from typing import Dict, Set
from abc import ABC, abstractmethod
import logging

logger = logging.getLogger(__name__)

class PermissionStrategy(ABC):
    """Strategy pattern for different permission checking approaches."""

    @abstractmethod
    def check_permission(self, permission_key: str) -> bool:
        """Check if permission is granted."""
        pass

    @abstractmethod
    def grant_permission(self, permission_key: str) -> bool:
        """Grant a permission."""
        pass

class SimplePermissionStrategy(PermissionStrategy):
    """Simple in-memory permission storage."""

    def __init__(self):
        self.permissions: Dict[str, bool] = {
            "hardware.flashlight": False,
            "hardware.camera": False,
            "hardware.volume": False,
            "hardware.brightness": False,
            "hardware.memory": False,
            "app.control": False,
            "app.messaging": False,
            "word.processing": False,
            "security.audit": False,
            "network.remote_control": False,
            "hardware.usb": False
        }

    def check_permission(self, permission_key: str) -> bool:
        return self.permissions.get(permission_key, False)

    def grant_permission(self, permission_key: str) -> bool:
        if permission_key in self.permissions:
            self.permissions[permission_key] = True
            logger.info(f"Granted permission: {permission_key}")
            return True
        return False

class PermissionManager:
    """
    Manages user permissions for hardware and app access.
    Uses strategy pattern for different permission implementations.
    """

    def __init__(self, strategy: PermissionStrategy = None):
        self.strategy = strategy or SimplePermissionStrategy()

    def has(self, key: str) -> bool:
        """Check if permission is granted."""
        return self.strategy.check_permission(key)

    def grant(self, key: str) -> bool:
        """Grant a permission."""
        return self.strategy.grant_permission(key)

    def revoke(self, key: str) -> bool:
        """Revoke a permission."""
        # For simple strategy, just set to False
        if isinstance(self.strategy, SimplePermissionStrategy):
            if key in self.strategy.permissions:
                self.strategy.permissions[key] = False
                logger.info(f"Revoked permission: {key}")
                return True
        return False

    def request(self, key: str) -> bool:
        """Request permission - auto-grant for simulation."""
        if not self.has(key):
            return self.grant(key)
        return True