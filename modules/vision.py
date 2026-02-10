# modules/vision.py
# Streamlit-only obstacle detection logic.
# UI must call: analyze_frame(frame=None) -> {"label": str, "confidence": float}
# Stability > complexity.

from __future__ import annotations

import os
from typing import Any, Dict

# Optional imports (kept safe). If missing, we still return valid output.
try:
    import numpy as np  # type: ignore
except Exception:
    np = None  # type: ignore

try:
    import cv2  # type: ignore
except Exception:
    cv2 = None  # type: ignore


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
        return _mock_output()

    # Real mode: simple heuristic. Never crash.
    try:
        if cv2 is None or np is None:
            return _safe_return("clear", 0.0)

        img = frame

        # If it's not a numpy array (e.g., PIL image), try converting
        if not isinstance(img, np.ndarray):
            try:
                img = np.array(img)
            except Exception:
                return _safe_return("clear", 0.0)

        if img is None or getattr(img, "size", 0) == 0:
            return _safe_return("clear", 0.0)

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
            return _safe_return(label, conf)

        if center_density > 0.065:
            conf = (center_density - 0.06) / 0.10
            return _safe_return("object", conf)

        return _safe_return("clear", 0.0)

    except Exception:
        return _safe_return("clear", 0.0)
