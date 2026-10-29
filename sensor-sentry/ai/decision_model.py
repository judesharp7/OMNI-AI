"""
decision_model.py — Sensor AI Decision Model
=============================================
Multi-layer ML model for sensor fault classification and
autonomous decision making. Uses a lightweight approach:

  1. Gradient-Boosted Decision Tree (fast, interpretable) — primary
  2. Small feed-forward neural net (PyTorch) — when available
  3. Rule-based fallback — always available

The model outputs severity classification + confidence + remediation action.
"""

import json
import logging
import os
import pickle
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

logger = logging.getLogger(__name__)

MODEL_DIR = Path(__file__).resolve().parent / "models"

# ── Optional ML imports ──────────────────────────────────────────

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    np = None
    NUMPY_AVAILABLE = False

try:
    from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
    from sklearn.preprocessing import StandardScaler
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import classification_report, accuracy_score
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

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


# ── PyTorch Neural Net (lightweight) ─────────────────────────────

class SensorNet(nn.Module if TORCH_AVAILABLE else object):
    """Small feed-forward net for sensor anomaly classification."""

    def __init__(self, input_dim: int = 16, n_classes: int = 4):
        if not TORCH_AVAILABLE:
            raise ImportError("PyTorch required for SensorNet")
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, 128),
            nn.BatchNorm1d(128),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(128, 64),
            nn.BatchNorm1d(64),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Linear(32, n_classes),
        )

    def forward(self, x):
        return self.net(x)


# ── Rule-Based Fallback ─────────────────────────────────────────

class RuleBasedClassifier:
    """Fast rule-based classifier — always available, no dependencies."""

    def predict(self, features: List[float]) -> Tuple[int, float, str]:
        """
        Returns (severity, confidence, action_string).
        Features layout from training_data.extract_features():
          [0]=mean, [1]=std, [2]=z_score, [3]=p2p, [4]=rms,
          [5]=kurtosis, [6]=skew, [7]=crest, [8]=energy,
          [9]=crossing_rate, [10]=trend_slope, [11]=autocorr,
          [12]=diff_mean, [13]=diff_max, [14]=latest_val, [15]=window_size
        """
        if len(features) < 16:
            return (0, 0.5, "NOMINAL")

        z = abs(features[2])
        kurt = features[5]
        diff_max = features[13]
        std = features[1]
        trend = abs(features[10])

        score = 0
        if z >= 3.5:        score += 4
        elif z >= 3.0:      score += 3
        elif z >= 2.5:      score += 2
        elif z >= 2.0:      score += 1

        if kurt > 5.0:      score += 2
        elif kurt > 3.0:    score += 1

        if std > 0 and diff_max > std * 4:
            score += 2
        elif std > 0 and diff_max > std * 2:
            score += 1

        if trend > 0.1:     score += 1

        if score >= 7:
            return (3, 0.85, "EMERGENCY_SHUTDOWN_AND_REWRITE_FIRMWARE")
        elif score >= 4:
            return (2, 0.80, "ISOLATE_AND_INITIATE_DIAGNOSTIC")
        elif score >= 2:
            return (1, 0.70, "LOG_WARNING_AND_INCREASE_SAMPLING")
        else:
            return (0, 0.90, "NOMINAL")

    def predict_batch(self, feature_matrix: List[List[float]]
                      ) -> List[Tuple[int, float, str]]:
        return [self.predict(f) for f in feature_matrix]


# ── Main Decision Model (ensemble) ──────────────────────────────

class SensorDecisionModel:
    """
    Ensemble decision model that combines:
    1. Gradient-Boosted Trees (sklearn)  — fast, interpretable
    2. SensorNet (PyTorch)               — neural pattern recognition
    3. Rule-based fallback               — always available

    Each model votes; final decision uses weighted confidence.
    """

    SEVERITY_MAP = {0: "NOMINAL", 1: "WARNING", 2: "CRITICAL", 3: "EMERGENCY"}
    ACTION_MAP = {
        0: "NOMINAL",
        1: "LOG_WARNING_AND_INCREASE_SAMPLING",
        2: "ISOLATE_AND_INITIATE_DIAGNOSTIC",
        3: "EMERGENCY_SHUTDOWN_AND_REWRITE_FIRMWARE",
    }

    def __init__(self):
        self.rule_model = RuleBasedClassifier()
        self.gb_model = None    # GradientBoostingClassifier
        self.rf_model = None    # RandomForestClassifier
        self.scaler = None      # StandardScaler
        self.torch_model = None # SensorNet
        self.is_trained = False
        logger.info("SensorDecisionModel initialised (sklearn=%s, torch=%s)",
                     SKLEARN_AVAILABLE, TORCH_AVAILABLE)

    def train(self, X: List[List[float]], y: List[int],
              test_size: float = 0.2) -> Dict[str, Any]:
        """
        Train the ensemble model.
        Returns a report dict with accuracy metrics.
        """
        if not SKLEARN_AVAILABLE or not NUMPY_AVAILABLE:
            logger.warning("sklearn/numpy unavailable — using rule-based only")
            self.is_trained = False
            return {"status": "rule_based_only", "accuracy": None}

        X_arr = np.array(X, dtype=np.float32)
        y_arr = np.array(y, dtype=np.int32)

        # Split
        X_train, X_test, y_train, y_test = train_test_split(
            X_arr, y_arr, test_size=test_size, stratify=y_arr, random_state=42)

        # Normalise
        self.scaler = StandardScaler()
        X_train_s = self.scaler.fit_transform(X_train)
        X_test_s = self.scaler.transform(X_test)

        # ── Train Gradient Boosting ────────────────────────────
        t0 = time.time()
        self.gb_model = GradientBoostingClassifier(
            n_estimators=200, max_depth=5, learning_rate=0.1,
            subsample=0.8, random_state=42)
        self.gb_model.fit(X_train_s, y_train)
        gb_acc = accuracy_score(y_test, self.gb_model.predict(X_test_s))
        gb_time = time.time() - t0

        # ── Train Random Forest ────────────────────────────────
        t0 = time.time()
        self.rf_model = RandomForestClassifier(
            n_estimators=150, max_depth=8, random_state=42)
        self.rf_model.fit(X_train_s, y_train)
        rf_acc = accuracy_score(y_test, self.rf_model.predict(X_test_s))
        rf_time = time.time() - t0

        # ── Train PyTorch net (if available) ────────────────────
        torch_acc = None
        if TORCH_AVAILABLE:
            try:
                torch_acc = self._train_torch(X_train_s, y_train, X_test_s, y_test)
            except Exception as e:
                logger.warning("PyTorch training failed: %s", e)

        self.is_trained = True
        report = {
            "status": "trained",
            "gradient_boost": {"accuracy": round(gb_acc, 4), "train_time_s": round(gb_time, 3)},
            "random_forest":  {"accuracy": round(rf_acc, 4), "train_time_s": round(rf_time, 3)},
            "pytorch":        {"accuracy": round(torch_acc, 4) if torch_acc else None},
            "samples":        len(X_arr),
            "features":       X_arr.shape[1],
            "classes":        len(set(y)),
        }
        logger.info("Training complete: GB=%.3f RF=%.3f %s",
                     gb_acc, rf_acc,
                     f"NN={torch_acc:.3f}" if torch_acc else "NN=n/a")
        return report

    def _train_torch(self, X_train, y_train, X_test, y_test) -> float:
        """Train the PyTorch SensorNet."""
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        model = SensorNet(input_dim=X_train.shape[1], n_classes=4).to(device)

        X_t = torch.tensor(X_train, dtype=torch.float32).to(device)
        y_t = torch.tensor(y_train, dtype=torch.long).to(device)
        X_v = torch.tensor(X_test, dtype=torch.float32).to(device)
        y_v = torch.tensor(y_test, dtype=torch.long).to(device)

        optimizer = torch.optim.Adam(model.parameters(), lr=0.001, weight_decay=1e-4)
        scheduler = torch.optim.lr_scheduler.StepLR(optimizer, step_size=30, gamma=0.5)

        model.train()
        for epoch in range(80):
            optimizer.zero_grad()
            out = model(X_t)
            loss = F.cross_entropy(out, y_t)
            loss.backward()
            optimizer.step()
            scheduler.step()

        model.eval()
        with torch.no_grad():
            preds = model(X_v).argmax(dim=1)
            acc = (preds == y_v).float().mean().item()

        self.torch_model = model
        return acc

    def predict(self, features: List[float]) -> Dict[str, Any]:
        """
        Predict severity for a single feature vector using ensemble voting.
        Returns dict with severity, confidence, action, and model votes.
        """
        votes = []
        weights = []

        # Rule-based (always available, lowest weight)
        sev_r, conf_r, act_r = self.rule_model.predict(features)
        votes.append(sev_r)
        weights.append(0.2)

        if self.is_trained and NUMPY_AVAILABLE:
            f_arr = np.array([features], dtype=np.float32)
            f_scaled = self.scaler.transform(f_arr) if self.scaler else f_arr

            # Gradient Boosting
            if self.gb_model:
                gb_pred = int(self.gb_model.predict(f_scaled)[0])
                gb_proba = self.gb_model.predict_proba(f_scaled)[0]
                gb_conf = float(max(gb_proba))
                votes.append(gb_pred)
                weights.append(0.4 * gb_conf)

            # Random Forest
            if self.rf_model:
                rf_pred = int(self.rf_model.predict(f_scaled)[0])
                rf_proba = self.rf_model.predict_proba(f_scaled)[0]
                rf_conf = float(max(rf_proba))
                votes.append(rf_pred)
                weights.append(0.25 * rf_conf)

            # PyTorch
            if self.torch_model and TORCH_AVAILABLE:
                with torch.no_grad():
                    t_in = torch.tensor(f_scaled, dtype=torch.float32)
                    logits = self.torch_model(t_in)
                    probs = F.softmax(logits, dim=-1)
                    nn_pred = int(probs.argmax(dim=1).item())
                    nn_conf = float(probs.max().item())
                    votes.append(nn_pred)
                    weights.append(0.35 * nn_conf)

        # Weighted vote
        if not votes:
            final_sev = sev_r
        else:
            score_per_class = {0: 0.0, 1: 0.0, 2: 0.0, 3: 0.0}
            for v, w in zip(votes, weights):
                score_per_class[v] += w
            final_sev = max(score_per_class, key=score_per_class.get)

        total_weight = sum(weights) or 1.0
        confidence = score_per_class.get(final_sev, 0.0) / total_weight

        return {
            "severity": final_sev,
            "severity_label": self.SEVERITY_MAP[final_sev],
            "confidence": round(confidence, 4),
            "action": self.ACTION_MAP[final_sev],
            "model_votes": votes,
            "model_weights": [round(w, 3) for w in weights],
            "is_ml_trained": self.is_trained,
        }

    def predict_batch(self, feature_matrix: List[List[float]]
                      ) -> List[Dict[str, Any]]:
        """Predict for multiple samples."""
        return [self.predict(f) for f in feature_matrix]

    # ── Persistence ──────────────────────────────────────────────

    def save(self, path: Optional[str] = None):
        """Save trained models to disk."""
        save_dir = Path(path) if path else MODEL_DIR
        save_dir.mkdir(parents=True, exist_ok=True)

        if self.gb_model:
            with open(save_dir / "gb_model.pkl", "wb") as f:
                pickle.dump(self.gb_model, f)
        if self.rf_model:
            with open(save_dir / "rf_model.pkl", "wb") as f:
                pickle.dump(self.rf_model, f)
        if self.scaler:
            with open(save_dir / "scaler.pkl", "wb") as f:
                pickle.dump(self.scaler, f)
        if self.torch_model and TORCH_AVAILABLE:
            torch.save(self.torch_model.state_dict(), save_dir / "sensor_net.pt")

        meta = {"is_trained": self.is_trained, "saved_at": time.time()}
        with open(save_dir / "model_meta.json", "w") as f:
            json.dump(meta, f)

        logger.info("Models saved to %s", save_dir)

    def load(self, path: Optional[str] = None) -> bool:
        """Load trained models from disk."""
        load_dir = Path(path) if path else MODEL_DIR
        meta_file = load_dir / "model_meta.json"

        if not meta_file.exists():
            logger.info("No saved models found at %s", load_dir)
            return False

        try:
            if SKLEARN_AVAILABLE:
                gb_path = load_dir / "gb_model.pkl"
                if gb_path.exists():
                    with open(gb_path, "rb") as f:
                        self.gb_model = pickle.load(f)

                rf_path = load_dir / "rf_model.pkl"
                if rf_path.exists():
                    with open(rf_path, "rb") as f:
                        self.rf_model = pickle.load(f)

                sc_path = load_dir / "scaler.pkl"
                if sc_path.exists():
                    with open(sc_path, "rb") as f:
                        self.scaler = pickle.load(f)

            if TORCH_AVAILABLE:
                nn_path = load_dir / "sensor_net.pt"
                if nn_path.exists():
                    self.torch_model = SensorNet()
                    self.torch_model.load_state_dict(
                        torch.load(nn_path, map_location="cpu"))
                    self.torch_model.eval()

            self.is_trained = True
            logger.info("Models loaded from %s", load_dir)
            return True
        except Exception as e:
            logger.error("Failed to load models: %s", e)
            return False
