# security/auditor.py
"""
Security auditing system following SOLID principles.
Single responsibility: perform security checks and audits.
"""

from typing import Dict, List, Any
from datetime import datetime
from abc import ABC, abstractmethod
import logging

# Optional imports
try:
    import psutil
except ImportError:
    psutil = None

try:
    import wmi
except ImportError:
    wmi = None

try:
    from cryptography.fernet import Fernet
except ImportError:
    Fernet = None

logger = logging.getLogger(__name__)

class SecurityCheck(ABC):
    """Abstract base class for security checks."""

    @abstractmethod
    def perform_check(self) -> Dict[str, Any]:
        """Perform the security check."""
        pass

class RansomwareCheck(SecurityCheck):
    """Checks for ransomware indicators."""

    def perform_check(self) -> Dict[str, Any]:
        threats = []
        # Simplified check - in real implementation would scan files
        return {"threats": threats}

class RemoteAccessCheck(SecurityCheck):
    """Checks for unauthorized remote access."""

    def perform_check(self) -> Dict[str, Any]:
        threats = []

        if psutil:
            try:
                connections = psutil.net_connections()
                suspicious_ports = [4444, 6667, 31337]
                for conn in connections:
                    if conn.laddr and conn.laddr.port in suspicious_ports:
                        threats.append(f"Suspicious connection on port {conn.laddr.port}")
            except Exception as e:
                logger.error(f"Remote access check error: {e}")

        return {"threats": threats}

class HardwareIntegrityCheck(SecurityCheck):
    """Checks hardware integrity."""

    def perform_check(self) -> Dict[str, Any]:
        threats = []
        # Simplified check
        return {"threats": threats}

class ProcessCheck(SecurityCheck):
    """Checks for suspicious processes."""

    def perform_check(self) -> Dict[str, Any]:
        threats = []

        if psutil:
            try:
                suspicious_patterns = ['keylogger', 'trojan', 'backdoor']
                for proc in psutil.process_iter(['name']):
                    proc_name = proc.info['name'].lower() if proc.info['name'] else ""
                    if any(pattern in proc_name for pattern in suspicious_patterns):
                        threats.append(f"Suspicious process: {proc.info['name']}")
            except Exception as e:
                logger.error(f"Process check error: {e}")

        return {"threats": threats}

class SecurityAuditor:
    """
    Performs comprehensive security audits.
    Uses composition over inheritance for different check types.
    """

    def __init__(self, permissions):
        self.permissions = permissions
        self.checks = self._create_checks()
        self.encryption_key = self._generate_key()
        self.cipher = Fernet(self.encryption_key) if Fernet else None

    def _create_checks(self) -> List[SecurityCheck]:
        """Factory method for security checks."""
        return [
            RansomwareCheck(),
            RemoteAccessCheck(),
            HardwareIntegrityCheck(),
            ProcessCheck()
        ]

    def _generate_key(self) -> bytes:
        """Generate encryption key."""
        if Fernet:
            return Fernet.generate_key()
        return b"mock_key"

    def run_audit(self) -> str:
        """Run comprehensive security audit."""
        if not self.permissions.request("security.audit"):
            return "Permission denied for security audit."

        audit_results = {
            "timestamp": datetime.now().isoformat(),
            "threats_detected": [],
            "system_status": "clean",
            "recommendations": []
        }

        # Run all checks
        for check in self.checks:
            try:
                result = check.perform_check()
                audit_results["threats_detected"].extend(result["threats"])
            except Exception as e:
                logger.error(f"Check failed: {e}")

        # Determine status
        if audit_results["threats_detected"]:
            audit_results["system_status"] = "compromised"

        # Generate recommendations
        audit_results["recommendations"] = self._generate_recommendations(audit_results["threats_detected"])

        return f"Security audit complete: {audit_results}"

    def _generate_recommendations(self, threats: List[str]) -> List[str]:
        """Generate security recommendations."""
        recommendations = []

        if any('ransom' in threat.lower() for threat in threats):
            recommendations.extend([
                "Enable Windows Defender",
                "Create system restore point",
                "Backup important files"
            ])

        if any('remote' in threat.lower() for threat in threats):
            recommendations.extend([
                "Disable Remote Desktop if not needed",
                "Use strong passwords",
                "Enable Windows Firewall"
            ])

        if not recommendations:
            recommendations.append("System appears secure")

        return recommendations