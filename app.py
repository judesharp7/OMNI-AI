#!/usr/bin/env python3
"""
app.py — OMNI-AI primary entry point.

Starts the Flask web server with the AI brain attached.
Open http://localhost:5000 in your browser after launching.

Usage:
    python app.py            # starts on port 5000
    python app.py --port 8080
    python app.py --no-browser
"""
import importlib.util
import sys
import logging
import argparse
import threading
import webbrowser
from datetime import datetime, timezone
from pathlib import Path
from flask import Flask, jsonify, request, send_file, send_from_directory

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(name)-20s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("omni-ai")

# Bootstrap AI brain
# ---------------------------------------------------------------------------
def _build_brain():
    """Instantiate JarvisCore with graceful fallback on import error."""
    try:
        from main import create_omnisystem
        jarvis = create_omnisystem()
        logger.info("✓ AI brain initialised (JarvisCore)")
        return jarvis
    except Exception as exc:
        logger.warning("⚠ AI brain unavailable (%s) — running in mock mode", exc)
        return None


# ---------------------------------------------------------------------------
# Flask app factory
# ---------------------------------------------------------------------------
def create_app(brain=None) -> Flask:
    """Return a configured Flask application.

    Parameters
    ----------
    brain:
        A JarvisCore instance (or None for mock mode).
    """
    ui_dir = Path(__file__).parent / "ui"

    app = Flask(__name__, static_folder=str(ui_dir), template_folder=str(ui_dir))
    app.config["MAX_CONTENT_LENGTH"] = 16 * 1024
    app.config["DEBUG"] = False
    app.config["OMNI_HOST"] = "127.0.0.1"

    # Attach the brain to the app so routes can access it via current_app
    app.config["BRAIN"] = brain
    try:
        from security.encryption import EncryptionManager, PasswordHasher

        app.config["ENCRYPTION_MANAGER"] = EncryptionManager()
        app.config["PASSWORD_HASHER"] = PasswordHasher()
    except ImportError:
        logger.exception("Security dependencies are unavailable")
        app.config["ENCRYPTION_MANAGER"] = None
        app.config["PASSWORD_HASHER"] = None

    def timestamp():
        return datetime.now(timezone.utc).isoformat()

    def json_object():
        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            return None, (jsonify({"success": False, "error": "A JSON object is required"}), 400)
        return data, None

    # ------------------------------------------------------------------
    # Static UI routes
    # ------------------------------------------------------------------

    @app.route("/")
    def index():
        return send_file(ui_dir / "index.html")

    @app.route("/styles.css")
    def styles():
        return send_from_directory(str(ui_dir), "styles.css", mimetype="text/css")

    @app.route("/script.js")
    def script():
        return send_from_directory(str(ui_dir), "script.js", mimetype="application/javascript")

    # ------------------------------------------------------------------
    # Core chat endpoint  ← the new wired-up route
    # ------------------------------------------------------------------

    @app.route("/api/chat", methods=["POST"])
    def chat():
        """Send a message to the AI brain and get a response."""
        data, error = json_object()
        if error:
            return error

        message = data.get("message")
        if not isinstance(message, str):
            return jsonify({"success": False, "error": "Message must be a string"}), 400
        message = message.strip()

        if not message:
            return jsonify({"success": False, "error": "No message provided"}), 400
        if len(message) > 4000:
            return jsonify({"success": False, "error": "Message must be 4000 characters or fewer"}), 400

        active_brain = app.config.get("BRAIN")
        intent_info = {}
        if active_brain:
            try:
                if hasattr(active_brain, "chat_detailed"):
                    detailed = active_brain.chat_detailed(message)
                    response_text = detailed["response"]
                    intent_info = {
                        "intent": detailed.get("intent"),
                        "confidence": detailed.get("confidence"),
                        "entities": detailed.get("entities"),
                        "action_plan": detailed.get("action_plan")
                    }
                else:
                    response_text = active_brain.chat(message)
            except Exception as exc:
                logger.exception("Brain.chat() failed")
                return jsonify({
                    "success": False,
                    "error": "The assistant could not process your request",
                }), 502
        else:
            response_text = (
                f"[Mock] You said: '{message}'. "
                "Install optional dependencies to enable the full AI brain."
            )

        payload = {
            "success": True,
            "message": message,
            "response": response_text,
            "timestamp": timestamp(),
        }
        if intent_info:
            payload["details"] = intent_info

        return jsonify(payload)


    # ------------------------------------------------------------------
    # System status
    # ------------------------------------------------------------------

    @app.route("/api/status", methods=["GET"])
    def status():
        active_brain = app.config.get("BRAIN")
        return jsonify({
            "success": True,
            "brain_available": active_brain is not None,
            "timestamp": datetime.now().isoformat(),
        })

    @app.route("/api/health", methods=["GET"])
    def health():
        try:
            import psutil
            cpu_usage = psutil.cpu_percent(interval=0.1)
            memory_usage = psutil.virtual_memory().percent
            disk_root = Path.cwd().anchor or str(Path.cwd())
            disk_usage = psutil.disk_usage(disk_root).percent
            usage = max(cpu_usage, memory_usage, disk_usage)
            return jsonify({
                "success": True,
                "data": {
                    "overall_status": "critical" if usage >= 95 else "degraded" if usage >= 80 else "good",
                    "cpu_usage": cpu_usage,
                    "memory_usage": memory_usage,
                    "disk_usage": disk_usage,
                    "timestamp": timestamp(),
                }
            })
        except ImportError:
            return jsonify({"success": False, "error": "System monitoring is unavailable"}), 503
        except Exception:
            logger.exception("System health check failed")
            return jsonify({"success": False, "error": "System health could not be collected"}), 503

    @app.route("/api/monitor", methods=["GET"])
    def monitor():
        try:
            import psutil

            processes = []
            process_count = 0
            for process in psutil.process_iter(["pid", "name", "memory_percent"]):
                process_count += 1
                try:
                    info = process.info
                    processes.append({
                        "pid": info["pid"],
                        "name": info["name"] or "Unknown",
                        "memory_percent": info["memory_percent"] or 0,
                    })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            processes.sort(key=lambda item: item["memory_percent"], reverse=True)
            return jsonify({
                "success": True,
                "data": {
                    "process_count": process_count,
                    "processes": processes[:5],
                    "uptime_seconds": max(0, int(datetime.now().timestamp() - psutil.boot_time())),
                },
                "timestamp": timestamp(),
            })
        except ImportError:
            return jsonify({"success": False, "error": "System monitoring is unavailable"}), 503
        except Exception:
            logger.exception("System monitor request failed")
            return jsonify({"success": False, "error": "System monitoring data could not be collected"}), 503

    @app.route("/api/capabilities", methods=["GET"])
    def capabilities():
        caps: dict = {}
        for lib, key in [
            ("torch", "pytorch"),
            ("tensorflow", "tensorflow"),
            ("speech_recognition", "speech_recognition"),
            ("pyttsx3", "text_to_speech"),
            ("cryptography", "encryption"),
            ("psutil", "system_monitoring"),
        ]:
            caps[key] = importlib.util.find_spec(lib) is not None
        return jsonify({"success": True, "data": caps, "timestamp": timestamp()})

    @app.route("/api/encrypt", methods=["POST"])
    def encrypt():
        data, error = json_object()
        if error:
            return error

        text = data.get("text")
        if not isinstance(text, str) or not text:
            return jsonify({"success": False, "error": "Text must be a non-empty string"}), 400
        if len(text) > 8000:
            return jsonify({"success": False, "error": "Text must be 8000 characters or fewer"}), 400

        manager = app.config.get("ENCRYPTION_MANAGER")
        if manager is None or manager.cipher is None:
            return jsonify({"success": False, "error": "Encryption is unavailable"}), 503

        encrypted = manager.encrypt_data(text)
        if encrypted is None:
            logger.error("Encryption manager returned no ciphertext")
            return jsonify({"success": False, "error": "Encryption failed"}), 500
        return jsonify({
            "success": True,
            "data": {
                "encrypted": encrypted.decode("ascii"),
                "key": manager.key.decode("ascii"),
                "algorithm": "Fernet",
                "key_warning": "Store the key separately. Anyone with the key can decrypt this value.",
            },
            "timestamp": timestamp(),
        })

    @app.route("/api/hash", methods=["POST"])
    def hash_password():
        data, error = json_object()
        if error:
            return error

        password = data.get("password")
        if not isinstance(password, str) or not password:
            return jsonify({"success": False, "error": "Password must be a non-empty string"}), 400
        if len(password) > 1024:
            return jsonify({"success": False, "error": "Password must be 1024 characters or fewer"}), 400

        hasher = app.config.get("PASSWORD_HASHER")
        if hasher is None:
            return jsonify({"success": False, "error": "Password hashing is unavailable"}), 503
        hash_value, salt = hasher.hash_password(password)
        if not hash_value or not salt:
            logger.error("Password hasher returned an empty result")
            return jsonify({"success": False, "error": "Password hashing failed"}), 500
        return jsonify({
            "success": True,
            "data": {
                "hash": hash_value,
                "salt": salt,
                "algorithm": "PBKDF2-HMAC-SHA256",
                "iterations": hasher.iterations,
            },
            "timestamp": timestamp(),
        })

    @app.route("/api/audit", methods=["POST"])
    def security_audit():
        debug_enabled = app.config.get("DEBUG", app.debug)
        crypto_available = importlib.util.find_spec("cryptography") is not None
        monitoring_available = importlib.util.find_spec("psutil") is not None
        checks = [
            {
                "name": "Debug mode disabled",
                "status": "passed" if not debug_enabled else "warning",
                "detail": "Debug mode is disabled" if not debug_enabled else "Debug mode is enabled",
            },
            {
                "name": "Loopback-only binding",
                "status": "passed" if app.config["OMNI_HOST"] in {"127.0.0.1", "localhost", "::1"} else "warning",
                "detail": f"Server host: {app.config['OMNI_HOST']}",
            },
            {
                "name": "Encryption dependency",
                "status": "passed" if crypto_available else "warning",
                "detail": "Cryptography package is installed" if crypto_available else "Cryptography package is missing",
            },
            {
                "name": "System monitoring dependency",
                "status": "passed" if monitoring_available else "warning",
                "detail": "psutil package is installed" if monitoring_available else "psutil package is missing",
            },
        ]
        return jsonify({
            "success": True,
            "data": {
                "status": "passed" if all(check["status"] == "passed" for check in checks) else "warning",
                "checks_passed": sum(check["status"] == "passed" for check in checks),
                "checks": checks,
                "scope": "Local application configuration checks only; this is not a malware or vulnerability scan.",
            },
            "timestamp": timestamp(),
        })

    # ------------------------------------------------------------------
    # Error handlers
    # ------------------------------------------------------------------

    @app.errorhandler(404)
    def not_found(_err):
        return jsonify({"success": False, "error": "Not found", "path": request.path}), 404

    @app.errorhandler(500)
    def server_error(err):
        logger.error("500: %s", err)
        return jsonify({"success": False, "error": "Internal server error"}), 500

    @app.errorhandler(413)
    def request_too_large(_err):
        return jsonify({"success": False, "error": "Request body is too large"}), 413

    return app


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="OMNI-AI Web App")
    parser.add_argument("--port", type=int, default=5000, help="Port to listen on (default: 5000)")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind (default: 127.0.0.1)")
    parser.add_argument("--no-browser", action="store_true", help="Don't open browser automatically")
    parser.add_argument("--debug", action="store_true", help="Enable Flask debug mode")
    args = parser.parse_args()

    brain = _build_brain()
    app = create_app(brain)
    app.config["OMNI_HOST"] = args.host
    app.config["DEBUG"] = args.debug
    app.debug = args.debug

    url = f"http://{args.host}:{args.port}"

    logger.info("=" * 60)
    logger.info("  OMNI-AI  —  Intelligent Cross-Platform Assistant")
    logger.info("=" * 60)
    logger.info("  URL   : %s", url)
    logger.info("  Brain : %s", "Ready" if brain else "Mock mode (see requirements-optional.txt)")
    logger.info("  Press Ctrl+C to stop")
    logger.info("=" * 60)

    if not args.no_browser:
        # Open browser half a second after server starts
        threading.Timer(0.5, lambda: webbrowser.open(url)).start()

    app.run(host=args.host, port=args.port, debug=args.debug, use_reloader=False)


if __name__ == "__main__":
    main()
