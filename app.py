import streamlit as st

from modules.vision import analyze_frame
from modules.feedback import trigger_feedback
from modules.utils import format_confidence

st.set_page_config(
    page_title="Multimodal Assistive Obstacle Detection",
    layout="wide"
)

st.title("Multimodal Assistive Obstacle Detection")

# --- Layout ---
left, right = st.columns([2, 1])

with left:
    st.subheader("Camera View")
    st.info("Phase 0/1: Camera feed will appear here soon.")

with right:
    st.subheader("Detection Status")
    st.write("Obstacle: --")
    st.write("Confidence: --")

st.divider()

mode = st.radio(
    "Accessibility Mode",
    ["Sound Only", "Vibration Only", "Sound + Vibration"],
    horizontal=True
)

mock_mode = st.checkbox("Mock Mode", value=True)

# --- Mock Detection Result (Phase 1 baseline) ---
if mock_mode:
    label = st.selectbox("Mock Label", ["clear", "step", "curb", "object"])
    confidence = st.slider("Mock Confidence", 0.0, 1.0, 0.92, 0.01)

    result = {"label": label, "confidence": confidence}
else:
    # Later: feed real frame into analyze_frame(frame)
    result = analyze_frame(frame=None)

label = result["label"]
confidence = result["confidence"]

with right:
    st.subheader("Detection Status")
    if label == "clear":
        st.success("CLEAR")
    else:
        st.error(label.upper())

    st.write(f"Confidence: {format_confidence(confidence)}")

# Trigger feedback (sound + simulated vibration)
feedback = trigger_feedback(label, mode)

if mode in ("Vibration Only", "Sound + Vibration") and label != "clear":
    st.warning(f"Simulated vibration pattern (ms): {feedback['pattern']}")
