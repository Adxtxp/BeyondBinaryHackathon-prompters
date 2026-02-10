import pyttsx3
import threading
import time

# --- CONFIGURATION ---
COOLDOWN_SECONDS = 3.0  # Wait 3s before repeating the SAME warning
_last_triggered_time = 0
_last_triggered_label = None

def build_feedback(label: str):
    """
    Maps labels to messages + simulated vibration patterns.
    """
    mapping = {
        "step":   {"message": "Caution. Step ahead.", "pattern": [200, 100, 200]},
        "curb":   {"message": "Curb detected.",       "pattern": [200, 100, 200]},
        "object": {"message": "Obstacle detected.",   "pattern": [500]},
        "clear":  {"message": "",                     "pattern": []},
    }
    return mapping.get(label, {"message": "Unknown obstacle", "pattern": [100]})

def _speak_worker(text):
    """
    Runs in a background thread so the camera doesn't freeze.
    """
    try:
        # Re-initialize engine inside thread to avoid loop conflicts
        engine = pyttsx3.init()
        engine.setProperty('rate', 170) # Slightly faster speech
        engine.say(text)
        engine.runAndWait()
    except:
        pass # Fail silently if audio driver is busy

def trigger_feedback(label: str, mode: str):
    """
    Triggers multimodal feedback with Anti-Spam (Cooldown) logic.
    """
    global _last_triggered_time, _last_triggered_label
    
    # 1. Get the Feedback Data
    fb = build_feedback(label)
    current_time = time.time()
    
    # 2. COOLDOWN LOGIC (The most important part!)
    # If the path is clear, reset immediately so we are ready for the next obstacle.
    if label == "clear":
        _last_triggered_label = "clear"
        return {"status": "clear", "message": "", "pattern": []}

    # If we are seeing the SAME obstacle as before...
    if label == _last_triggered_label:
        # ...check if 3 seconds have passed. If not, do NOTHING.
        if (current_time - _last_triggered_time) < COOLDOWN_SECONDS:
            return {"status": "cooldown", "message": fb["message"], "pattern": []}

    # 3. If we pass the checks, TRIGGER the feedback
    _last_triggered_label = label
    _last_triggered_time = current_time

    # Audio Trigger (Threaded)
    if "Sound" in mode and fb["message"]:
        threading.Thread(target=_speak_worker, args=(fb["message"],)).start()

    # Return data for UI visualization (Role 2)
    return {
        "status": "triggered",
        "message": fb["message"],
        "pattern": fb["pattern"] if "Vibration" in mode else []
    }