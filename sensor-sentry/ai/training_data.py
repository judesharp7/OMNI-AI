"""
training_data.py — Curated Sensor AI Training Datasets
======================================================
Provides structured training data for the sensor AI decision model.
Datasets are based on real-world patterns from:
  - NASA Bearing Dataset (vibration anomaly detection)
  - SKAB (Skoltech Anomaly Benchmark for IoT)
  - Yahoo S5 (time-series anomaly detection)
  - UCR Time Series Archive (classification baselines)
  - Tennessee Eastman Process (chemical plant faults)

Each sample is a feature vector + label for supervised training.
"""

import random
import math
import logging
from typing import List, Dict, Tuple, Any
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class TrainingSample:
    """Single training example for the sensor AI model."""
    features: List[float]
    label: str              # NOMINAL / WARNING / CRITICAL / EMERGENCY
    severity: int           # 0-3
    sensor_type: str        # temperature / pressure / vibration / humidity / current / flow
    description: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


# ── Feature Extraction ─────────────────────────────────────────

def extract_features(readings: List[float], window: int = 50) -> List[float]:
    """
    Extract 16 statistical features from a sensor time-series window.
    These features are chosen based on literature from:
      - Bearing fault detection (vibration analysis)
      - Process control (chemical/thermal monitoring)
      - IoT anomaly detection benchmarks
    """
    n = len(readings)
    if n < 5:
        return [0.0] * 16

    w = readings[-min(n, window):]
    mean = sum(w) / len(w)
    var = sum((x - mean) ** 2 for x in w) / len(w) if len(w) > 1 else 0.0
    std = var ** 0.5

    # Rate-of-change features
    diffs = [w[i] - w[i-1] for i in range(1, len(w))]
    diff_mean = sum(diffs) / len(diffs) if diffs else 0.0
    diff_max = max(diffs) if diffs else 0.0

    # Z-score of latest value
    z = (w[-1] - mean) / std if std > 1e-12 else 0.0

    # Peak-to-peak
    p2p = max(w) - min(w)

    # RMS (Root Mean Square)
    rms = (sum(x ** 2 for x in w) / len(w)) ** 0.5

    # Kurtosis (peakedness — heavy tails indicate anomalies)
    kurt = 0.0
    if std > 1e-12 and len(w) > 3:
        kurt = sum((x - mean) ** 4 for x in w) / (len(w) * std ** 4) - 3.0

    # Skewness (asymmetry)
    skew = 0.0
    if std > 1e-12 and len(w) > 2:
        skew = sum((x - mean) ** 3 for x in w) / (len(w) * std ** 3)

    # Crest factor (peak / RMS)
    crest = max(abs(x) for x in w) / rms if rms > 1e-12 else 0.0

    # Energy (sum of squares)
    energy = sum(x ** 2 for x in w)

    # Crossing rate (how often signal crosses the mean)
    crossings = sum(1 for i in range(1, len(w))
                    if (w[i] - mean) * (w[i-1] - mean) < 0)
    crossing_rate = crossings / len(w) if len(w) > 1 else 0.0

    # Trend slope (linear regression coefficient)
    x_indices = list(range(len(w)))
    x_mean = sum(x_indices) / len(x_indices)
    slope_num = sum((xi - x_mean) * (yi - mean)
                    for xi, yi in zip(x_indices, w))
    slope_den = sum((xi - x_mean) ** 2 for xi in x_indices)
    trend_slope = slope_num / slope_den if slope_den > 0 else 0.0

    # Autocorrelation at lag 1
    autocorr = 0.0
    if len(w) > 2 and var > 1e-12:
        autocorr = sum((w[i] - mean) * (w[i-1] - mean)
                       for i in range(1, len(w))) / ((len(w) - 1) * var)

    return [
        mean,           # 0  — central tendency
        std,            # 1  — spread
        z,              # 2  — latest deviation
        p2p,            # 3  — range
        rms,            # 4  — signal energy proxy
        kurt,           # 5  — tail weight (anomaly indicator)
        skew,           # 6  — asymmetry
        crest,          # 7  — peak-to-RMS ratio
        energy,         # 8  — total energy
        crossing_rate,  # 9  — oscillation frequency
        trend_slope,    # 10 — directional drift
        autocorr,       # 11 — temporal dependence
        diff_mean,      # 12 — average rate of change
        diff_max,       # 13 — max instantaneous change
        w[-1],          # 14 — latest raw value
        len(w),         # 15 — window size (data maturity)
    ]


# ── Synthetic Dataset Generators ────────────────────────────────

def _generate_normal_readings(base: float, noise: float, n: int = 100) -> List[float]:
    """Generate normal sensor readings (Gaussian noise around base)."""
    return [base + random.gauss(0, noise) for _ in range(n)]


def _generate_drift(base: float, noise: float, drift_rate: float, n: int = 100) -> List[float]:
    """Simulate gradual sensor drift (aging sensor, fouling, etc.)."""
    return [base + random.gauss(0, noise) + drift_rate * i for i in range(n)]


def _generate_spike(base: float, noise: float, spike_mag: float,
                    spike_pos: int = 80, n: int = 100) -> List[float]:
    """Simulate sudden spike anomaly."""
    data = _generate_normal_readings(base, noise, n)
    data[spike_pos] = base + spike_mag
    return data


def _generate_oscillation(base: float, noise: float,
                          amplitude: float, period: int = 20,
                          n: int = 100) -> List[float]:
    """Simulate periodic oscillation (mechanical vibration, etc.)."""
    return [base + amplitude * math.sin(2 * math.pi * i / period)
            + random.gauss(0, noise) for i in range(n)]


def _generate_step_change(base: float, noise: float,
                          step_mag: float, step_pos: int = 50,
                          n: int = 100) -> List[float]:
    """Simulate sudden level shift (valve opening, mode change)."""
    return [(base + random.gauss(0, noise)) if i < step_pos
            else (base + step_mag + random.gauss(0, noise))
            for i in range(n)]


def _generate_intermittent_fault(base: float, noise: float,
                                 fault_mag: float, n: int = 100) -> List[float]:
    """Simulate intermittent sensor faults (loose connection, etc.)."""
    data = _generate_normal_readings(base, noise, n)
    for i in range(n):
        if random.random() > 0.95:
            data[i] = base + fault_mag * random.choice([-1, 1])
    return data


# ── Sensor Profiles (based on real-world sensor specs) ──────────

SENSOR_PROFILES = {
    "temperature": {
        "base": 72.0, "noise": 2.0, "unit": "°C",
        "warn_z": 2.0, "crit_z": 3.0,
        "spike": 25.0, "drift_rate": 0.05
    },
    "pressure": {
        "base": 145.0, "noise": 4.0, "unit": "PSI",
        "warn_z": 2.0, "crit_z": 3.0,
        "spike": 50.0, "drift_rate": 0.1
    },
    "vibration": {
        "base": 2.1, "noise": 0.3, "unit": "mm/s",
        "warn_z": 2.0, "crit_z": 3.0,
        "spike": 5.0, "drift_rate": 0.01
    },
    "humidity": {
        "base": 55.0, "noise": 3.0, "unit": "%RH",
        "warn_z": 2.0, "crit_z": 3.0,
        "spike": 30.0, "drift_rate": 0.08
    },
    "current": {
        "base": 12.4, "noise": 0.6, "unit": "A",
        "warn_z": 2.0, "crit_z": 3.0,
        "spike": 8.0, "drift_rate": 0.02
    },
    "flow_rate": {
        "base": 88.0, "noise": 5.0, "unit": "L/m",
        "warn_z": 2.0, "crit_z": 3.0,
        "spike": 45.0, "drift_rate": 0.15
    },
}


# ── Complete Training Dataset Generator ─────────────────────────

def generate_training_dataset(samples_per_class: int = 200) -> List[TrainingSample]:
    """
    Generate a comprehensive training dataset covering all failure modes.

    Failure modes modeled (inspired by real datasets):
    - Normal operation → NOMINAL
    - Minor drift → WARNING
    - Sudden spike → CRITICAL
    - Step change → CRITICAL
    - Intermittent faults → WARNING / CRITICAL
    - Heavy oscillation → WARNING
    - Cascading failure (drift + spike) → EMERGENCY
    """
    dataset: List[TrainingSample] = []

    for sensor_type, profile in SENSOR_PROFILES.items():
        base = profile["base"]
        noise = profile["noise"]
        spike = profile["spike"]
        drift = profile["drift_rate"]

        # ── NOMINAL samples ────────────────────────────────────
        for _ in range(samples_per_class):
            readings = _generate_normal_readings(base, noise)
            features = extract_features(readings)
            dataset.append(TrainingSample(
                features=features, label="NOMINAL", severity=0,
                sensor_type=sensor_type,
                description="Normal operating conditions"
            ))

        # ── WARNING samples ────────────────────────────────────
        # Mild drift
        for _ in range(samples_per_class // 3):
            readings = _generate_drift(base, noise, drift * 0.5)
            features = extract_features(readings)
            dataset.append(TrainingSample(
                features=features, label="WARNING", severity=1,
                sensor_type=sensor_type,
                description="Gradual sensor drift detected"
            ))

        # Mild oscillation
        for _ in range(samples_per_class // 3):
            readings = _generate_oscillation(base, noise, noise * 2.5)
            features = extract_features(readings)
            dataset.append(TrainingSample(
                features=features, label="WARNING", severity=1,
                sensor_type=sensor_type,
                description="Abnormal oscillation pattern"
            ))

        # Intermittent minor fault
        for _ in range(samples_per_class // 3):
            readings = _generate_intermittent_fault(base, noise, spike * 0.3)
            features = extract_features(readings)
            dataset.append(TrainingSample(
                features=features, label="WARNING", severity=1,
                sensor_type=sensor_type,
                description="Intermittent minor fault"
            ))

        # ── CRITICAL samples ───────────────────────────────────
        # Sudden spike
        for _ in range(samples_per_class // 3):
            readings = _generate_spike(base, noise, spike)
            features = extract_features(readings)
            dataset.append(TrainingSample(
                features=features, label="CRITICAL", severity=2,
                sensor_type=sensor_type,
                description="Sudden critical spike"
            ))

        # Step change
        for _ in range(samples_per_class // 3):
            readings = _generate_step_change(base, noise, spike * 0.7)
            features = extract_features(readings)
            dataset.append(TrainingSample(
                features=features, label="CRITICAL", severity=2,
                sensor_type=sensor_type,
                description="Level shift — possible equipment failure"
            ))

        # Heavy intermittent faults
        for _ in range(samples_per_class // 3):
            readings = _generate_intermittent_fault(base, noise, spike * 0.8)
            features = extract_features(readings)
            dataset.append(TrainingSample(
                features=features, label="CRITICAL", severity=2,
                sensor_type=sensor_type,
                description="Severe intermittent sensor fault"
            ))

        # ── EMERGENCY samples ──────────────────────────────────
        # Cascading: drift → spike
        for _ in range(samples_per_class // 2):
            readings = _generate_drift(base, noise, drift * 2, n=80)
            readings.extend(_generate_spike(
                base + drift * 2 * 80, noise, spike * 1.5, spike_pos=15, n=20))
            features = extract_features(readings)
            dataset.append(TrainingSample(
                features=features, label="EMERGENCY", severity=3,
                sensor_type=sensor_type,
                description="Cascading failure — drift + critical spike"
            ))

        # Runaway (exponential growth)
        for _ in range(samples_per_class // 2):
            readings = [base + noise * random.gauss(0, 1) + (1.05 ** i - 1) * noise * 3
                        for i in range(100)]
            features = extract_features(readings)
            dataset.append(TrainingSample(
                features=features, label="EMERGENCY", severity=3,
                sensor_type=sensor_type,
                description="Runaway condition — exponential divergence"
            ))

    random.shuffle(dataset)
    logger.info("Generated training dataset: %d samples across %d sensor types",
                len(dataset), len(SENSOR_PROFILES))
    return dataset


def dataset_to_arrays(dataset: List[TrainingSample]) -> Tuple[List[List[float]], List[int]]:
    """Convert dataset to feature matrix X and label vector y for training."""
    X = [s.features for s in dataset]
    y = [s.severity for s in dataset]
    return X, y


def get_label_map() -> Dict[int, str]:
    return {0: "NOMINAL", 1: "WARNING", 2: "CRITICAL", 3: "EMERGENCY"}
