# security/encryption.py
"""
Encryption and security module using cryptography.Fernet.
Provides secure data encryption, key management, and cryptographic operations.
"""

import logging
import os
import json
from typing import Optional, Dict, Any, Tuple
from datetime import datetime, timedelta
import base64

# Cryptography imports
try:
    from cryptography.fernet import Fernet, InvalidToken
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
    from cryptography.hazmat.backends import default_backend
    CRYPTO_AVAILABLE = True
except ImportError:
    Fernet = None
    InvalidToken = None
    PBKDF2 = None
    hashes = None
    default_backend = None
    CRYPTO_AVAILABLE = False

logger = logging.getLogger(__name__)


class EncryptionManager:
    """Secure encryption and decryption manager."""

    def __init__(self, key: Optional[bytes] = None):
        """
        Initialize encryption manager.
        
        Args:
            key: Fernet encryption key (generated if not provided)
        """
        if not CRYPTO_AVAILABLE:
            logger.warning("Cryptography library not available")
            self.cipher = None
            self.key = None
            return

        if key:
            try:
                self.key = key
                self.cipher = Fernet(key)
                logger.info("Encryption manager initialized with provided key")
            except Exception as e:
                logger.error(f"Invalid key provided: {e}")
                self.generate_new_key()
        else:
            self.generate_new_key()

    def generate_new_key(self) -> bytes:
        """Generate a new encryption key."""
        if not CRYPTO_AVAILABLE:
            return None

        self.key = Fernet.generate_key()
        self.cipher = Fernet(self.key)
        logger.info("New encryption key generated")
        return self.key

    def encrypt_data(self, data: str) -> Optional[bytes]:
        """
        Encrypt sensitive data.
        
        Args:
            data: Data to encrypt
            
        Returns:
            Encrypted data or None if failed
        """
        if not self.cipher:
            logger.warning("Encryption not available")
            return data.encode() if isinstance(data, str) else data

        try:
            encrypted = self.cipher.encrypt(data.encode() if isinstance(data, str) else data)
            logger.debug("Data encrypted successfully")
            return encrypted
        except Exception as e:
            logger.error(f"Encryption error: {e}")
            return None

    def decrypt_data(self, encrypted_data: bytes) -> Optional[str]:
        """
        Decrypt sensitive data.
        
        Args:
            encrypted_data: Encrypted data to decrypt
            
        Returns:
            Decrypted data or None if failed
        """
        if not self.cipher:
            logger.warning("Encryption not available")
            return encrypted_data.decode() if isinstance(encrypted_data, bytes) else encrypted_data

        try:
            decrypted = self.cipher.decrypt(encrypted_data)
            logger.debug("Data decrypted successfully")
            return decrypted.decode()
        except InvalidToken:
            logger.error("Invalid encryption token")
            return None
        except Exception as e:
            logger.error(f"Decryption error: {e}")
            return None

    def encrypt_dict(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Encrypt dictionary contents."""
        encrypted_dict = {}
        
        for key, value in data.items():
            if isinstance(value, str):
                encrypted_value = self.encrypt_data(value)
                encrypted_dict[key] = encrypted_value.decode() if encrypted_value else None
            elif isinstance(value, dict):
                encrypted_dict[key] = self.encrypt_dict(value)
            else:
                encrypted_dict[key] = value
        
        return encrypted_dict

    def decrypt_dict(self, encrypted_data: Dict[str, Any]) -> Dict[str, Any]:
        """Decrypt dictionary contents."""
        decrypted_dict = {}
        
        for key, value in encrypted_data.items():
            if isinstance(value, str):
                # Try to decrypt if it looks encrypted
                decrypted_value = self.decrypt_data(value.encode())
                decrypted_dict[key] = decrypted_value if decrypted_value else value
            elif isinstance(value, dict):
                decrypted_dict[key] = self.decrypt_dict(value)
            else:
                decrypted_dict[key] = value
        
        return decrypted_dict

    def encrypt_file(self, input_path: str, output_path: str) -> bool:
        """Encrypt file contents."""
        try:
            with open(input_path, 'rb') as f:
                data = f.read()
            
            encrypted = self.cipher.encrypt(data) if self.cipher else data
            
            with open(output_path, 'wb') as f:
                f.write(encrypted)
            
            logger.info(f"File encrypted: {input_path} -> {output_path}")
            return True
        except Exception as e:
            logger.error(f"File encryption error: {e}")
            return False

    def decrypt_file(self, input_path: str, output_path: str) -> bool:
        """Decrypt file contents."""
        try:
            with open(input_path, 'rb') as f:
                encrypted_data = f.read()
            
            decrypted = self.cipher.decrypt(encrypted_data) if self.cipher else encrypted_data
            
            with open(output_path, 'wb') as f:
                f.write(decrypted)
            
            logger.info(f"File decrypted: {input_path} -> {output_path}")
            return True
        except Exception as e:
            logger.error(f"File decryption error: {e}")
            return False

    def save_key(self, filepath: str) -> bool:
        """Save encryption key to file."""
        try:
            with open(filepath, 'wb') as f:
                f.write(self.key)
            logger.info(f"Encryption key saved to {filepath}")
            return True
        except Exception as e:
            logger.error(f"Error saving key: {e}")
            return False

    def load_key(self, filepath: str) -> bool:
        """Load encryption key from file."""
        try:
            with open(filepath, 'rb') as f:
                self.key = f.read()
            self.cipher = Fernet(self.key) if CRYPTO_AVAILABLE else None
            logger.info(f"Encryption key loaded from {filepath}")
            return True
        except Exception as e:
            logger.error(f"Error loading key: {e}")
            return False


class PasswordHasher:
    """Secure password hashing using PBKDF2."""

    def __init__(self, iterations: int = 100000):
        """
        Initialize password hasher.
        
        Args:
            iterations: Number of PBKDF2 iterations
        """
        if not CRYPTO_AVAILABLE or not PBKDF2:
            logger.warning("Cryptography library not available")
            self.iterations = iterations
            return

        self.iterations = iterations
        self.backend = default_backend()
        logger.info(f"Password hasher initialized with {iterations} iterations")

    def hash_password(self, password: str, salt: Optional[bytes] = None) -> Tuple[str, str]:
        """
        Hash a password using PBKDF2.
        
        Args:
            password: Password to hash
            salt: Salt value (generated if not provided)
            
        Returns:
            Tuple of (hash, salt) as base64 strings
        """
        if not CRYPTO_AVAILABLE or not PBKDF2:
            return base64.b64encode(password.encode()).decode(), "no_salt"

        try:
            if salt is None:
                salt = os.urandom(16)
            else:
                salt = base64.b64decode(salt)

            kdf = PBKDF2(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=self.iterations,
                backend=self.backend
            )

            hash_value = kdf.derive(password.encode())
            return base64.b64encode(hash_value).decode(), base64.b64encode(salt).decode()

        except Exception as e:
            logger.error(f"Password hashing error: {e}")
            return None, None

    def verify_password(self, password: str, hash_value: str, salt: str) -> bool:
        """
        Verify a password against its hash.
        
        Args:
            password: Password to verify
            hash_value: Stored hash
            salt: Stored salt
            
        Returns:
            True if password matches, False otherwise
        """
        if not CRYPTO_AVAILABLE or not PBKDF2:
            return password == base64.b64decode(hash_value).decode()

        try:
            computed_hash, _ = self.hash_password(password, salt)
            return computed_hash == hash_value
        except Exception as e:
            logger.error(f"Password verification error: {e}")
            return False


class SecureSessionManager:
    """Manage secure sessions with encrypted data."""

    def __init__(self, encryption_manager: EncryptionManager):
        """Initialize session manager."""
        self.encryption_manager = encryption_manager
        self.sessions: Dict[str, Dict[str, Any]] = {}
        logger.info("Secure Session Manager initialized")

    def create_session(self, session_id: str, data: Dict[str, Any], 
                      ttl_minutes: int = 60) -> bool:
        """Create an encrypted session."""
        try:
            encrypted_data = self.encryption_manager.encrypt_dict(data)
            expiry = datetime.now() + timedelta(minutes=ttl_minutes)
            
            self.sessions[session_id] = {
                'data': encrypted_data,
                'expiry': expiry,
                'created': datetime.now()
            }
            
            logger.info(f"Session created: {session_id}")
            return True
        except Exception as e:
            logger.error(f"Session creation error: {e}")
            return False

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve and decrypt session data."""
        try:
            if session_id not in self.sessions:
                return None
            
            session = self.sessions[session_id]
            
            # Check expiry
            if datetime.now() > session['expiry']:
                del self.sessions[session_id]
                logger.info(f"Session expired: {session_id}")
                return None
            
            decrypted_data = self.encryption_manager.decrypt_dict(session['data'])
            return decrypted_data
        except Exception as e:
            logger.error(f"Session retrieval error: {e}")
            return None

    def delete_session(self, session_id: str) -> bool:
        """Delete session."""
        try:
            if session_id in self.sessions:
                del self.sessions[session_id]
                logger.info(f"Session deleted: {session_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Session deletion error: {e}")
            return False


# Export classes
__all__ = [
    'EncryptionManager',
    'PasswordHasher',
    'SecureSessionManager',
    'CRYPTO_AVAILABLE'
]
