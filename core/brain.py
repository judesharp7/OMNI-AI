# core/brain.py
"""
Core intelligence engine using Transformer architecture.
Handles intent classification, entity extraction, and response generation.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple, Any, Protocol
from dataclasses import dataclass
from datetime import datetime
import re
import time
import logging

# Optional imports with fallbacks
try:
    import torch
    import torch.nn as nn
    import torch.nn.functional as F
    TORCH_AVAILABLE = True
except ImportError:
    torch = None
    nn = None
    F = None
    TORCH_AVAILABLE = False
try:
    import numpy as np  # type: ignore
except ImportError:
    np = None  # type: ignore

from .memory import ContextManager
from .personality import ResponseGenerator

# Configure logging
logger = logging.getLogger(__name__)

@dataclass
class IntentResult:
    """Data class for intent classification results."""
    intent: str
    confidence: float
    entities: Dict[str, Any]
    action_plan: List[Dict]
    response: str
    requires_confirmation: bool

class ModelInterface(Protocol):
    """Protocol for ML model interface."""
    def predict(self, input_batch, verbose: int = 0) -> Tuple[List[List[float]], List[List[float]]]:
        ...

    def save_weights(self, path: str) -> None:
        ...

    def load_weights(self, path: str) -> None:
        ...

    def compile(self, **kwargs) -> None:
        ...

class MockTFModel:
    """Mock TensorFlow model for fallback when TF is not available."""

    def __init__(self, n_intents: int, context_window: int, embedding_dim: int):
        self.n_intents = n_intents
        self.context_window = context_window
        self.embedding_dim = embedding_dim
        logger.info("Using MockTFModel - TensorFlow not available")

    def predict(self, input_batch, verbose=0):
        # Return low confidence to trigger rule-based fallback
        intent_vector = [[0.1] + [0.0] * (self.n_intents - 1)]
        response_vector = [[0.0] * (self.context_window * self.embedding_dim)]
        return intent_vector, response_vector

    def save_weights(self, path):
        pass

    def load_weights(self, path):
        pass

    def compile(self, **kwargs):
        pass

class PyTorchTransformerModel(nn.Module if TORCH_AVAILABLE else object):
    """PyTorch-based transformer model for intent classification."""

    def __init__(self, n_intents: int, context_window: int, embedding_dim: int,
                 num_heads: int = 4, ff_dim: int = 256):
        if not TORCH_AVAILABLE:
            raise ImportError("PyTorch required for PyTorchTransformerModel")

        super().__init__()  # Required for nn.Module registration

        self.n_intents = n_intents
        self.context_window = context_window
        self.embedding_dim = embedding_dim
        self.num_heads = num_heads
        self.ff_dim = ff_dim

        # Model components
        self.embedding = nn.Embedding(50000, embedding_dim)
        self.pos_embedding = nn.Embedding(context_window, embedding_dim)

        # Transformer layers
        self.transformer_blocks = nn.ModuleList([
            nn.TransformerEncoderLayer(
                d_model=embedding_dim,
                nhead=num_heads,
                dim_feedforward=ff_dim,
                dropout=0.1,
                batch_first=True
            ) for _ in range(2)  # Reduced for efficiency
        ])

        # Output heads
        self.intent_classifier = nn.Linear(embedding_dim, n_intents)
        self.response_generator = nn.Linear(embedding_dim, context_window * embedding_dim)

        # Initialize weights
        self.apply(self._init_weights)

    def _init_weights(self, module):
        if isinstance(module, nn.Linear):
            torch.nn.init.xavier_uniform_(module.weight)
            if module.bias is not None:
                torch.nn.init.zeros_(module.bias)
        elif isinstance(module, nn.Embedding):
            torch.nn.init.normal_(module.weight, mean=0, std=0.02)

    def forward(self, input_tokens):
        # input_tokens shape: (batch_size, seq_len)
        seq_len = input_tokens.size(1)

        # Embeddings
        token_emb = self.embedding(input_tokens)
        positions = torch.arange(0, seq_len, device=input_tokens.device).unsqueeze(0)
        pos_emb = self.pos_embedding(positions)

        x = token_emb + pos_emb

        # Transformer blocks
        for transformer in self.transformer_blocks:
            x = transformer(x)

        # Global average pooling
        x = torch.mean(x, dim=1)

        # Output heads
        intent_logits = self.intent_classifier(x)
        response_emb = self.response_generator(x)

        return intent_logits, response_emb

    def predict(self, input_batch, verbose=0):
        with torch.no_grad():
            if isinstance(input_batch, list):
                input_batch = torch.tensor(input_batch, dtype=torch.long)

            intent_logits, response_emb = self.forward(input_batch)

            # Convert to numpy for compatibility
            intent_probs = F.softmax(intent_logits, dim=-1).cpu().numpy()
            response_emb = response_emb.cpu().numpy()

            return intent_probs, response_emb

    def save_weights(self, path):
        torch.save(self.state_dict(), path)

    def load_weights(self, path):
        if torch.cuda.is_available():
            self.load_state_dict(torch.load(path))
        else:
            self.load_state_dict(torch.load(path, map_location=torch.device('cpu')))

    def compile(self, **kwargs):
        # PyTorch doesn't need compilation like TensorFlow
        pass

class IntentClassifier:
    """Handles intent classification with rule-based, contextual, and ML fallbacks."""

    def __init__(self):
        self.intents = [
            "message_read", "message_reply", "message_send",
            "hardware_flashlight", "hardware_camera", "hardware_volume",
            "hardware_brightness", "hardware_memory",
            "app_open", "app_close", "app_send_message",
            "word_process", "security_audit",
            "memory_search", "memory_store", "general_chat",
            "weather_query", "reminder_set", "alarm_set",
            "call_make", "contact_search", "system_status",
            "execute_command", "custom_instruction",
            "hardware_remote_control", "hardware_microcontroller"
        ]

    def classify_rule_based(self, text: str, context_manager: Optional[ContextManager] = None) -> str:
        """Fast rule-based and context-aware intent classification."""
        text_lower = text.lower().strip()

        # Memory store phrases
        if any(p in text_lower for p in ["remember that", "remember my", "my name is", "my favorite", "store fact"]):
            return "memory_store"

        # Memory search / recall phrases
        if any(p in text_lower for p in ["what is my", "do you remember", "what did i say", "recall", "what's my"]):
            return "memory_search"

        # Hardware intents & Pronoun resolution
        if any(word in text_lower for word in ["flashlight", "torch", "light"]):
            return "hardware_flashlight"
        elif any(word in text_lower for word in ["volume", "sound", "audio"]):
            return "hardware_volume"
        elif any(word in text_lower for word in ["brightness", "screen", "display"]):
            return "hardware_brightness"
        elif any(word in text_lower for word in ["camera", "photo", "picture"]):
            return "hardware_camera"
        elif any(word in text_lower for word in ["memory", "ram", "storage"]):
            return "hardware_memory"

        # Context-aware pronoun handling for hardware (e.g. "turn it off", "turn it on")
        if context_manager and any(w in text_lower for w in ["turn it off", "turn it on", "switch it off", "switch it on"]):
            last_hw = context_manager.get_last_entity("hardware")
            if last_hw:
                return f"hardware_{last_hw}"

        # App intents & Context-aware pronoun handling (e.g. "close it", "open it")
        if any(word in text_lower for word in ["open", "launch", "start"]):
            if any(app in text_lower for app in ["whatsapp", "facebook", "chrome", "word", "excel"]):
                return "app_open"
            elif context_manager and "it" in text_lower and context_manager.get_last_entity("apps"):
                return "app_open"

        if any(word in text_lower for word in ["close", "stop", "quit"]):
            if any(app in text_lower for app in ["whatsapp", "facebook", "chrome"]):
                return "app_close"
            elif context_manager and "it" in text_lower and context_manager.get_last_entity("apps"):
                return "app_close"

        # Message intents
        if any(word in text_lower for word in ["send", "message", "text"]) and \
           any(contact in text_lower for contact in ["to", "message"]):
            return "message_send"

        # Word processing
        if any(word in text_lower for word in ["word", "document", "write", "create"]):
            return "word_process"

        # Security
        if any(word in text_lower for word in ["audit", "security", "check", "scan"]):
            return "security_audit"

        # System status / Health queries
        if any(word in text_lower for word in ["system status", "health", "how are you", "status check", "system health"]):
            return "system_status"

        # Remote PC Commands
        if "on pc" in text_lower or "remote" in text_lower or "ip" in text_lower or re.search(r'\d+\.\d+\.\d+\.\d+', text_lower):
            return "hardware_remote_control"
            
        # Microcontroller Commands
        if "microcontroller" in text_lower or "arduino" in text_lower or "esp" in text_lower or "usb" in text_lower or "com port" in text_lower or re.search(r'com\d+', text_lower):
            return "hardware_microcontroller"

        # System commands
        if any(word in text_lower for word in ["run", "execute", "do", "perform"]) or \
           text_lower.startswith(("dir", "ls", "echo", "date")):
            return "execute_command"

        # Conversational greetings / general chat
        if any(word in text_lower for word in ["hello", "hi", "hey", "who are you", "what can you do", "thanks", "thank you"]):
            return "general_chat"

        return "custom_instruction"

class EntityExtractor:
    """Extracts entities from text with rule-based patterns and contextual pronoun resolution."""

    def extract(self, text: str, context_manager: Optional[ContextManager] = None) -> Dict[str, Any]:
        """Extract named entities, parameters, and sentiment."""
        entities = {
            "contacts": [],
            "apps": [],
            "hardware": [],
            "time_references": [],
            "messages": [],
            "commands": [],
            "parameters": [],
            "ips": [],
            "com_ports": [],
            "memory_key": None,
            "memory_val": None,
            "sentiment": "neutral"
        }

        text_lower = text.lower()

        # Sentiment analysis
        if any(w in text_lower for w in ["great", "awesome", "good", "thanks", "thank you", "excellent"]):
            entities["sentiment"] = "positive"
        elif any(w in text_lower for w in ["bad", "slow", "error", "broken", "wrong", "fail"]):
            entities["sentiment"] = "negative"

        # Fact extraction (Memory Store)
        name_match = re.search(r"(?:my name is|i am|call me)\s+([a-zA-Z0-9_]+)", text_lower)
        if name_match:
            entities["memory_key"] = "name"
            entities["memory_val"] = name_match.group(1).capitalize()

        fav_match = re.search(r"my favorite\s+([a-zA-Z0-9_]+)\s+is\s+([a-zA-Z0-9_ ]+)", text_lower)
        if fav_match:
            entities["memory_key"] = f"favorite_{fav_match.group(1)}"
            entities["memory_val"] = fav_match.group(2).strip()

        rem_match = re.search(r"remember (?:that\s+)?(.+?)\s+is\s+(.+)", text_lower)
        if rem_match and not entities["memory_key"]:
            entities["memory_key"] = rem_match.group(1).strip()
            entities["memory_val"] = rem_match.group(2).strip()

        # Fact Query extraction (Memory Search)
        query_name_match = re.search(r"what(?:'s|\s+is)\s+my\s+([a-zA-Z0-9_ ]+)", text_lower)
        if query_name_match:
            entities["memory_key"] = query_name_match.group(1).strip()

        # Contact extraction
        contact_patterns = [
            r"from (\w+)", r"to (\w+)", r"message (\w+)",
            r"text (\w+)", r"call (\w+)", r"with (\w+)"
        ]
        for pattern in contact_patterns:
            matches = re.findall(pattern, text_lower)
            entities["contacts"].extend(matches)

        # App detection
        common_apps = ["whatsapp", "facebook", "messenger", "chrome",
                      "camera", "gallery", "settings", "calendar",
                      "word", "excel", "notepad", "calculator",
                      "file explorer", "explorer", "cmd", "powershell"]
        for app in common_apps:
            if app in text_lower:
                entities["apps"].append(app)

        # Hardware detection
        hardware_keywords = {
            "flashlight": ["flashlight", "torch", "flash", "light"],
            "camera": ["camera", "photo", "picture", "selfie", "capture"],
            "volume": ["volume", "sound", "audio", "loud", "quiet", "mute"],
            "brightness": ["brightness", "screen", "display", "dim", "bright"],
            "memory": ["memory", "ram", "storage", "disk", "scan"]
        }
        for hw, keywords in hardware_keywords.items():
            if any(kw in text_lower for kw in keywords):
                entities["hardware"].append(hw)

        # Time extraction
        time_patterns = [
            r"at (\d{1,2}(?::\d{2})?\s*(?:am|pm)?)",
            r"in (\d+)\s*(minutes?|hours?|days?)",
            r"tomorrow", r"today", r"tonight"
        ]
        for pattern in time_patterns:
            matches = re.findall(pattern, text_lower)
            entities["time_references"].extend(matches)

        # Command extraction
        command_patterns = [
            r"(?:run|execute|do|perform)\s+(.+)",
            r"(?:open|launch|start)\s+(.+)",
            r"(?:close|stop|quit)\s+(.+)",
            r"(?:set|change|adjust)\s+(.+)",
            r"(?:check|show|get|display)\s+(.+)",
            r"(?:send|write|create)\s+(.+)"
        ]
        for pattern in command_patterns:
            match = re.search(pattern, text_lower)
            if match:
                entities["commands"].append(match.group(1).strip())

        # Parameter extraction
        param_patterns = [
            r"to\s+(\w+)", r"with\s+(.+)", r"using\s+(.+)",
            r"level\s+(\d+)", r"value\s+(\d+)", r"at\s+(\d+)%?"
        ]
        for pattern in param_patterns:
            matches = re.findall(pattern, text_lower)
            entities["parameters"].extend(matches)

        # IP Address extraction
        ip_pattern = r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b"
        entities["ips"].extend(re.findall(ip_pattern, text))

        # COM Port extraction
        com_pattern = r"\bcom\d+\b"
        entities["com_ports"].extend(re.findall(com_pattern, text_lower))

        # Microcontroller instructions
        if "microcontroller" in text_lower or "arduino" in text_lower or "esp" in text_lower:
            cmd_match = re.search(r"(?:send|instruction|command|run)\s+(.+)", text_lower)
            if cmd_match:
                cmd_str = cmd_match.group(1).strip()
                if cmd_str not in entities["commands"]:
                    entities["commands"].append(cmd_str)

        # Pronoun & Anaphora resolution using recent context history
        if context_manager:
            if not entities["apps"] and any(pronoun in text_lower for pronoun in ["it", "that app", "the app"]):
                last_app = context_manager.get_last_entity("apps")
                if last_app:
                    entities["apps"].append(last_app)

            if not entities["hardware"] and any(pronoun in text_lower for pronoun in ["it", "that", "the device"]):
                last_hw = context_manager.get_last_entity("hardware")
                if last_hw:
                    entities["hardware"].append(last_hw)

            if not entities["contacts"] and any(pronoun in text_lower for pronoun in ["him", "her", "them", "that person"]):
                last_contact = context_manager.get_last_entity("contacts")
                if last_contact:
                    entities["contacts"].append(last_contact)

        return entities

class ActionPlanner:
    """Creates action plans based on intents and entities."""

    def create_plan(self, intent: str, entities: Dict, context: Dict) -> List[Dict]:
        """Create sequence of actions to execute."""
        plan = []

        if intent == "message_read":
            plan.append({
                "action": "fetch_messages",
                "platform": entities["apps"][0] if entities["apps"] else "whatsapp",
                "contact": entities["contacts"][0] if entities["contacts"] else None,
                "limit": 5
            })

        elif intent in ["message_reply", "message_send"]:
            plan.append({
                "action": "send_message",
                "platform": entities["apps"][0] if entities["apps"] else "whatsapp",
                "contact": entities["contacts"][0] if entities["contacts"] else "unknown",
                "message": self._extract_message_content(context.get("raw_input", ""))
            })

        elif intent == "hardware_remote_control":
            cmd = entities["commands"][0] if entities["commands"] else context.get("raw_input", "").replace("on pc", "").replace("remote", "").strip()
            ip = entities["ips"][0] if entities["ips"] else "127.0.0.1"
            plan.append({
                "action": "remote_control",
                "ip": ip,
                "command": cmd
            })

        elif intent == "hardware_microcontroller":
            cmd = entities["commands"][0] if entities["commands"] else context.get("raw_input", "").replace("microcontroller", "").strip()
            port = entities["com_ports"][0].upper() if entities["com_ports"] else "COM3"
            plan.append({
                "action": "microcontroller_control",
                "port": port,
                "command": cmd
            })

        elif intent.startswith("hardware_"):
            hw_type = intent.replace("hardware_", "")
            plan.append({
                "action": "control_hardware",
                "hardware": hw_type,
                "operation": self._determine_hardware_operation(context.get("raw_input", ""), hw_type)
            })

        elif intent == "app_open":
            plan.append({
                "action": "launch_app",
                "app_name": entities["apps"][0] if entities["apps"] else None
            })

        elif intent == "app_close":
            plan.append({
                "action": "close_app",
                "app_name": entities["apps"][0] if entities["apps"] else None
            })

        elif intent == "word_process":
            plan.append({
                "action": "word_process",
                "text": context.get("raw_input", "")
            })

        elif intent == "security_audit":
            plan.append({"action": "security_audit"})

        elif intent == "system_status":
            plan.append({"action": "system_status"})

        elif intent == "memory_store":
            plan.append({
                "action": "store_memory",
                "key": entities.get("memory_key"),
                "value": entities.get("memory_val")
            })

        elif intent == "memory_search":
            plan.append({
                "action": "search_memory",
                "key": entities.get("memory_key")
            })

        elif intent == "execute_command":
            cmd = entities["commands"][0] if entities["commands"] else context.get("raw_input", "").replace("Execute command:", "").replace("execute command:", "").strip()
            plan.append({"action": "execute_command", "command": cmd})

        elif intent == "custom_instruction":
            plan.append({
                "action": "custom_instruction",
                "instruction": context.get("raw_input", ""),
                "entities": entities
            })

        # Fallback
        if not plan and entities["commands"]:
            plan.append({"action": "execute_command", "command": entities["commands"][0]})

        return plan

    def _determine_hardware_operation(self, text: str, hardware: str) -> Dict:
        """Determine hardware operation from context."""
        text_lower = text.lower()

        if hardware == "flashlight":
            if any(w in text_lower for w in ["off", "disable", "stop", "deactivate", "turn off"]):
                return {"state": "off", "brightness": 0}
            else:
                return {"state": "on", "brightness": 100}

        elif hardware == "volume":
            level = 50
            if "up" in text_lower or "louder" in text_lower or "increase" in text_lower:
                level = min(100, level + 20)
            elif "down" in text_lower or "quieter" in text_lower or "decrease" in text_lower:
                level = max(0, level - 20)
            elif "mute" in text_lower or "silent" in text_lower:
                level = 0
            return {"level": level}

        elif hardware == "brightness":
            level = 50
            if "up" in text_lower or "brighter" in text_lower:
                level = min(100, level + 30)
            elif "down" in text_lower or "dimmer" in text_lower:
                level = max(0, level - 30)
            return {"level": level}

        elif hardware == "memory":
            return {"scan": True}

        return {}

    def _extract_message_content(self, text: str) -> str:
        """Extract message content to send."""
        patterns = [
            r'saying\s+["\']?(.+?)["\']?(?:$|\.|\!)',
            r'say\s+["\']?(.+?)["\']?(?:$|\.|\!)',
            r'message\s+["\']?(.+?)["\']?(?:$|\.|\!)',
            r'reply\s+["\']?(.+?)["\']?(?:$|\.|\!)'
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return "Hello"

class OmniBrain:
    """
    Central intelligence engine using SOLID principles.
    Single responsibility: coordinate intent processing, memory integration, and response generation.
    """

    def __init__(self, model_path: Optional[str] = None):
        self.model_path = model_path or "models/omniai_brain"
        self.context_window = 2048
        self.embedding_dim = 128
        self.num_heads = 4
        self.ff_dim = 256

        # Dependency injection - components are loosely coupled
        self.intent_classifier = IntentClassifier()
        self.entity_extractor = EntityExtractor()
        self.action_planner = ActionPlanner()
        self.context_manager = ContextManager()
        self.response_generator = ResponseGenerator()
        
        self.model: ModelInterface = self._init_model()

        logger.info("OmniBrain initialized with SOLID architecture and adaptive memory")

    def _init_model(self) -> ModelInterface:
        """Initialize ML model with fallback."""
        if TORCH_AVAILABLE:
            try:
                return PyTorchTransformerModel(
                    n_intents=len(self.intent_classifier.intents),
                    context_window=self.context_window,
                    embedding_dim=self.embedding_dim,
                    num_heads=self.num_heads,
                    ff_dim=self.ff_dim
                )
            except Exception as e:
                logger.warning(f"Failed to initialize PyTorchTransformerModel: {e}")
        return MockTFModel(
            n_intents=len(self.intent_classifier.intents),
            context_window=self.context_window,
            embedding_dim=self.embedding_dim
        )

    def tokenize(self, text: str) -> List[int]:
        """Simple tokenization."""
        words = text.lower().split()
        return [hash(w) % 49999 + 1 for w in words[:self.context_window]]

    def pad_sequence(self, tokens: List[int]) -> List[int]:
        """Pad or truncate to context window."""
        if len(tokens) < self.context_window:
            tokens = tokens + [0] * (self.context_window - len(tokens))
        return tokens[:self.context_window]

    def process_input(self, user_input: str, context: Optional[Dict] = None) -> IntentResult:
        """
        Main adaptive processing pipeline with context awareness and fast latency.
        """
        start_time = time.time()

        # Add user message to memory
        self.context_manager.add_user_message(user_input)

        # Extract entities with context history awareness
        entities = self.entity_extractor.extract(user_input, self.context_manager)
        self.context_manager.update_entities(entities)

        # Classify intent (checking rule-based and contextual logic)
        intent = self.intent_classifier.classify_rule_based(user_input, self.context_manager)
        confidence = 0.95

        # ML Model prediction fallback
        if intent == "custom_instruction":
            tokens = self.tokenize(user_input)
            input_batch = [self.pad_sequence(tokens)]
            intent_probs, _ = self.model.predict(input_batch, verbose=0)
            intent_idx = int(max(range(len(intent_probs[0])), key=lambda i: intent_probs[0][i]))
            predicted_intent = self.intent_classifier.intents[intent_idx]
            ml_conf = float(intent_probs[0][intent_idx])
            if ml_conf > 0.6:
                intent = predicted_intent
                confidence = ml_conf

        # Execute memory persistence logic
        memory_result = None
        if intent == "memory_store" and entities.get("memory_key") and entities.get("memory_val"):
            self.context_manager.store_user_fact(entities["memory_key"], entities["memory_val"])
            memory_result = f"I've remembered that your {entities['memory_key']} is {entities['memory_val']}."
        elif intent == "memory_search":
            key = entities.get("memory_key")
            if key:
                val = self.context_manager.get_user_fact(key)
                if val:
                    memory_result = f"Your {key} is {val}."
                else:
                    facts = self.context_manager.search_user_fact(key)
                    if facts:
                        fact_strs = [f"{k}: {v}" for k, v in facts.items()]
                        memory_result = f"Here is what I remember: {', '.join(fact_strs)}"
                    else:
                        memory_result = f"I don't have a stored record for your {key} yet."
            else:
                summary = self.context_manager.get_context_summary()
                memory_result = f"I am currently tracking {summary['stored_facts_count']} user facts in memory."

        # Create action plan
        action_plan = self.action_planner.create_plan(intent, entities, {"raw_input": user_input})

        # Context bundle for response generator
        context_bundle = {
            "memory_result": memory_result,
            "recent_context": self.context_manager.get_recent_context(3),
            "user_facts": self.context_manager.user_memory,
            "sentiment": entities.get("sentiment", "neutral")
        }

        # Generate adaptive response
        response = self.response_generator.generate(intent, entities, action_plan, context_bundle)

        # Check confirmation requirement
        requires_confirmation = self._needs_confirmation(intent, entities)

        # Update context memory with response
        self.context_manager.add_assistant_message(response)

        processing_time = time.time() - start_time
        logger.info(f"Adaptive processing completed in {processing_time:.3f}s (Intent: {intent})")

        return IntentResult(
            intent=intent,
            confidence=confidence,
            entities=entities,
            action_plan=action_plan,
            response=response,
            requires_confirmation=requires_confirmation
        )

    def _needs_confirmation(self, intent: str, entities: Dict) -> bool:
        """Determine if user confirmation is required."""
        sensitive_intents = [
            "message_send", "message_reply", "call_make", "app_close",
            "security_audit", "word_process", "app_send_message"
        ]
        return intent in sensitive_intents and not entities.get("apps")

    def chat(self, message: str) -> str:
        """Simple chat interface."""
        result = self.process_input(message)
        return result.response

    def save_model(self, path: Optional[str] = None):
        """Save model weights."""
        save_path = path or self.model_path
        self.model.save_weights(f"{save_path}/weights.h5")

    def load_model(self, path: Optional[str] = None):
        """Load model weights."""
        from pathlib import Path
        load_path = path or self.model_path
        weights_file = f"{load_path}/weights.h5"
        if Path(weights_file).exists():
            self.model.load_weights(weights_file)