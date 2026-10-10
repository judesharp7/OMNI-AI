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
import pandas as pd
import sys
import logging
import argparse
import threading
import webbrowser
from datetime import datetime
from pathlib import Path
from flask import Flask, jsonify, request, send_file, send_from_directory
from flask_cors import CORS

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(name)-20s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("omni-ai")

#---------------------------------------------------------------------------
# training model
# ---------------------------------------------------------------------------
from sklearn.ensemble import IsolationForest
# this is not saved on pc its an online dataset

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
    CORS(app)

    # Attach the brain to the app so routes can access it via current_app
    app.config["BRAIN"] = brain

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
        data = request.get_json(silent=True) or {}
        message = (data.get("message") or "").strip()

        if not message:
            return jsonify({"success": False, "error": "No message provided"}), 400

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
                logger.error("Brain.chat() error: %s", exc)
                response_text = "I encountered an error processing your request."
        else:
            response_text = (
                f"[Mock] You said: '{message}'. "
                "Install optional dependencies to enable the full AI brain."
            )

        payload = {
            "success": True,
            "message": message,
            "response": response_text,
            "timestamp": datetime.now().isoformat(),
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
            return jsonify({
                "success": True,
                "data": {
                    "overall_status": "good",
                    "cpu_usage": psutil.cpu_percent(interval=0.1),
                    "memory_usage": psutil.virtual_memory().percent,
                    "disk_usage": psutil.disk_usage("/").percent,
                    "timestamp": datetime.now().isoformat(),
                }
            })
        except ImportError:
            return jsonify({
                "success": True,
                "data": {
                    "overall_status": "unknown",
                    "note": "psutil not installed",
                    "timestamp": datetime.now().isoformat(),
                }
            })

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
            try:
                __import__(lib)
                caps[key] = True
            except ImportError:
                caps[key] = False
        return jsonify({"success": True, "data": caps, "timestamp": datetime.now().isoformat()})

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
