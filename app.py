import streamlit as st
import cv2
import numpy as np


from modules.vision import analyze_frame
from modules.feedback import trigger_feedback
from modules.utils import format_confidence

st.set_page_config(
    page_title="Multimodal Assistive Obstacle Detection",
    layout="wide"
)

st.title("Multimodal Assistive Obstacle Detection")

# Initialize camera state
if "camera_running" not in st.session_state:
    st.session_state.camera_running = False

# --- Layout ---
left, right = st.columns([2, 1])

with left:
    st.subheader("Camera View")

    frame_placeholder = st.empty()

    if st.session_state.get("camera_running", False):
        cap = cv2.VideoCapture(0)

        if not cap.isOpened():
            st.error("Unable to access camera.")
        else:
            ret, frame = cap.read()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame_placeholder.image(frame, channels="RGB", use_container_width=True)
            cap.release()
    else:
        st.info("Camera is stopped.")

st.divider()

mode = st.radio(
    "Accessibility Mode",
    ["Sound Only", "Vibration Only", "Sound + Vibration"],
    horizontal=True
)

mock_mode = st.checkbox("Mock Mode", value=True)

st.divider()

st.subheader("Camera Controls")

col_start, col_stop = st.columns(2)

with col_start:
    if st.button("Start Camera"):
        st.session_state.camera_running = True

with col_stop:
    if st.button("Stop Camera"):
        st.session_state.camera_running = False

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
