# voice/engine.py
"""
Voice processing system following SOLID principles.
Single responsibility: handle speech-to-text and text-to-speech.
"""

from typing import Optional, Callable, Any
from abc import ABC, abstractmethod
import threading
import queue
import logging

# Optional imports
try:
    import speech_recognition as sr
except ImportError:
    sr = None

try:
    import pyttsx3
except ImportError:
    pyttsx3 = None

logger = logging.getLogger(__name__)

class SpeechToTextEngine(ABC):
    """Abstract base class for speech-to-text."""

    @abstractmethod
    def listen(self) -> Optional[str]:
        """Listen for speech and convert to text."""
        pass

class TextToSpeechEngine(ABC):
    """Abstract base class for text-to-speech."""

    @abstractmethod
    def speak(self, text: str) -> None:
        """Convert text to speech."""
        pass

class GoogleSTTEngine(SpeechToTextEngine):
    """Google Speech-to-Text engine."""

    def __init__(self):
        self.recognizer = sr.Recognizer() if sr else None

    def listen(self) -> Optional[str]:
        if not self.recognizer:
            return "Speech recognition not available"

        try:
            with sr.Microphone() as source:
                self.recognizer.adjust_for_ambient_noise(source)
                audio = self.recognizer.listen(source)
                return self.recognizer.recognize_google(audio)
        except Exception as e:
            logger.error(f"Speech recognition error: {e}")
            return None

class PyTTSXEngine(TextToSpeechEngine):
    """pyttsx3 Text-to-Speech engine."""

    def __init__(self):
        self.engine = pyttsx3.init() if pyttsx3 else None

    def speak(self, text: str) -> None:
        if self.engine:
            self.engine.say(text)
            self.engine.runAndWait()
        else:
            print(f"TTS: {text}")

class VoiceEngine:
    """
    Voice processing engine with STT and TTS capabilities.
    Uses strategy pattern for different engines.
    """

    def __init__(self):
        self.stt_engine = GoogleSTTEngine()
        self.tts_engine = PyTTSXEngine()
        self.is_listening = False
        self.command_queue = queue.Queue()
        self.callback: Optional[Callable[[str], str]] = None
        self.listen_thread: Optional[threading.Thread] = None

    def start_voice_control(self, callback: Callable[[str], str]) -> None:
        """Start voice control with callback."""
        self.callback = callback
        self.is_listening = True
        self.listen_thread = threading.Thread(target=self._listen_loop, daemon=True)
        self.listen_thread.start()
        logger.info("Voice control started")

    def stop_voice_control(self) -> None:
        """Stop voice control."""
        self.is_listening = False
        if self.listen_thread:
            self.listen_thread.join(timeout=1.0)
        logger.info("Voice control stopped")

    def _listen_loop(self) -> None:
        """Main listening loop."""
        while self.is_listening:
            try:
                command = self.stt_engine.listen()
                if command and self.callback:
                    response = self.callback(command)
                    self.tts_engine.speak(response)
            except Exception as e:
                logger.error(f"Voice loop error: {e}")

    def speak(self, text: str) -> None:
        """Speak text."""
        self.tts_engine.speak(text)