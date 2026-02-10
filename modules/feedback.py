import pyttsx3

_tts_engine = None

def get_tts_engine():
    global _tts_engine
    if _tts_engine is None:
        _tts_engine = pyttsx3.init()
    return _tts_engine

def build_feedback(label: str):
    """
    Maps labels to messages + simulated vibration patterns.
    Returns a dict with:
      - message: text to speak/show
      - pattern: list of ints representing simulated vibration (ms)
    """
    mapping = {
        "step":   {"message": "Step detected ahead",   "pattern": [200, 100, 200, 100, 200]},
        "curb":   {"message": "Curb detected ahead",   "pattern": [200, 100, 200, 100, 200]},
        "object": {"message": "Obstacle detected",     "pattern": [300, 150, 300]},
        "clear":  {"message": "Path is clear",         "pattern": []},
    }
    return mapping.get(label, {"message": "Unknown obstacle", "pattern": [150, 100, 150]})

def trigger_feedback(label: str, mode: str):
    """
    mode: "Sound Only" | "Vibration Only" | "Sound + Vibration"
    """
    fb = build_feedback(label)

    # Sound (TTS)
    if label != "clear" and mode in ("Sound Only", "Sound + Vibration"):
        engine = get_tts_engine()
        engine.say(fb["message"])
        engine.runAndWait()

    # Vibration (simulated for Streamlit)
    # We'll show pattern on-screen later in the UI.
    return fb
