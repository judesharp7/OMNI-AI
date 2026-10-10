# integration/omniai_integration.py
"""
Main OMNI-AI integration module combining all advanced features.
Integrates TensorFlow, Cryptography, Speech Recognition, pyttsx3, psutil, and WMI.
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

from core.ai_models import HybridAIModel, TENSORFLOW_AVAILABLE, PYTORCH_AVAILABLE
from core.memory import ContextManager
from core.personality import ResponseGenerator
from security.encryption import EncryptionManager, PasswordHasher, SecureSessionManager
from security.auditor import SecurityAuditor
from hardware.system_monitor import ComprehensiveMonitor, PSUTIL_AVAILABLE, WMI_AVAILABLE
from voice.advanced_voice import VoiceInteractionEngine, PYTTSX3_AVAILABLE, SPEECH_RECOGNITION_AVAILABLE
from hardware.permissions import PermissionManager
from platforms.controller import AppController

logger = logging.getLogger(__name__)


class OmniAIIntegration:
    """
    Comprehensive OMNI-AI system integrating all advanced technologies.
    Combines AI, security, voice, system monitoring, and encryption.
    """

    def __init__(self):
        """Initialize OMNI-AI integration."""
        logger.info("=" * 80)
        logger.info("INITIALIZING OMNI-AI ADVANCED SYSTEM")
        logger.info("=" * 80)
        
        # AI Models
        self.ai_model = HybridAIModel()
        logger.info(f"✓ AI Models: {self.ai_model.get_model_info()}")
        
        # Memory and Personality
        self.memory = ContextManager()
        self.personality = ResponseGenerator()
        
        # Security and Encryption
        self.encryption_manager = EncryptionManager()
        self.password_hasher = PasswordHasher()
        self.session_manager = SecureSessionManager(self.encryption_manager)
        self.security_auditor = SecurityAuditor(PermissionManager())
        logger.info(f"✓ Encryption: Available" if self.encryption_manager.cipher else "✗ Encryption: Not available")
        
        # System Monitoring
        self.system_monitor = ComprehensiveMonitor()
        logger.info(f"✓ psutil: {PSUTIL_AVAILABLE}")
        logger.info(f"✓ WMI (Windows): {WMI_AVAILABLE}")
        
        # Voice
        self.voice_engine = VoiceInteractionEngine()
        logger.info(f"✓ pyttsx3: {PYTTSX3_AVAILABLE}")
        logger.info(f"✓ Speech Recognition: {SPEECH_RECOGNITION_AVAILABLE}")
        
        # System info
        self.creation_time = datetime.now()
        logger.info("=" * 80)
        logger.info("OMNI-AI INITIALIZATION COMPLETE")
        logger.info("=" * 80)

    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status."""
        return {
            'timestamp': datetime.now().isoformat(),
            'ai_systems': {
                'tensorflow': TENSORFLOW_AVAILABLE,
                'pytorch': PYTORCH_AVAILABLE,
                'hybrid_model': self.ai_model.get_model_info()
            },
            'security': {
                'encryption_available': bool(self.encryption_manager.cipher),
                'password_hashing': True,
                'session_management': True
            },
            'monitoring': {
                'psutil': PSUTIL_AVAILABLE,
                'wmi_windows': WMI_AVAILABLE
            },
            'voice': {
                'pyttsx3': PYTTSX3_AVAILABLE,
                'speech_recognition': SPEECH_RECOGNITION_AVAILABLE
            }
        }

    def get_full_system_report(self) -> Dict[str, Any]:
        """Get comprehensive system report."""
        report = {
            'system_status': self.get_system_status(),
            'system_metrics': self.system_monitor.get_full_system_report(),
            'ai_capabilities': self.ai_model.get_model_info(),
            'security_status': self.security_auditor.run_audit(),
            'timestamp': datetime.now().isoformat()
        }
        return report

    def secure_data(self, data: str, key: Optional[bytes] = None) -> Dict[str, Any]:
        """Encrypt sensitive data."""
        if key:
            self.encryption_manager.key = key
            self.encryption_manager.cipher = self.encryption_manager.cipher.__class__(key)
        
        encrypted = self.encryption_manager.encrypt_data(data)
        return {
            'data': data,
            'encrypted': encrypted.decode() if encrypted else None,
            'key': self.encryption_manager.key.decode() if self.encryption_manager.key else None
        }

    def unsecure_data(self, encrypted_data: str, key: Optional[bytes] = None) -> Optional[str]:
        """Decrypt sensitive data."""
        if key:
            self.encryption_manager = EncryptionManager(key)
        
        return self.encryption_manager.decrypt_data(encrypted_data.encode() if isinstance(encrypted_data, str) else encrypted_data)

    def hash_password(self, password: str) -> Dict[str, str]:
        """Hash a password securely."""
        hash_value, salt = self.password_hasher.hash_password(password)
        return {
            'password': password,
            'hash': hash_value,
            'salt': salt
        }

    def verify_password(self, password: str, hash_value: str, salt: str) -> bool:
        """Verify password against stored hash."""
        return self.password_hasher.verify_password(password, hash_value, salt)

    def start_voice_interaction(self, greeting: str = "Hello! I'm OMNI-AI, your intelligent assistant."):
        """Start voice interaction."""
        self.voice_engine.start_conversation(greeting)

    def stop_voice_interaction(self, farewell: str = "Thank you for using OMNI-AI. Goodbye!"):
        """Stop voice interaction."""
        self.voice_engine.stop_conversation(farewell)

    def ask_question(self, question: str) -> Optional[str]:
        """Ask a question and get voice response."""
        return self.voice_engine.ask_question(question)

    def process_voice_command(self, command: str) -> Dict[str, Any]:
        """Process voice command through AI."""
        # This would integrate with the AI model to process commands
        return {
            'command': command,
            'status': 'processed',
            'timestamp': datetime.now().isoformat()
        }

    def monitor_system(self) -> Dict[str, Any]:
        """Get system monitoring report."""
        return self.system_monitor.get_full_system_report()

    def get_system_health(self) -> Dict[str, Any]:
        """Get system health status."""
        metrics = self.system_monitor.psutil_monitor.get_system_health()
        
        health_report = {
            'overall_status': metrics.get('status'),
            'cpu_usage': metrics.get('cpu_usage'),
            'memory_usage': metrics.get('memory_usage'),
            'issues': metrics.get('issues'),
            'top_processes': self.system_monitor.psutil_monitor.get_process_info()[:5],
            'timestamp': datetime.now().isoformat()
        }
        
        return health_report

    def run_security_audit(self) -> Dict[str, Any]:
        """Run comprehensive security audit."""
        audit_result = self.security_auditor.run_audit()
        
        return {
            'audit_result': audit_result,
            'encryption_status': 'enabled' if self.encryption_manager.cipher else 'disabled',
            'timestamp': datetime.now().isoformat()
        }

    def create_secure_session(self, session_id: str, data: Dict[str, Any], ttl_minutes: int = 60) -> bool:
        """Create a secure encrypted session."""
        return self.session_manager.create_session(session_id, data, ttl_minutes)

    def get_session_data(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve session data."""
        return self.session_manager.get_session(session_id)

    def delete_session(self, session_id: str) -> bool:
        """Delete session."""
        return self.session_manager.delete_session(session_id)

    def get_all_capabilities(self) -> Dict[str, Any]:
        """Get all system capabilities."""
        return {
            'ai_models': {
                'tensorflow': TENSORFLOW_AVAILABLE,
                'pytorch': PYTORCH_AVAILABLE,
                'intent_classification': bool(self.ai_model.tf_intent_model),
                'entity_extraction': bool(self.ai_model.tf_entity_model)
            },
            'encryption': {
                'fernet': bool(self.encryption_manager.cipher),
                'pbkdf2_hashing': True
            },
            'voice': {
                'text_to_speech': PYTTSX3_AVAILABLE,
                'speech_to_text': SPEECH_RECOGNITION_AVAILABLE,
                'voice_customization': PYTTSX3_AVAILABLE
            },
            'system_monitoring': {
                'psutil': PSUTIL_AVAILABLE,
                'wmi_windows': WMI_AVAILABLE,
                'cpu_monitoring': PSUTIL_AVAILABLE,
                'memory_monitoring': PSUTIL_AVAILABLE,
                'disk_monitoring': PSUTIL_AVAILABLE,
                'network_monitoring': PSUTIL_AVAILABLE,
                'process_monitoring': PSUTIL_AVAILABLE
            },
            'security': {
                'security_auditing': True,
                'ransomware_detection': True,
                'remote_access_detection': True,
                'process_monitoring': PSUTIL_AVAILABLE
            },
            'timestamp': datetime.now().isoformat()
        }


def initialize_omniai() -> OmniAIIntegration:
    """Initialize and return OMNI-AI integration system."""
    return OmniAIIntegration()


# Export
__all__ = [
    'OmniAIIntegration',
    'initialize_omniai'
]
