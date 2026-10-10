# core/memory.py
"""
Context and memory management following SOLID principles.
Single responsibility: manage conversation context, entity history, and long-term memory.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import threading
from collections import deque
import logging

logger = logging.getLogger(__name__)

class ContextManager:
    """
    Manages conversation context, recent entity state, preferences, and key-value user memory.
    Thread-safe and efficient memory usage.
    """

    def __init__(self, max_context_length: int = 15):
        self.max_context_length = max_context_length
        self.context_memory: deque = deque(maxlen=max_context_length)
        self.entity_history: Dict[str, List[Any]] = {
            "contacts": [],
            "apps": [],
            "hardware": [],
            "ips": [],
            "com_ports": [],
            "commands": []
        }
        self.user_memory: Dict[str, Any] = {}
        self.preferences: Dict[str, Any] = {}
        self._lock = threading.RLock()  # Reentrant lock for thread safety

    def add_user_message(self, content: str) -> None:
        """Add user message to context."""
        with self._lock:
            message = {
                "role": "user",
                "content": content,
                "timestamp": datetime.now().isoformat()
            }
            self.context_memory.append(message)
            logger.debug(f"Added user message: {content[:50]}...")

    def add_assistant_message(self, content: str) -> None:
        """Add assistant message to context."""
        with self._lock:
            message = {
                "role": "assistant",
                "content": content,
                "timestamp": datetime.now().isoformat()
            }
            self.context_memory.append(message)
            logger.debug(f"Added assistant message: {content[:50]}...")

    def update_entities(self, entities: Dict[str, Any]) -> None:
        """Track extracted entities in history for pronoun and contextual reference."""
        with self._lock:
            for key, val in entities.items():
                if key in self.entity_history and isinstance(val, list):
                    for item in val:
                        if item and item not in self.entity_history[key]:
                            self.entity_history[key].append(item)
                        # Keep list concise (max 10 recent per category)
                        if len(self.entity_history[key]) > 10:
                            self.entity_history[key].pop(0)

    def get_last_entity(self, entity_type: str) -> Optional[Any]:
        """Retrieve the most recent entity of a specific type for pronoun resolution."""
        with self._lock:
            history = self.entity_history.get(entity_type, [])
            return history[-1] if history else None

    def store_user_fact(self, key: str, value: Any) -> None:
        """Store a long-term fact or preference about the user."""
        with self._lock:
            key_clean = key.lower().strip()
            self.user_memory[key_clean] = value
            logger.info(f"Stored user memory: {key_clean} = {value}")

    def get_user_fact(self, key: str) -> Optional[Any]:
        """Retrieve a stored user fact."""
        with self._lock:
            return self.user_memory.get(key.lower().strip())

    def search_user_fact(self, query: str) -> Dict[str, Any]:
        """Search user memory by fuzzy key matching."""
        with self._lock:
            q = query.lower().strip()
            results = {}
            for k, v in self.user_memory.items():
                if q in k or k in q:
                    results[k] = v
            return results

    def set_preference(self, key: str, value: Any) -> None:
        """Set system/user preference."""
        with self._lock:
            self.preferences[key.lower().strip()] = value

    def get_preference(self, key: str, default: Any = None) -> Any:
        """Get system/user preference."""
        with self._lock:
            return self.preferences.get(key.lower().strip(), default)

    def get_recent_context(self, limit: Optional[int] = None) -> List[Dict]:
        """Get recent conversation context."""
        with self._lock:
            if limit is None:
                return list(self.context_memory)
            return list(self.context_memory)[-limit:]

    def clear_context(self) -> None:
        """Clear all context memory."""
        with self._lock:
            self.context_memory.clear()
            self.entity_history = {k: [] for k in self.entity_history}
            logger.info("Context memory cleared")

    def get_context_summary(self) -> Dict[str, Any]:
        """Get summary of current context and memory."""
        with self._lock:
            return {
                "total_messages": len(self.context_memory),
                "max_capacity": self.max_context_length,
                "utilization_percent": (len(self.context_memory) / self.max_context_length) * 100,
                "stored_facts_count": len(self.user_memory),
                "recent_entities": {k: len(v) for k, v in self.entity_history.items()},
                "last_message_time": self.context_memory[-1]["timestamp"] if self.context_memory else None
            }