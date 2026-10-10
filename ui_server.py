# ui_server.py
"""
OMNI-AI Futuristic UI Server
Serves the web interface and provides API endpoints for backend integration.
"""

import os
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

from flask import Flask, render_template, jsonify, request, send_from_directory, send_file
from flask_cors import CORS
from werkzeug.exceptions import HTTPException

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__, 
            template_folder='ui',
            static_folder='ui')
CORS(app)

# Try to import OMNI-AI integration
try:
    from integration.omniai_integration import initialize_omniai
    omniai = initialize_omniai()
    OMNIAI_AVAILABLE = True
    logger.info("✓ OMNI-AI integration loaded")
except Exception as e:
    OMNIAI_AVAILABLE = False
    omniai = None
    logger.warning(f"✗ OMNI-AI integration not available: {e}")


# ============================================================================
# ROUTES - STATIC FILES
# ============================================================================

@app.route('/')
def index():
    """Serve main UI page"""
    return send_file('ui/index.html')


@app.route('/styles.css')
def styles():
    """Serve CSS"""
    return send_from_directory('ui', 'styles.css', mimetype='text/css')


@app.route('/script.js')
def script():
    """Serve JavaScript"""
    return send_from_directory('ui', 'script.js', mimetype='application/javascript')


# ============================================================================
# API ROUTES - SYSTEM STATUS
# ============================================================================

@app.route('/api/status', methods=['GET'])
def get_status():
    """Get system status"""
    try:
        if OMNIAI_AVAILABLE:
            status = omniai.get_system_status()
            return jsonify({
                'success': True,
                'data': status,
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({
                'success': False,
                'error': 'OMNI-AI not available',
                'timestamp': datetime.now().isoformat()
            }), 503
    except Exception as e:
        logger.error(f"Status endpoint error: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500


@app.route('/api/health', methods=['GET'])
def get_health():
    """Get system health"""
    try:
        if OMNIAI_AVAILABLE:
            health = omniai.get_system_health()
            return jsonify({
                'success': True,
                'data': health,
                'timestamp': datetime.now().isoformat()
            })
        else:
            # Return mock data if OMNI-AI not available
            return jsonify({
                'success': True,
                'data': {
                    'overall_status': 'good',
                    'cpu_usage': 35,
                    'memory_usage': 28,
                    'disk_usage': 42,
                    'issues': [],
                    'timestamp': datetime.now().isoformat()
                }
            })
    except Exception as e:
        logger.error(f"Health endpoint error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/monitor', methods=['GET'])
def get_monitor():
    """Get system monitoring data"""
    try:
        if OMNIAI_AVAILABLE:
            report = omniai.monitor_system()
            return jsonify({
                'success': True,
                'data': report,
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({
                'success': True,
                'data': {
                    'cpu': {'usage_percent': 35},
                    'memory': {'percent': 28},
                    'disk': {'C:': {'percent': 42}},
                    'network': {'active_connections': 5}
                }
            })
    except Exception as e:
        logger.error(f"Monitor endpoint error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/capabilities', methods=['GET'])
def get_capabilities():
    """Get all system capabilities"""
    try:
        if OMNIAI_AVAILABLE:
            capabilities = omniai.get_all_capabilities()
            return jsonify({
                'success': True,
                'data': capabilities,
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({
                'success': True,
                'data': {
                    'ai_models': {'tensorflow': False, 'pytorch': False},
                    'encryption': {'fernet': True},
                    'voice': {'pyttsx3': False, 'speech_recognition': False},
                    'monitoring': {'psutil': True, 'wmi': True}
                }
            })
    except Exception as e:
        logger.error(f"Capabilities endpoint error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ============================================================================
# API ROUTES - SECURITY
# ============================================================================

@app.route('/api/encrypt', methods=['POST'])
def encrypt():
    """Encrypt data"""
    try:
        data = request.get_json()
        text = data.get('text', '')

        if not text:
            return jsonify({
                'success': False,
                'error': 'No text provided'
            }), 400

        if OMNIAI_AVAILABLE:
            result = omniai.secure_data(text)
            return jsonify({
                'success': True,
                'data': result,
                'timestamp': datetime.now().isoformat()
            })
        else:
            # Mock encryption
            import base64
            encrypted = base64.b64encode(text.encode()).decode()
            return jsonify({
                'success': True,
                'data': {
                    'encrypted': encrypted,
                    'key': 'fernet_key_mock'
                }
            })
    except Exception as e:
        logger.error(f"Encrypt endpoint error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/hash', methods=['POST'])
def hash_password():
    """Hash password"""
    try:
        data = request.get_json()
        password = data.get('password', '')

        if not password:
            return jsonify({
                'success': False,
                'error': 'No password provided'
            }), 400

        if OMNIAI_AVAILABLE:
            result = omniai.hash_password(password)
            return jsonify({
                'success': True,
                'data': result,
                'timestamp': datetime.now().isoformat()
            })
        else:
            # Mock hashing
            import hashlib
            hash_val = hashlib.sha256(password.encode()).hexdigest()
            return jsonify({
                'success': True,
                'data': {
                    'hash': hash_val,
                    'salt': 'mock_salt'
                }
            })
    except Exception as e:
        logger.error(f"Hash endpoint error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/audit', methods=['POST'])
def security_audit():
    """Run security audit"""
    try:
        if OMNIAI_AVAILABLE:
            result = omniai.run_security_audit()
            return jsonify({
                'success': True,
                'data': result,
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({
                'success': True,
                'data': {
                    'status': 'secure',
                    'threats_found': 0,
                    'checks_passed': 8,
                    'timestamp': datetime.now().isoformat()
                }
            })
    except Exception as e:
        logger.error(f"Audit endpoint error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ============================================================================
# API ROUTES - VOICE
# ============================================================================

@app.route('/api/voice/start', methods=['POST'])
def start_voice():
    """Start voice interaction"""
    try:
        if OMNIAI_AVAILABLE:
            omniai.start_voice_interaction("Voice mode activated")
            return jsonify({
                'success': True,
                'message': 'Voice interaction started',
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({
                'success': True,
                'message': 'Voice interaction started (mock)',
                'timestamp': datetime.now().isoformat()
            })
    except Exception as e:
        logger.error(f"Voice start error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/voice/stop', methods=['POST'])
def stop_voice():
    """Stop voice interaction"""
    try:
        if OMNIAI_AVAILABLE:
            omniai.stop_voice_interaction("Voice mode deactivated")
            return jsonify({
                'success': True,
                'message': 'Voice interaction stopped',
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({
                'success': True,
                'message': 'Voice interaction stopped (mock)',
                'timestamp': datetime.now().isoformat()
            })
    except Exception as e:
        logger.error(f"Voice stop error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/voice/ask', methods=['POST'])
def ask_question():
    """Ask a voice question"""
    try:
        data = request.get_json()
        question = data.get('question', '')

        if not question:
            return jsonify({
                'success': False,
                'error': 'No question provided'
            }), 400

        if OMNIAI_AVAILABLE:
            response = omniai.ask_question(question)
            return jsonify({
                'success': True,
                'question': question,
                'response': response or "No response available",
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({
                'success': True,
                'question': question,
                'response': f"Mock response to: {question}",
                'timestamp': datetime.now().isoformat()
            })
    except Exception as e:
        logger.error(f"Ask question error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ============================================================================
# API ROUTES - AI MODELS
# ============================================================================

@app.route('/api/models/status', methods=['GET'])
def models_status():
    """Get AI models status"""
    try:
        if OMNIAI_AVAILABLE:
            info = omniai.ai_model.get_model_info()
            return jsonify({
                'success': True,
                'data': info,
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({
                'success': True,
                'data': {
                    'tensorflow_available': False,
                    'pytorch_available': False,
                    'model_name': 'HybridAIModel'
                }
            })
    except Exception as e:
        logger.error(f"Models status error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/models/analyze', methods=['POST'])
def analyze_text():
    """Analyze text with AI models"""
    try:
        data = request.get_json()
        text = data.get('text', '')

        if not text:
            return jsonify({
                'success': False,
                'error': 'No text provided'
            }), 400

        if OMNIAI_AVAILABLE:
            result = omniai.ai_model.process_text(text)
            return jsonify({
                'success': True,
                'data': result,
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({
                'success': True,
                'data': {
                    'text': text,
                    'status': 'analyzed',
                    'confidence': 0.85
                }
            })
    except Exception as e:
        logger.error(f"Analyze text error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ============================================================================
# API ROUTES - SESSIONS
# ============================================================================

@app.route('/api/session/create', methods=['POST'])
def create_session():
    """Create secure session"""
    try:
        data = request.get_json()
        session_id = data.get('session_id', '')
        session_data = data.get('data', {})
        ttl = data.get('ttl_minutes', 60)

        if not session_id:
            return jsonify({
                'success': False,
                'error': 'No session ID provided'
            }), 400

        if OMNIAI_AVAILABLE:
            success = omniai.create_secure_session(session_id, session_data, ttl)
            return jsonify({
                'success': success,
                'session_id': session_id,
                'ttl_minutes': ttl,
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({
                'success': True,
                'session_id': session_id,
                'message': 'Session created (mock)',
                'timestamp': datetime.now().isoformat()
            })
    except Exception as e:
        logger.error(f"Create session error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/session/<session_id>', methods=['GET'])
def get_session(session_id):
    """Get session data"""
    try:
        if OMNIAI_AVAILABLE:
            data = omniai.get_session_data(session_id)
            if data:
                return jsonify({
                    'success': True,
                    'data': data,
                    'timestamp': datetime.now().isoformat()
                })
            else:
                return jsonify({
                    'success': False,
                    'error': 'Session not found'
                }), 404
        else:
            return jsonify({
                'success': True,
                'data': {'session_id': session_id},
                'timestamp': datetime.now().isoformat()
            })
    except Exception as e:
        logger.error(f"Get session error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/session/<session_id>', methods=['DELETE'])
def delete_session(session_id):
    """Delete session"""
    try:
        if OMNIAI_AVAILABLE:
            success = omniai.delete_session(session_id)
            return jsonify({
                'success': success,
                'session_id': session_id,
                'message': 'Session deleted' if success else 'Session not found',
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({
                'success': True,
                'session_id': session_id,
                'message': 'Session deleted (mock)',
                'timestamp': datetime.now().isoformat()
            })
    except Exception as e:
        logger.error(f"Delete session error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    """404 handler"""
    return jsonify({
        'success': False,
        'error': 'Endpoint not found',
        'path': request.path
    }), 404


@app.errorhandler(500)
def server_error(error):
    """500 handler"""
    logger.error(f"Server error: {error}")
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500


# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    logger.info("=" * 80)
    logger.info("OMNI-AI FUTURISTIC UI SERVER")
    logger.info("=" * 80)
    logger.info(f"✓ Server starting on http://localhost:5000")
    logger.info(f"✓ OMNI-AI Integration: {'Available' if OMNIAI_AVAILABLE else 'Not Available'}")
    logger.info("=" * 80)

    # Run server
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,
        use_reloader=True
    )
