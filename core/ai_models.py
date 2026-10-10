# core/ai_models.py
"""
Advanced AI Models using TensorFlow and PyTorch.
Provides intent classification, entity extraction, and response generation.
"""

import logging
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
import json

# TensorFlow imports
try:
    import tensorflow as tf
    from tensorflow import keras
    from tensorflow.keras import layers, models
    TENSORFLOW_AVAILABLE = True
except ImportError:
    tf = None
    keras = None
    layers = None
    models = None
    TENSORFLOW_AVAILABLE = False

# PyTorch imports
try:
    import torch
    import torch.nn as nn
    PYTORCH_AVAILABLE = True
except ImportError:
    torch = None
    nn = None
    PYTORCH_AVAILABLE = False

# NumPy
try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    np = None
    NUMPY_AVAILABLE = False

logger = logging.getLogger(__name__)

class TensorFlowIntentModel:
    """TensorFlow-based intent classification model."""

    def __init__(self, n_intents: int = 10, vocab_size: int = 5000, embedding_dim: int = 128):
        """
        Initialize TensorFlow intent model.
        
        Args:
            n_intents: Number of intent classes
            vocab_size: Size of vocabulary
            embedding_dim: Embedding dimension
        """
        if not TENSORFLOW_AVAILABLE:
            logger.warning("TensorFlow not available - using mock model")
            self.model = None
            return

        self.n_intents = n_intents
        self.vocab_size = vocab_size
        self.embedding_dim = embedding_dim
        self.max_sequence_length = 20
        
        self.model = self._build_model()
        logger.info(f"TensorFlow Intent Model created with {n_intents} intents")

    def _build_model(self):
        """Build the neural network model."""
        if not TENSORFLOW_AVAILABLE:
            return None

        model = models.Sequential([
            layers.Embedding(self.vocab_size, self.embedding_dim, 
                           input_length=self.max_sequence_length),
            layers.Bidirectional(layers.LSTM(128, return_sequences=True)),
            layers.Attention(),
            layers.GlobalAveragePooling1D(),
            layers.Dense(256, activation='relu', kernel_regularizer=keras.regularizers.l2(0.001)),
            layers.Dropout(0.3),
            layers.Dense(128, activation='relu'),
            layers.Dropout(0.2),
            layers.Dense(self.n_intents, activation='softmax')
        ])

        model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=0.001),
            loss='categorical_crossentropy',
            metrics=['accuracy']
        )

        logger.info("TensorFlow model compiled successfully")
        return model

    def predict_intent(self, tokens: List[int]) -> Tuple[str, float]:
        """
        Predict intent from tokenized input.
        
        Args:
            tokens: List of token IDs
            
        Returns:
            Tuple of (intent, confidence)
        """
        if not self.model or not TENSORFLOW_AVAILABLE:
            return "general", 0.5

        try:
            # Pad sequence
            padded = tf.keras.preprocessing.sequence.pad_sequences(
                [tokens], maxlen=self.max_sequence_length, padding='post'
            )
            
            # Predict
            prediction = self.model.predict(padded, verbose=0)
            intent_idx = np.argmax(prediction[0])
            confidence = float(prediction[0][intent_idx])
            
            intent_names = [f"intent_{i}" for i in range(self.n_intents)]
            return intent_names[intent_idx], confidence
            
        except Exception as e:
            logger.error(f"Intent prediction error: {e}")
            return "general", 0.5

    def train(self, X_train, y_train, epochs: int = 10, batch_size: int = 32):
        """Train the model."""
        if not self.model:
            logger.warning("Cannot train - model not available")
            return

        try:
            self.model.fit(X_train, y_train, epochs=epochs, batch_size=batch_size, verbose=0)
            logger.info(f"Model trained for {epochs} epochs")
        except Exception as e:
            logger.error(f"Training error: {e}")

    def save_model(self, path: str):
        """Save model to disk."""
        if self.model:
            self.model.save(path)
            logger.info(f"Model saved to {path}")

    def load_model(self, path: str):
        """Load model from disk."""
        if TENSORFLOW_AVAILABLE:
            self.model = keras.models.load_model(path)
            logger.info(f"Model loaded from {path}")


class TensorFlowEntityExtractor:
    """TensorFlow-based entity extraction model using Sequence Tagging."""

    def __init__(self, n_entities: int = 20, vocab_size: int = 5000):
        """Initialize entity extractor."""
        if not TENSORFLOW_AVAILABLE:
            logger.warning("TensorFlow not available")
            self.model = None
            return

        self.n_entities = n_entities
        self.vocab_size = vocab_size
        self.model = self._build_model()
        logger.info(f"TensorFlow Entity Extractor created for {n_entities} entity types")

    def _build_model(self):
        """Build sequence tagging model."""
        if not TENSORFLOW_AVAILABLE:
            return None

        model = models.Sequential([
            layers.Embedding(self.vocab_size, 128, input_length=20),
            layers.Bidirectional(layers.LSTM(256, return_sequences=True)),
            layers.Dropout(0.3),
            layers.Dense(128, activation='relu'),
            layers.Dropout(0.3),
            layers.Dense(self.n_entities, activation='softmax')
        ])

        model.compile(
            optimizer='adam',
            loss='categorical_crossentropy',
            metrics=['accuracy']
        )

        return model

    def extract_entities(self, tokens: List[int]) -> List[Dict[str, Any]]:
        """Extract entities from tokenized input."""
        if not self.model:
            return []

        try:
            predictions = self.model.predict(np.array([tokens]), verbose=0)
            entities = []
            
            for idx, pred in enumerate(predictions[0]):
                entity_type_idx = np.argmax(pred)
                confidence = float(pred[entity_type_idx])
                
                if confidence > 0.5:
                    entities.append({
                        'type': f'entity_{entity_type_idx}',
                        'position': idx,
                        'confidence': confidence
                    })
            
            return entities
            
        except Exception as e:
            logger.error(f"Entity extraction error: {e}")
            return []


class PyTorchAdvancedModel(nn.Module):
    """Advanced PyTorch model for complex NLP tasks."""

    def __init__(self, vocab_size: int = 5000, embedding_dim: int = 256, 
                 hidden_dim: int = 512, num_classes: int = 10):
        """Initialize PyTorch model."""
        super().__init__()

        if not PYTORCH_AVAILABLE:
            logger.warning("PyTorch not available")
            return

        self.embedding = nn.Embedding(vocab_size, embedding_dim)
        self.lstm = nn.LSTM(embedding_dim, hidden_dim, batch_first=True, bidirectional=True)
        self.attention = nn.MultiheadAttention(hidden_dim * 2, num_heads=8)
        self.fc1 = nn.Linear(hidden_dim * 2, 256)
        self.fc2 = nn.Linear(256, num_classes)
        self.dropout = nn.Dropout(0.3)
        self.relu = nn.ReLU()

        logger.info("PyTorch Advanced Model initialized")

    def forward(self, x):
        """Forward pass."""
        if not PYTORCH_AVAILABLE:
            return None

        # Embedding
        embedded = self.embedding(x)
        
        # LSTM
        lstm_out, (hidden, cell) = self.lstm(embedded)
        
        # Attention
        attn_out, _ = self.attention(lstm_out, lstm_out, lstm_out)
        
        # Fully connected
        fc_out = self.relu(self.fc1(attn_out[:, -1, :]))
        fc_out = self.dropout(fc_out)
        output = self.fc2(fc_out)
        
        return output

    def predict(self, x):
        """Make predictions."""
        if not PYTORCH_AVAILABLE:
            return None

        with torch.no_grad():
            output = self.forward(x)
            return output


class HybridAIModel:
    """Hybrid model combining TensorFlow and PyTorch capabilities."""

    def __init__(self):
        """Initialize hybrid model."""
        self.tf_intent_model = TensorFlowIntentModel() if TENSORFLOW_AVAILABLE else None
        self.tf_entity_model = TensorFlowEntityExtractor() if TENSORFLOW_AVAILABLE else None
        self.pytorch_model = None
        
        if PYTORCH_AVAILABLE:
            self.pytorch_model = PyTorchAdvancedModel()
        
        self.model_name = "HybridAIModel"
        self.creation_time = datetime.now()
        logger.info("Hybrid AI Model initialized")

    def get_model_info(self) -> Dict[str, Any]:
        """Get model information."""
        return {
            'model_name': self.model_name,
            'tensorflow_available': TENSORFLOW_AVAILABLE,
            'pytorch_available': PYTORCH_AVAILABLE,
            'creation_time': str(self.creation_time),
            'components': {
                'intent_classifier': bool(self.tf_intent_model),
                'entity_extractor': bool(self.tf_entity_model),
                'pytorch_model': bool(self.pytorch_model)
            }
        }

    def process_text(self, text: str) -> Dict[str, Any]:
        """Process text through all models."""
        # This would tokenize and process through all models
        return {
            'status': 'processed',
            'text': text,
            'timestamp': datetime.now().isoformat()
        }

    def save_all_models(self, directory: str):
        """Save all models to disk."""
        try:
            if self.tf_intent_model:
                self.tf_intent_model.save_model(f"{directory}/tf_intent_model")
            if self.pytorch_model and PYTORCH_AVAILABLE:
                torch.save(self.pytorch_model.state_dict(), f"{directory}/pytorch_model.pt")
            logger.info(f"All models saved to {directory}")
        except Exception as e:
            logger.error(f"Error saving models: {e}")

    def load_all_models(self, directory: str):
        """Load all models from disk."""
        try:
            if self.tf_intent_model:
                self.tf_intent_model.load_model(f"{directory}/tf_intent_model")
            if self.pytorch_model and PYTORCH_AVAILABLE:
                self.pytorch_model.load_state_dict(torch.load(f"{directory}/pytorch_model.pt"))
            logger.info(f"All models loaded from {directory}")
        except Exception as e:
            logger.error(f"Error loading models: {e}")


# Export main classes
__all__ = [
    'TensorFlowIntentModel',
    'TensorFlowEntityExtractor',
    'PyTorchAdvancedModel',
    'HybridAIModel',
    'TENSORFLOW_AVAILABLE',
    'PYTORCH_AVAILABLE',
    'NUMPY_AVAILABLE'
]
