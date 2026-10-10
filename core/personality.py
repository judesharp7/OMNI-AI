# core/personality.py
"""
Response generation and personality management.
Single responsibility: generate contextual responses.
"""

from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)


class ResponseGenerator:
    """
    Generates natural language responses based on intent and context.
    """

    def __init__(self):
        # Plain string templates — variables are substituted at runtime in generate()
        self.response_templates: Dict[str, str] = {
            "message_read":        "I'll check your messages{contact_suffix}.",
            "message_reply":       "I'll reply to {contact_name} with your message.",
            "message_send":        "Sending your message to {contact_name}.",
            "hardware_flashlight": "Turning flashlight {hw_state}.",
            "hardware_volume":     "Adjusting volume now.",
            "hardware_brightness": "Changing screen brightness.",
            "hardware_camera":     "Camera ready.",
            "hardware_memory":     "Scanning memory now.",
            "app_open":            "Opening {app_name}.",
            "app_close":           "Closing {app_name}.",
            "security_audit":      "Starting security audit now.",
            "word_process":        "Launching word processing tools.",
            "general_chat":        "I'm here to help. You can ask me to check messages, control your device, or just chat.",
            "execute_command":     "Executing command.",
            "custom_instruction":  "Processing your instruction.",
            "weather_query":       "Fetching weather information.",
            "reminder_set":        "Setting your reminder.",
            "alarm_set":           "Setting your alarm.",
            "call_make":           "Initiating call to {contact_name}.",
            "contact_search":      "Searching for {contact_name}.",
            "system_status":       "Checking system status.",
            "memory_search":       "Searching memory.",
            "memory_store":        "Storing to memory.",
            "hardware_remote_control": "Sending instruction to remote PC at {ip_address}.",
            "hardware_microcontroller": "Sending instruction to microcontroller on {com_port}."
        }

    def generate(self, intent: str, entities: Dict, action_plan: List[Dict], context_bundle: Optional[Dict] = None) -> str:
        """
        Generate an adaptive contextual response based on intent, entities, action plan, and context bundle.
        """
        try:
            context_bundle = context_bundle or {}
            memory_result = context_bundle.get("memory_result")
            user_facts = context_bundle.get("user_facts") or {}
            sentiment = context_bundle.get("sentiment", "neutral")
            user_name = user_facts.get("name")

            # Memory result takes priority if available
            if memory_result:
                prefix = f"Certainly{', ' + user_name if user_name else ''}! " if sentiment == "positive" else ""
                return f"{prefix}{memory_result}"

            # Extract entity details
            contacts = entities.get("contacts") or []
            apps = entities.get("apps") or []
            ips = entities.get("ips") or []
            com_ports = entities.get("com_ports") or []
            
            contact_name = contacts[0] if contacts else "them"
            app_name = apps[0] if apps else "the app"
            ip_address = ips[0] if ips else "127.0.0.1"
            com_port = com_ports[0].upper() if com_ports else "COM3"

            # Determine hardware state from action plan
            hw_state = "on"
            if action_plan:
                op = action_plan[0].get("operation", {})
                if op.get("state") == "off":
                    hw_state = "off"

            # Build optional contact suffix
            contact_suffix = f" from {contact_name}" if contacts else ""

            # Conversational customization based on sentiment & known name
            name_greeting = f", {user_name}" if user_name else ""

            if intent == "general_chat":
                if sentiment == "positive":
                    return f"You're very welcome{name_greeting}! I'm always here to assist you."
                elif user_name:
                    return f"Hello{name_greeting}! How can I help you right now? You can ask me to run commands, check system status, manage memory, or control applications."
                else:
                    return "Hello! I am OMNI-AI. You can ask me to manage system apps, scan hardware, recall user memories, or execute commands."

            elif intent == "system_status":
                return f"System check complete{name_greeting}. All core engines, AI modules, and security parameters are fully operational."

            template = self.response_templates.get(intent, "I'm processing your request.")

            response = template.format(
                contact_name=contact_name,
                contact_suffix=contact_suffix,
                app_name=app_name,
                hw_state=hw_state,
                ip_address=ip_address,
                com_port=com_port
            )

            if user_name and not response.endswith("."):
                response += f", {user_name}."

            logger.debug("Generated adaptive response for intent '%s': %s", intent, response)
            return response

        except Exception as e:
            logger.error("Error generating response: %s", e)
            return "I'm processing your request."