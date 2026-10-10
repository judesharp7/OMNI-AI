# platforms/controller.py
"""
Platform and app control system following SOLID principles.
Single responsibility: control applications and messaging platforms.
"""

from typing import Dict, Any
from abc import ABC, abstractmethod
import logging

logger = logging.getLogger(__name__)

class MessagingPlatform(ABC):
    """Abstract base class for messaging platforms."""

    @abstractmethod
    def send_message(self, contact: str, message: str) -> str:
        """Send message to contact."""
        pass

class WhatsAppPlatform(MessagingPlatform):
    """WhatsApp messaging platform."""

    def send_message(self, contact: str, message: str) -> str:
        return f"Sent message to {contact} on WhatsApp: '{message}' (mock)."

class FacebookPlatform(MessagingPlatform):
    """Facebook Messenger platform."""

    def send_message(self, contact: str, message: str) -> str:
        return f"Sent message to {contact} on Facebook: '{message}' (mock)."

class AppLauncher(ABC):
    """Abstract base class for app launching."""

    @abstractmethod
    def launch(self, app_name: str) -> str:
        """Launch an application."""
        pass

    @abstractmethod
    def close(self, app_name: str) -> str:
        """Close an application."""
        pass

class WindowsAppLauncher(AppLauncher):
    """Windows application launcher."""

    def launch(self, app_name: str) -> str:
        return f"App {app_name} opened (mock)."

    def close(self, app_name: str) -> str:
        return f"App {app_name} closed (mock)."

class AppController:
    """
    Controls applications and messaging platforms.
    Uses strategy pattern for different platforms.
    """

    def __init__(self, permissions):
        self.permissions = permissions
        self.messaging_platforms = self._create_messaging_platforms()
        self.app_launcher = WindowsAppLauncher()

    def _create_messaging_platforms(self) -> Dict[str, MessagingPlatform]:
        """Factory method for messaging platforms."""
        return {
            "whatsapp": WhatsAppPlatform(),
            "facebook": FacebookPlatform()
        }

    def open_app(self, app_name: str) -> str:
        """Open an application."""
        if not self.permissions.request("app.control"):
            return "Permission denied for app control."
        return self.app_launcher.launch(app_name)

    def close_app(self, app_name: str) -> str:
        """Close an application."""
        if not self.permissions.request("app.control"):
            return "Permission denied for app control."
        return self.app_launcher.close(app_name)

    def send_message(self, platform: str, contact: str, message: str) -> str:
        """Send message via specified platform."""
        if not self.permissions.request("app.messaging"):
            return "Permission denied for messaging apps."

        platform_lower = platform.lower()
        if platform_lower in self.messaging_platforms:
            return self.messaging_platforms[platform_lower].send_message(contact, message)
        else:
            # Default to WhatsApp
            return self.messaging_platforms["whatsapp"].send_message(contact, message)