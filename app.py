import streamlit as st
import cv2
import numpy as np
import time


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
if "label" not in st.session_state:
    st.session_state.label = "clear"
if "confidence" not in st.session_state:
    st.session_state.confidence = 0.0
if "last_detection_time" not in st.session_state:
    st.session_state.last_detection_time = 0
if "last_label" not in st.session_state:
    st.session_state.last_label = "clear"

# --- Controls ---
mode = st.radio(
    "Accessibility Mode",
    ["Sound Only", "Vibration Only", "Sound + Vibration"],
    horizontal=True
)

mock_mode = st.checkbox("Mock Mode", value=True)

# --- Mock Detection Controls (only shown when mock mode is on) ---
if mock_mode:
    label = st.selectbox("Mock Label", ["clear", "step", "curb", "object"])
    confidence = st.slider("Mock Confidence", 0.0, 1.0, 0.92, 0.01)
    st.session_state.label = label
    st.session_state.confidence = confidence

st.divider()

# --- Layout ---
left, right = st.columns([2, 1])

with left:
    st.subheader("Camera View")

    col_start, col_stop = st.columns(2)

    with col_start:
        if st.button("Start Camera"):
            st.session_state.camera_running = True

    with col_stop:
        if st.button("Stop Camera"):
            st.session_state.camera_running = False

    frame_placeholder = st.empty()

    if st.session_state.camera_running:
        cap = cv2.VideoCapture(0)

        try:
            while st.session_state.camera_running:
                ret, frame = cap.read()
                if not ret:
                    st.error("Failed to read frame.")
                    break

                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame_placeholder.image(frame, channels="RGB", use_container_width=True)

                if not mock_mode:
                    current_time = time.time()
                    if current_time - st.session_state.last_detection_time > 0.5:
                        result = analyze_frame(frame)
                        st.session_state.label = result["label"]
                        st.session_state.confidence = result["confidence"]
                        st.session_state.last_detection_time = current_time

                time.sleep(0.03)  # ~30 FPS safe delay
        finally:
            cap.release()
    else:
        st.info("Camera is stopped.")

with right:
    st.subheader("Detection Status")
    if st.session_state.label == "clear":
        st.success("CLEAR")
    else:
        st.error(st.session_state.label.upper())

    st.write(f"Confidence: {format_confidence(st.session_state.confidence)}")

# Trigger feedback (sound + simulated vibration)
if st.session_state.label != st.session_state.last_label:
    feedback = trigger_feedback(st.session_state.label, mode)
    st.session_state.last_label = st.session_state.label
else:
    feedback = {"pattern": []}

if mode in ("Vibration Only", "Sound + Vibration") and st.session_state.label != "clear":
    st.warning(f"Simulated vibration pattern (ms): {feedback['pattern']}")
