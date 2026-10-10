# voice/advanced_voice.py
"""
Advanced voice processing with enhanced pyttsx3 and speech_recognition.
Provides multi-engine support, voice customization, and real-time processing.
"""

import logging
from typing import Optional, Callable, List, Dict, Any
from abc import ABC, abstractmethod
import threading
import queue
import time

# Speech Recognition
try:
    import speech_recognition as sr
    SPEECH_RECOGNITION_AVAILABLE = True
except ImportError:
    sr = None
    SPEECH_RECOGNITION_AVAILABLE = False

# Text-to-Speech
try:
    import pyttsx3
    PYTTSX3_AVAILABLE = True
except ImportError:
    pyttsx3 = None
    PYTTSX3_AVAILABLE = False

logger = logging.getLogger(__name__)


class AdvancedTextToSpeech:
    """Advanced text-to-speech engine with voice customization."""

    def __init__(self):
        """Initialize advanced TTS engine."""
        if not PYTTSX3_AVAILABLE:
            logger.warning("pyttsx3 not available - TTS disabled")
            self.engine = None
            return

        try:
            self.engine = pyttsx3.init()
            self.engine.setProperty('rate', 150)  # Speed
            self.engine.setProperty('volume', 0.9)  # Volume
            
            # Set default voice
            voices = self.engine.getProperty('voices')
            if voices:
                self.engine.setProperty('voice', voices[0].id)
            
            logger.info("Advanced TTS engine initialized")
        except Exception as e:
            logger.error(f"TTS initialization error: {e}")
            self.engine = None

    def set_voice_properties(self, rate: int = 150, volume: float = 0.9):
        """Set voice properties."""
        if not self.engine:
            return

        try:
            self.engine.setProperty('rate', rate)
            self.engine.setProperty('volume', volume)
            logger.info(f"Voice properties set: rate={rate}, volume={volume}")
        except Exception as e:
            logger.error(f"Error setting properties: {e}")

    def get_available_voices(self) -> List[Dict[str, Any]]:
        """Get available voices."""
        if not self.engine:
            return []

        try:
            voices = self.engine.getProperty('voices')
            return [
                {
                    'id': voice.id,
                    'name': voice.name,
                    'languages': voice.languages,
                    'gender': voice.gender
                }
                for voice in voices
            ]
        except Exception as e:
            logger.error(f"Error getting voices: {e}")
            return []

    def set_voice(self, voice_id: str):
        """Set specific voice."""
        if not self.engine:
            return

        try:
            self.engine.setProperty('voice', voice_id)
            logger.info(f"Voice set to: {voice_id}")
        except Exception as e:
            logger.error(f"Error setting voice: {e}")

    def speak(self, text: str, wait: bool = True) -> bool:
        """Speak text."""
        if not self.engine:
            logger.warning(f"TTS disabled - would say: {text}")
            return False

        try:
            self.engine.say(text)
            if wait:
                self.engine.runAndWait()
            logger.debug(f"Spoke: {text}")
            return True
        except Exception as e:
            logger.error(f"Speech error: {e}")
            return False

    def stop_speaking(self):
        """Stop current speech."""
        if self.engine:
            self.engine.stop()

    def save_to_file(self, text: str, filename: str) -> bool:
        """Save speech to audio file."""
        if not self.engine:
            return False

        try:
            self.engine.save_to_file(text, filename)
            self.engine.runAndWait()
            logger.info(f"Speech saved to: {filename}")
            return True
        except Exception as e:
            logger.error(f"Error saving to file: {e}")
            return False


class AdvancedSpeechRecognition:
    """Advanced speech-to-text with multiple engine support."""

    def __init__(self):
        """Initialize advanced STT engine."""
        if not SPEECH_RECOGNITION_AVAILABLE:
            logger.warning("speech_recognition not available - STT disabled")
            self.recognizer = None
            return

        try:
            self.recognizer = sr.Recognizer()
            self.recognizer.energy_threshold = 4000
            self.recognizer.dynamic_energy_threshold = True
            logger.info("Advanced STT engine initialized")
        except Exception as e:
            logger.error(f"STT initialization error: {e}")
            self.recognizer = None

    def listen_with_timeout(self, timeout: int = 5, phrase_time_limit: int = 10) -> Optional[str]:
        """Listen for speech with timeout."""
        if not self.recognizer:
            return None

        try:
            with sr.Microphone() as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                logger.debug("Listening...")
                
                audio = self.recognizer.listen(
                    source,
                    timeout=timeout,
                    phrase_time_limit=phrase_time_limit
                )
            
            return self._recognize_audio(audio)
        except sr.UnknownValueError:
            logger.warning("Could not understand audio")
            return None
        except sr.RequestError as e:
            logger.error(f"Recognition service error: {e}")
            return None
        except Exception as e:
            logger.error(f"Listening error: {e}")
            return None

    def recognize_from_file(self, audio_file: str) -> Optional[str]:
        """Recognize speech from audio file."""
        if not self.recognizer:
            return None

        try:
            with sr.AudioFile(audio_file) as source:
                audio = self.recognizer.record(source)
            return self._recognize_audio(audio)
        except Exception as e:
            logger.error(f"File recognition error: {e}")
            return None

    def _recognize_audio(self, audio) -> Optional[str]:
        """Recognize audio using multiple engines with fallback."""
        if not self.recognizer:
            return None

        try:
            # Try Google Speech Recognition (most reliable)
            try:
                text = self.recognizer.recognize_google(audio)
                logger.debug(f"Google recognized: {text}")
                return text
            except sr.UnknownValueError:
                logger.warning("Google: Could not understand")
            except sr.RequestError:
                logger.warning("Google service error, trying alternatives...")
            
            # Try Sphinx (offline alternative)
            try:
                text = self.recognizer.recognize_sphinx(audio)
                logger.debug(f"Sphinx recognized: {text}")
                return text
            except sr.UnknownValueError:
                logger.warning("Sphinx: Could not understand")
            except Exception:
                pass
            
            return None
        except Exception as e:
            logger.error(f"Audio recognition error: {e}")
            return None

    def detect_speech_activity(self, audio) -> float:
        """Detect speech activity level (0.0 to 1.0)."""
        if not self.recognizer or not SPEECH_RECOGNITION_AVAILABLE:
            return 0.5

        try:
            # Estimate energy level
            frame_data = audio.frame_data
            rms = sum(abs(x) for x in frame_data) / len(frame_data) if frame_data else 0
            activity = min(rms / 32768.0, 1.0)
            return activity
        except Exception as e:
            logger.error(f"Activity detection error: {e}")
            return 0.5


class VoiceInteractionEngine:
    """High-level voice interaction combining STT and TTS."""

    def __init__(self):
        """Initialize voice interaction engine."""
        self.tts = AdvancedTextToSpeech()
        self.stt = AdvancedSpeechRecognition()
        self.is_active = False
        self.listen_thread: Optional[threading.Thread] = None
        self.response_queue: queue.Queue = queue.Queue()
        self.command_queue: queue.Queue = queue.Queue()
        logger.info("Voice Interaction Engine initialized")

    def start_conversation(self, greeting: str = "Hello! I'm listening."):
        """Start voice conversation mode."""
        self.is_active = True
        self.tts.speak(greeting)
        self.listen_thread = threading.Thread(target=self._conversation_loop, daemon=True)
        self.listen_thread.start()
        logger.info("Conversation started")

    def stop_conversation(self, farewell: str = "Goodbye!"):
        """Stop voice conversation mode."""
        self.is_active = False
        self.tts.speak(farewell)
        if self.listen_thread:
            self.listen_thread.join(timeout=2.0)
        logger.info("Conversation stopped")

    def _conversation_loop(self):
        """Main conversation loop."""
        while self.is_active:
            try:
                # Listen for command
                command = self.stt.listen_with_timeout(timeout=5, phrase_time_limit=10)
                
                if command:
                    logger.info(f"User said: {command}")
                    self.command_queue.put(command)
                    
                    # Get response from queue
                    try:
                        response = self.response_queue.get(timeout=5)
                        if response:
                            self.tts.speak(response)
                    except queue.Empty:
                        self.tts.speak("No response available")
                else:
                    time.sleep(1)
            except Exception as e:
                logger.error(f"Conversation loop error: {e}")

    def process_voice_command(self, callback: Callable[[str], str]):
        """Process voice commands with callback."""
        while self.is_active:
            try:
                command = self.command_queue.get(timeout=1)
                response = callback(command)
                self.response_queue.put(response)
            except queue.Empty:
                pass
            except Exception as e:
                logger.error(f"Command processing error: {e}")

    def ask_question(self, question: str, timeout: int = 10) -> Optional[str]:
        """Ask a question and get voice response."""
        self.tts.speak(question)
        return self.stt.listen_with_timeout(timeout=timeout)

    def read_text(self, text: str, save_to_file: Optional[str] = None) -> bool:
        """Read text aloud, optionally saving to file."""
        if save_to_file:
            return self.tts.save_to_file(text, save_to_file)
        else:
            return self.tts.speak(text)


# Export classes
__all__ = [
    'AdvancedTextToSpeech',
    'AdvancedSpeechRecognition',
    'VoiceInteractionEngine',
    'PYTTSX3_AVAILABLE',
    'SPEECH_RECOGNITION_AVAILABLE'
]
