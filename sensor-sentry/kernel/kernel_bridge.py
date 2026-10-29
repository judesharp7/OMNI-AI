"""
kernel_bridge.py — Python ↔ C++ Kernel Bridge
==============================================
Provides a clean Pythonic API on top of the compiled C++ shared library.
Falls back to a pure-Python emulation if the native kernel isn't built yet.
"""

import ctypes
import logging
import platform
import time
from ctypes import (
    Structure, c_int32, c_uint64, c_double, c_char, c_size_t,
    POINTER, byref
)
from pathlib import Path
from typing import Optional, Dict, List, Any

logger = logging.getLogger(__name__)

KERNEL_DIR = Path(__file__).resolve().parent


# ── C struct mirrors ────────────────────────────────────────────

class AnomalyDecision(Structure):
    _fields_ = [
        ("sensor_id",          c_int32),
        ("value",              c_double),
        ("z_score",            c_double),
        ("cusum_pos",          c_double),
        ("cusum_neg",          c_double),
        ("kalman_estimate",    c_double),
        ("kalman_uncertainty", c_double),
        ("severity",           c_int32),
        ("confidence",         c_double),
        ("action",             c_char * 128),
        ("timestamp_ms",       c_double),
    ]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "sensor_id":          self.sensor_id,
            "value":              self.value,
            "z_score":            round(self.z_score, 4),
            "cusum_pos":          round(self.cusum_pos, 4),
            "cusum_neg":          round(self.cusum_neg, 4),
            "kalman_estimate":    round(self.kalman_estimate, 4),
            "kalman_uncertainty": round(self.kalman_uncertainty, 6),
            "severity":           self.severity,
            "severity_label":     ["NOMINAL", "WARNING", "CRITICAL", "EMERGENCY"][
                                      min(self.severity, 3)],
            "confidence":         round(self.confidence, 4),
            "action":             self.action.decode("utf-8", errors="ignore").rstrip("\x00"),
            "timestamp_ms":       self.timestamp_ms,
        }


class KernelStats(Structure):
    _fields_ = [
        ("readings_processed", c_uint64),
        ("anomalies_detected", c_uint64),
        ("warnings_detected",  c_uint64),
        ("gc_cycles",          c_uint64),
        ("avg_latency_us",     c_double),
        ("max_latency_us",     c_double),
        ("free_pool_slots",    c_size_t),
        ("pool_capacity",      c_size_t),
        ("uptime_seconds",     c_double),
        ("active_sensors",     c_int32),
    ]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "readings_processed": self.readings_processed,
            "anomalies_detected": self.anomalies_detected,
            "warnings_detected":  self.warnings_detected,
            "gc_cycles":          self.gc_cycles,
            "avg_latency_us":     round(self.avg_latency_us, 2),
            "max_latency_us":     round(self.max_latency_us, 2),
            "free_pool_slots":    self.free_pool_slots,
            "pool_capacity":      self.pool_capacity,
            "uptime_seconds":     round(self.uptime_seconds, 2),
            "active_sensors":     self.active_sensors,
        }


# ── Native kernel loader ───────────────────────────────────────

def _find_kernel_lib() -> Optional[Path]:
    """Locate the compiled kernel shared library."""
    system = platform.system()
    if system == "Windows":
        candidates = ["omni_kernel.dll"]
    elif system == "Linux":
        candidates = ["omni_kernel.so", "libomni_kernel.so"]
    else:
        candidates = ["omni_kernel.dylib", "libomni_kernel.dylib"]

    for name in candidates:
        path = KERNEL_DIR / name
        if path.exists():
            return path
    return None


def _load_native() -> Optional[ctypes.CDLL]:
    """Try to load the native C++ kernel."""
    lib_path = _find_kernel_lib()
    if not lib_path:
        return None
    try:
        lib = ctypes.CDLL(str(lib_path))

        # omni_kernel_init() → int
        lib.omni_kernel_init.argtypes = []
        lib.omni_kernel_init.restype = c_int32

        # omni_kernel_destroy()
        lib.omni_kernel_destroy.argtypes = []
        lib.omni_kernel_destroy.restype = None

        # omni_push_reading(sensor_id, value, timestamp_ms) → int
        lib.omni_push_reading.argtypes = [c_int32, c_double, c_double]
        lib.omni_push_reading.restype = c_int32

        # omni_process_sensor(sensor_id, AnomalyDecision*) → int
        lib.omni_process_sensor.argtypes = [c_int32, POINTER(AnomalyDecision)]
        lib.omni_process_sensor.restype = c_int32

        # omni_process_batch(sensor_id, arr, max_out, n_written*) → int
        lib.omni_process_batch.argtypes = [
            c_int32, POINTER(AnomalyDecision), c_int32, POINTER(c_int32)]
        lib.omni_process_batch.restype = c_int32

        # omni_get_stats(KernelStats*) → void
        lib.omni_get_stats.argtypes = [POINTER(KernelStats)]
        lib.omni_get_stats.restype = None

        # omni_trigger_gc() → void
        lib.omni_trigger_gc.argtypes = []
        lib.omni_trigger_gc.restype = None

        # omni_get_sensor_mean(sensor_id) → double
        lib.omni_get_sensor_mean.argtypes = [c_int32]
        lib.omni_get_sensor_mean.restype = c_double

        # omni_get_sensor_stddev(sensor_id) → double
        lib.omni_get_sensor_stddev.argtypes = [c_int32]
        lib.omni_get_sensor_stddev.restype = c_double

        # omni_get_kalman_estimate(sensor_id) → double
        lib.omni_get_kalman_estimate.argtypes = [c_int32]
        lib.omni_get_kalman_estimate.restype = c_double

        # omni_get_kalman_uncertainty(sensor_id) → double
        lib.omni_get_kalman_uncertainty.argtypes = [c_int32]
        lib.omni_get_kalman_uncertainty.restype = c_double

        # omni_max_sensors() → int
        lib.omni_max_sensors.argtypes = []
        lib.omni_max_sensors.restype = c_int32

        # omni_reset_sensor(sensor_id) → void
        lib.omni_reset_sensor.argtypes = [c_int32]
        lib.omni_reset_sensor.restype = None

        return lib

    except (OSError, AttributeError) as e:
        logger.warning("Failed to load native kernel: %s", e)
        return None


# ── Pure-Python fallback ────────────────────────────────────────

class _PythonFallbackKernel:
    """Emulates the kernel API in pure Python when the C++ lib isn't built."""

    def __init__(self):
        from collections import deque
        self._history: Dict[int, deque] = {}
        self._readings = 0
        self._anomalies = 0
        self._warnings = 0
        self._start = time.time()
        self._max_sensors = 64
        logger.info("Using pure-Python kernel fallback (build C++ kernel for 10-100× speedup)")

    def push_reading(self, sensor_id: int, value: float, ts: float) -> int:
        from collections import deque
        if sensor_id not in self._history:
            self._history[sensor_id] = deque(maxlen=200)
        self._history[sensor_id].append((value, ts))
        return 0

    def process_sensor(self, sensor_id: int) -> Optional[Dict]:
        if sensor_id not in self._history or len(self._history[sensor_id]) < 2:
            return None

        data = self._history[sensor_id]
        values = [v for v, _ in data]
        val, ts = data[-1]
        n = len(values)
        mean = sum(values) / n
        std = (sum((x - mean)**2 for x in values) / n) ** 0.5 if n > 1 else 1.0
        z = (val - mean) / std if std > 1e-12 else 0.0

        severity = 0
        action = "NOMINAL"
        if abs(z) >= 3.0:
            severity = 2
            action = f"ISOLATE_SENSOR_{sensor_id}_INITIATE_DIAGNOSTIC"
            self._anomalies += 1
        elif abs(z) >= 2.0:
            severity = 1
            action = f"LOG_WARNING_SENSOR_{sensor_id}_INCREASE_SAMPLING"
            self._warnings += 1

        self._readings += 1
        return {
            "sensor_id": sensor_id,
            "value": val,
            "z_score": round(z, 4),
            "cusum_pos": 0.0,
            "cusum_neg": 0.0,
            "kalman_estimate": round(mean, 4),
            "kalman_uncertainty": 0.1,
            "severity": severity,
            "severity_label": ["NOMINAL", "WARNING", "CRITICAL", "EMERGENCY"][severity],
            "confidence": min(1.0, n / 50.0),
            "action": action,
            "timestamp_ms": ts,
        }

    def get_stats(self) -> Dict:
        return {
            "readings_processed": self._readings,
            "anomalies_detected": self._anomalies,
            "warnings_detected":  self._warnings,
            "gc_cycles":          0,
            "avg_latency_us":     0.0,
            "max_latency_us":     0.0,
            "free_pool_slots":    0,
            "pool_capacity":      0,
            "uptime_seconds":     round(time.time() - self._start, 2),
            "active_sensors":     len(self._history),
        }

    def trigger_gc(self):
        pass  # no-op in Python fallback


# ── Unified Kernel API ──────────────────────────────────────────

class OmniKernel:
    """
    Unified interface to the OMNI-AI C++ kernel.
    Auto-detects and loads the native library, falling back to
    pure-Python emulation if the .dll/.so hasn't been built.
    """

    def __init__(self):
        self._native = _load_native()
        self._fallback: Optional[_PythonFallbackKernel] = None
        self.native_available = False

        if self._native:
            rc = self._native.omni_kernel_init()
            if rc == 0:
                self.native_available = True
                logger.info("✅ Native C++ kernel loaded and initialised")
            else:
                logger.warning("Native kernel init returned %d, using fallback", rc)
                self._fallback = _PythonFallbackKernel()
        else:
            self._fallback = _PythonFallbackKernel()

    # ── Core operations ─────────────────────────────────────────

    def push_reading(self, sensor_id: int, value: float,
                     timestamp_ms: Optional[float] = None) -> int:
        """Push a sensor reading into the kernel's ring buffer."""
        ts = timestamp_ms if timestamp_ms is not None else time.time() * 1000.0
        if self.native_available:
            return self._native.omni_push_reading(sensor_id, value, ts)
        return self._fallback.push_reading(sensor_id, value, ts)

    def process_sensor(self, sensor_id: int) -> Optional[Dict[str, Any]]:
        """Process the next pending reading for a sensor. Returns dict or None."""
        if self.native_available:
            d = AnomalyDecision()
            rc = self._native.omni_process_sensor(sensor_id, byref(d))
            if rc != 0:
                return None
            return d.to_dict()
        return self._fallback.process_sensor(sensor_id)

    def process_batch(self, sensor_id: int, max_items: int = 64
                      ) -> List[Dict[str, Any]]:
        """Process all pending readings for a sensor, up to max_items."""
        if self.native_available:
            arr = (AnomalyDecision * max_items)()
            n = c_int32(0)
            self._native.omni_process_batch(sensor_id, arr, max_items, byref(n))
            return [arr[i].to_dict() for i in range(n.value)]
        else:
            results = []
            for _ in range(max_items):
                r = self._fallback.process_sensor(sensor_id)
                if r is None:
                    break
                results.append(r)
            return results

    def get_stats(self) -> Dict[str, Any]:
        """Get kernel telemetry."""
        if self.native_available:
            s = KernelStats()
            self._native.omni_get_stats(byref(s))
            d = s.to_dict()
            d["backend"] = "native_cpp"
            return d
        d = self._fallback.get_stats()
        d["backend"] = "python_fallback"
        return d

    def trigger_gc(self):
        """Trigger garbage collection in the slab allocator."""
        if self.native_available:
            self._native.omni_trigger_gc()
        else:
            self._fallback.trigger_gc()

    def get_sensor_info(self, sensor_id: int) -> Dict[str, float]:
        """Get real-time statistics for a sensor."""
        if self.native_available:
            return {
                "mean":               self._native.omni_get_sensor_mean(sensor_id),
                "std_dev":            self._native.omni_get_sensor_stddev(sensor_id),
                "kalman_estimate":    self._native.omni_get_kalman_estimate(sensor_id),
                "kalman_uncertainty": self._native.omni_get_kalman_uncertainty(sensor_id),
            }
        return {"mean": 0.0, "std_dev": 0.0,
                "kalman_estimate": 0.0, "kalman_uncertainty": 0.0}

    def reset_sensor(self, sensor_id: int):
        """Reset a sensor's state (stats, Kalman, buffer)."""
        if self.native_available:
            self._native.omni_reset_sensor(sensor_id)
        elif self._fallback and sensor_id in self._fallback._history:
            self._fallback._history[sensor_id].clear()

    def shutdown(self):
        """Cleanly tear down the kernel."""
        if self.native_available:
            self._native.omni_kernel_destroy()
            self.native_available = False
            logger.info("Native kernel destroyed")

    def __del__(self):
        try:
            self.shutdown()
        except Exception:
            pass
