# modules/vision.py
# Streamlit-only obstacle detection logic.
# UI must call: analyze_frame(frame=None) -> {"label": str, "confidence": float}
# Stability > complexity.

from __future__ import annotations

import os
import logging
from typing import Any, Dict, List
from collections import deque

# Console logging for demo transparency
logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s - %(message)s")
logger = logging.getLogger("vision")

# Optional imports (kept safe). If missing, we still return valid output.
try:
    import numpy as np  # type: ignore
except Exception:
    np = None  # type: ignore

try:
    import cv2  # type: ignore
except Exception:
    cv2 = None  # type: ignore

# --- Confidence Smoothing & Anti-Flicker ---
_label_history: deque = deque(maxlen=5)   # last 5 labels
_conf_history: deque = deque(maxlen=5)    # last 5 confidence values
_consecutive_failures: int = 0
MAX_FAILURES_BEFORE_FALLBACK = 5


# Internal helpers -------------------------------------------------------------

def _clamp01(x: Any) -> float:
    try:
        v = float(x)
    except Exception:
        return 0.0
    if v < 0.0:
        return 0.0
    if v > 1.0:
        return 1.0
    return v


def _safe_return(label: Any, confidence: Any) -> Dict[str, Any]:
    lbl = str(label) if label is not None else "clear"
    conf = _clamp01(confidence)

    allowed = {"step", "curb", "object", "clear"}
    if lbl not in allowed:
        return {"label": "clear", "confidence": 0.0}

    return {"label": lbl, "confidence": conf}


def _smooth_result(label: str, confidence: float) -> Dict[str, Any]:
    """Apply temporal smoothing to reduce flicker.
    Uses majority-vote on last 5 labels and averages confidence."""
    global _consecutive_failures
    _consecutive_failures = 0  # reset on successful detection

    _label_history.append(label)
    _conf_history.append(confidence)

    # Majority vote for label stability (activates after 2 frames)
    if len(_label_history) >= 2:
        from collections import Counter
        vote = Counter(_label_history).most_common(1)[0][0]
    else:
        vote = label

    # Average confidence smoothing
    avg_conf = sum(_conf_history) / len(_conf_history) if _conf_history else confidence

    logger.debug(f"Detection: raw={label}({confidence:.2f}) -> smoothed={vote}({avg_conf:.2f})")
    return _safe_return(vote, avg_conf)


def _handle_failure() -> Dict[str, Any]:
    """Track failures and auto-fallback to mock if too many consecutive."""
    global _consecutive_failures
    _consecutive_failures += 1
    logger.warning(f"Detection failure #{_consecutive_failures}/{MAX_FAILURES_BEFORE_FALLBACK}")

    if _consecutive_failures >= MAX_FAILURES_BEFORE_FALLBACK:
        logger.warning("Too many failures — falling back to Mock Mode")
        try:
            import streamlit as st
            st.session_state["mock_mode"] = True
            st.session_state["_auto_mock"] = True
        except Exception:
            pass
        return _safe_return("clear", 0.0)

    return _safe_return("clear", 0.0)


def _is_mock_mode() -> bool:
    # Environment override (useful in demos)
    if str(os.getenv("MOCK_MODE", "")).strip().lower() in {"1", "true", "yes", "on"}:
        return True

    # Streamlit session_state (does not require UI changes)
    try:
        import streamlit as st
        return bool(st.session_state.get("mock_mode", False))
    except Exception:
        return False


def _mock_output() -> Dict[str, Any]:
    try:
        import streamlit as st
        lbl = st.session_state.get("mock_label", "clear")
        conf = st.session_state.get("mock_confidence", 0.0)
        return _safe_return(lbl, conf)
    except Exception:
        return _safe_return("clear", 0.0)


# Core detection --------------------------------------------------------------

def analyze_frame(frame=None) -> dict:
    """
    Required signature. Must always return:
    {
        "label": str,         # "step", "curb", "object", "clear"
        "confidence": float   # 0.0 to 1.0
    }
    """
    # Mock mode OR no frame provided => safe mock output
    if _is_mock_mode() or frame is None:
        logger.info("Mock mode active — returning simulated output")
        return _mock_output()

    # Real mode: simple heuristic. Never crash.
    try:
        if cv2 is None or np is None:
            logger.warning("cv2/numpy not available")
            return _handle_failure()

        img = frame

        # If it's not a numpy array (e.g., PIL image), try converting
        if not isinstance(img, np.ndarray):
            try:
                img = np.array(img)
            except Exception:
                logger.warning("Failed to convert frame to numpy array")
                return _handle_failure()

        if img is None or getattr(img, "size", 0) == 0:
            logger.warning("Empty or invalid frame")
            return _handle_failure()

        # Convert to grayscale safely
        if len(img.shape) == 3:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        else:
            gray = img.copy()

        gray = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(gray, 60, 160)

        h, w = edges.shape[:2]

        # Bottom strip: step/curb cues
        bottom = edges[int(h * 0.65): h, :]
        bottom_density = float(np.mean(bottom > 0))  # 0..1

        # Center area: object cues
        cy1, cy2 = int(h * 0.30), int(h * 0.85)
        cx1, cx2 = int(w * 0.20), int(w * 0.80)
        center = edges[cy1:cy2, cx1:cx2]
        center_density = float(np.mean(center > 0))  # 0..1

        # Reduce flicker slightly
        bottom_density = round(bottom_density, 3)
        center_density = round(center_density, 3)

        # Conservative thresholds for demo safety
        if bottom_density > 0.085:
            label = "step" if bottom_density > 0.12 else "curb"
            conf = (bottom_density - 0.08) / 0.10
            return _smooth_result(label, conf)

        if center_density > 0.065:
            conf = (center_density - 0.06) / 0.10
            return _smooth_result("object", conf)

        return _smooth_result("clear", 0.0)

    except Exception as e:
        logger.error(f"Detection exception: {e}")
        return _handle_failure()
