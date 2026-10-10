# =============================================================================
# PROJECT: OmniAI - Intelligent Cross-Platform Assistant
# REFACTORED: Using SOLID principles for maintainability and efficiency
# STRUCTURE: Modular architecture with dependency injection
# SECURITY: Permission-based hardware access with user confirmation
# =============================================================================

"""
LEGACY COMPATIBILITY MODULE
This module now imports from the refactored SOLID architecture.
For new development, use main.py and the modular structure.
"""

# Import refactored components
from core import OmniBrain
from hardware import HardwareController, PermissionManager
from platforms import AppController
from security import SecurityAuditor
from voice import VoiceEngine
from main import ActionExecutor, JarvisCore, create_omnisystem

# Legacy class names for backward compatibility
PermissionManagerLegacy = PermissionManager
HardwareControllerLegacy = HardwareController
AppControllerLegacy = AppController
WordProcessor = lambda permissions: None  # Simplified for legacy
SecurityAuditorLegacy = SecurityAuditor
VoiceEngineLegacy = VoiceEngine
OmniBrainLegacy = OmniBrain
JarvisCoreLegacy = JarvisCore
MoltBot = JarvisCore  # Simplified legacy alias

# Create default instances for legacy compatibility
_permissions = PermissionManager()
_hardware = HardwareController(_permissions)
_apps = AppController(_permissions)
_auditor = SecurityAuditor(_permissions)
_voice = VoiceEngine()

# Create default brain with all components
_brain = OmniBrain()
_brain.permissions = _permissions
_brain.hardware = _hardware
_brain.apps = _apps
_brain.word_processor = WordProcessor(_permissions)
_brain.auditor = _auditor

# Create default Jarvis instance
_jarvis = JarvisCore(_brain, ActionExecutor(_hardware, _apps, _auditor), _voice)

def create_legacy_brain():
    """Create legacy-compatible brain instance."""
    return _brain

def create_legacy_jarvis():
    """Create legacy-compatible Jarvis instance."""
    return _jarvis

# Export legacy interface
__all__ = [
    'OmniBrain', 'PermissionManager', 'HardwareController', 'AppController',
    'WordProcessor', 'SecurityAuditor', 'VoiceEngine', 'JarvisCore', 'MoltBot',
    'create_legacy_brain', 'create_legacy_jarvis'
]       
#self.n_intents = n_intents
