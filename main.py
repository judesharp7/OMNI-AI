#!/usr/bin/env python3
"""
OmniAI - Intelligent Cross-Platform Assistant
Refactored using SOLID principles for maintainability and efficiency.

Architecture:
- Single Responsibility: Each class has one job
- Open/Closed: Classes are open for extension, closed for modification
- Liskov Substitution: Subtypes are substitutable for base types
- Interface Segregation: Clients depend only on methods they use
- Dependency Inversion: High-level modules don't depend on low-level modules
"""

import sys
import logging
from typing import Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import refactored modules
from core import OmniBrain
from hardware import HardwareController, PermissionManager
from platforms import AppController
from security import SecurityAuditor
from voice import VoiceEngine

class ActionExecutor:
    """
    Executes actions from the brain's action plan.
    Single responsibility: coordinate action execution.
    """

    def __init__(self, hardware: HardwareController, apps: AppController,
                 auditor: SecurityAuditor):
        self.hardware = hardware
        self.apps = apps
        self.auditor = auditor

    def execute_plan(self, action_plan: list) -> list:
        """Execute all actions in the plan."""
        results = []

        for item in action_plan:
            action = item.get("action")
            result = self._execute_action(action, item)
            results.append(result)

        return results

    def _execute_action(self, action: str, params: dict) -> str:
        """Execute a single action."""
        try:
            if action == "fetch_messages":
                return f"Fetched messages from {params.get('platform', 'unknown')} (mock)"

            elif action == "send_message":
                return self.apps.send_message(
                    params.get("platform", "whatsapp"),
                    params.get("contact", "unknown"),
                    params.get("message", "")
                )

            elif action == "control_hardware":
                hw = params.get("hardware")
                op = params.get("operation", {})
                return self._execute_hardware_action(hw, op)

            elif action == "remote_control":
                return self.hardware.remote_control(
                    params.get("ip", "127.0.0.1"), 
                    params.get("command", "")
                )

            elif action == "microcontroller_control":
                return self.hardware.microcontroller_control(
                    params.get("port", "COM3"), 
                    params.get("command", "")
                )

            elif action == "launch_app":
                return self.apps.open_app(params.get("app_name", "unknown"))

            elif action == "close_app":
                return self.apps.close_app(params.get("app_name", "unknown"))

            elif action == "word_process":
                return f"Composed document: {params.get('text', '')} (mock)"

            elif action == "security_audit":
                return self.auditor.run_audit()

            elif action == "execute_command":
                return self._execute_system_command(params.get("command", ""))

            elif action in ["store_memory", "search_memory", "system_status"]:
                return ""

            elif action == "custom_instruction":
                return f"Processed custom instruction: {params.get('instruction', '')}"

            else:
                return f"Unknown action: {action}"

        except Exception as e:
            logger.error(f"Action execution error: {e}")
            return f"Action failed: {e}"

    def _execute_hardware_action(self, hardware: str, operation: dict) -> str:
        """Execute hardware-specific actions."""
        if hardware == "flashlight":
            state = operation.get("state")
            if operation.get("error"):
                return operation["error"]
            return self.hardware.flashlight(state)

        elif hardware == "camera":
            return self.hardware.camera(operation.get("state", "capture"))

        elif hardware == "volume":
            return self.hardware.volume(operation.get("level", 50))

        elif hardware == "brightness":
            return self.hardware.brightness(operation.get("level", 50))

        elif hardware == "memory":
            return self.hardware.memory_scan()

        return f"Unknown hardware action: {hardware}"

    def _execute_system_command(self, command: str) -> str:
        """Execute system command with safety checks."""
        import subprocess

        command = command.replace("command:", "").replace("Command:", "").strip()
        safe_commands = ["dir", "ls", "echo", "date", "time", "whoami"]

        cmd_lower = command.lower().strip()
        base_cmd = cmd_lower.split()[0] if cmd_lower else ""

        if base_cmd in safe_commands or "calc" in cmd_lower or "notepad" in cmd_lower:
            try:
                result = subprocess.run(command, shell=True, capture_output=True,
                                      text=True, timeout=10)
                output = result.stdout.strip() or result.stderr.strip()
                return f"Executed: {output[:200]}..." if len(output) > 200 else f"Executed: {output}"
            except Exception as e:
                return f"Command failed: {str(e)}"
        else:
            return f"Command not allowed: {command}"

class JarvisCore:
    """
    High-level orchestrator using dependency injection.
    Follows Single Responsibility and Dependency Inversion principles.
    """

    def __init__(self, brain: OmniBrain, executor: ActionExecutor, voice: VoiceEngine):
        self.brain = brain
        self.executor = executor
        self.voice = voice
        self.running = False

    def wake(self) -> None:
        """Start the assistant."""
        self.running = True
        logger.info("Jarvis protocol engaged")
        self.voice.start_voice_control(self.execute_voice_command)

    def sleep(self) -> None:
        """Stop the assistant."""
        self.running = False
        self.voice.stop_voice_control()
        logger.info("Jarvis standing down")

    def execute_voice_command(self, command: str) -> str:
        """Process voice command."""
        if not command or command.strip() == "":
            return "No command provided."

        logger.info(f"Received command: {command}")

        # Process through brain
        result = self.brain.process_input(command)

        # Execute actions
        if result.action_plan:
            action_results = self.executor.execute_plan(result.action_plan)
            result.response += " " + " ".join(action_results)

        return result.response

    def chat(self, message: str) -> str:
        """Text-based chat interface."""
        detailed = self.chat_detailed(message)
        return detailed["response"]

    def chat_detailed(self, message: str) -> dict:
        """Text-based chat interface returning detailed execution result."""
        result = self.brain.process_input(message)
        action_outputs = []
        if result.action_plan:
            action_outputs = self.executor.execute_plan(result.action_plan)
            # Append non-empty action execution results if needed
            valid_outputs = [out for out in action_outputs if out and not result.response.endswith(out)]
            if valid_outputs:
                result.response = (result.response + " " + " ".join(valid_outputs)).strip()
        
        return {
            "response": result.response,
            "intent": result.intent,
            "confidence": result.confidence,
            "entities": result.entities,
            "action_plan": result.action_plan,
            "action_outputs": action_outputs,
            "requires_confirmation": result.requires_confirmation
        }


def create_omnisystem() -> JarvisCore:
    """
    Factory function to create the complete system.
    Demonstrates Dependency Injection.
    """
    # Create permissions
    permissions = PermissionManager()

    # Create controllers
    hardware = HardwareController(permissions)
    apps = AppController(permissions)
    auditor = SecurityAuditor(permissions)

    # Create brain
    brain = OmniBrain()

    # Create executor
    executor = ActionExecutor(hardware, apps, auditor)

    # Create voice engine
    voice = VoiceEngine()

    # Create core system
    jarvis = JarvisCore(brain, executor, voice)

    return jarvis

def main():
    """Main entry point."""
    try:
        # Create the system
        jarvis = create_omnisystem()

        if len(sys.argv) > 1:
            # Command line mode
            command = " ".join(sys.argv[1:])
            response = jarvis.chat(command)
            print(f"OmniAI: {response}")
        else:
            # Interactive mode
            print("OmniAI activated. Type 'quit' to exit.")
            while True:
                try:
                    user_input = input("You: ").strip()
                    if user_input.lower() in ['quit', 'exit', 'bye']:
                        break
                    response = jarvis.chat(user_input)
                    print(f"OmniAI: {response}")
                except KeyboardInterrupt:
                    break
            print("OmniAI deactivated.")

    except Exception as e:
        logger.error(f"System error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()