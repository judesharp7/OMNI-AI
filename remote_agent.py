"""
OMNI-AI Remote Agent
Run this lightweight script on other computers (Windows/Linux/Mac) 
so the main OMNI-AI host can monitor and control them over the local network.

Requires: pip install flask psutil
Usage: python remote_agent.py --port 5050
"""

import os
import argparse
import logging
from datetime import datetime
from flask import Flask, jsonify, request

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

app = Flask(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('RemoteAgent')

@app.route('/api/health', methods=['GET'])
def health_check():
    """Returns system health metrics."""
    if not PSUTIL_AVAILABLE:
        return jsonify({"success": False, "error": "psutil not installed"}), 500

    mem = psutil.virtual_memory()
    return jsonify({
        "success": True,
        "timestamp": datetime.now().isoformat(),
        "data": {
            "cpu_usage": psutil.cpu_percent(interval=0.5),
            "memory_usage": mem.percent,
            "memory_available_mb": mem.available / (1024 * 1024),
            "os": os.name
        }
    })

@app.route('/api/execute', methods=['POST'])
def execute_command():
    """Executes a system instruction (use with caution)."""
    data = request.json or {}
    instruction = data.get('instruction', '').lower()
    
    if not instruction:
        return jsonify({"success": False, "error": "No instruction provided"}), 400

    logger.info(f"Received instruction: {instruction}")
    response_msg = "Unknown command"
    
    # Basic safe commands for demonstration
    if 'beep' in instruction:
        # Very basic feedback mechanism
        response_msg = "Beep command received (simulated)."
    elif 'lock' in instruction:
        # Example of cross-platform lock
        if os.name == 'nt':
            os.system('rundll32.exe user32.dll,LockWorkStation')
            response_msg = "Workstation locked."
        else:
            response_msg = "Lock not implemented for this OS."
    elif 'echo' in instruction:
        response_msg = f"Echo: {instruction.replace('echo ', '')}"
    else:
        response_msg = f"Instruction '{instruction}' not supported remotely."

    return jsonify({
        "success": True,
        "message": response_msg,
        "timestamp": datetime.now().isoformat()
    })

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="OMNI-AI Remote Agent")
    parser.add_argument('--port', type=int, default=5050, help="Port to run on")
    parser.add_argument('--host', type=str, default='0.0.0.0', help="Host interface")
    args = parser.parse_args()

    logger.info(f"Starting Remote Agent on {args.host}:{args.port}")
    if not PSUTIL_AVAILABLE:
        logger.warning("psutil is not installed. /api/health will fail.")
    
    app.run(host=args.host, port=args.port, debug=False)
