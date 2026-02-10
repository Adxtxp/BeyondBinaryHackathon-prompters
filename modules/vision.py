def analyze_frame(frame=None):
    """
    Analyze a camera frame and return obstacle detection result.

    Args:
        frame: an image/frame object (later from OpenCV)

    Returns:
        dict: {"label": str, "confidence": float}
    """
    # Mock mode output for now (Phase 1)
    return {"label": "clear", "confidence": 0.0}
