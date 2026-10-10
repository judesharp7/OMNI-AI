# integration/__init__.py
"""
Integration module for OMNI-AI advanced features.
Combines TensorFlow, Cryptography, Speech Recognition, pyttsx3, psutil, and WMI.
"""

from .omniai_integration import OmniAIIntegration, initialize_omniai

__all__ = ['OmniAIIntegration', 'initialize_omniai']
