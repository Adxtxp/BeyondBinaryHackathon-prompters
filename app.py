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
if "demo_mode" not in st.session_state:
    st.session_state.demo_mode = False
if "_auto_mock" not in st.session_state:
    st.session_state._auto_mock = False

# --- Controls ---
st.subheader("⚙️ Settings")

col1, col2, col3 = st.columns(3)

with col1:
    high_contrast = st.checkbox("🌓 High Contrast", help="Toggle high contrast mode for better visibility")
    
with col2:
    large_font = st.checkbox("🔍 Large Font", help="Increase font size for better readability")
    
with col3:
    demo_mode = st.checkbox("🎬 Demo Mode", value=st.session_state.demo_mode, help="One-tap demo with pre-configured settings")

# Apply High Contrast CSS
if high_contrast:
    st.markdown("""
        <style>
            body {
                background-color: #000000;
                color: #FFFFFF;
            }
            .stApp {
                background-color: #000000;
            }
            div[data-testid="stSidebar"] {
                background-color: #111111;
            }
            h1, h2, h3, h4, h5, h6, p, span, label {
                color: #FFFFFF !important;
            }
            .stButton>button {
                background-color: #FFFF00;
                color: #000000;
                font-weight: bold;
            }
            .stCheckbox label {
                color: #FFFFFF !important;
            }
        </style>
    """, unsafe_allow_html=True)

# Apply Large Font CSS
if large_font:
    st.markdown("""
        <style>
            body, p, span, div, label {
                font-size: 1.3rem !important;
            }
            h1 { font-size: 3rem !important; }
            h2 { font-size: 2.5rem !important; }
            h3 { font-size: 2rem !important; }
            .stButton>button {
                font-size: 1.5rem !important;
                padding: 0.75rem 1.5rem !important;
            }
        </style>
    """, unsafe_allow_html=True)

mode = st.radio(
    "Accessibility Mode",
    ["Sound Only", "Vibration Only", "Sound + Vibration"],
    horizontal=True
)

# Re-trigger feedback on mode change (demo UX fix)
if "last_mode" not in st.session_state:
    st.session_state.last_mode = mode

if mode != st.session_state.last_mode:
    if st.session_state.label != "clear":
        trigger_feedback(st.session_state.label, mode)
    st.session_state.last_mode = mode

# Demo mode pre-sets
if demo_mode:
    mock_mode = True
    st.session_state.demo_mode = True
    st.session_state["mock_mode"] = True      # sync for vision.py
    st.info("🎬 Demo Mode Active - Using simulated detections")
    
    # Demo mode preset values - fixed to demonstrate obstacle detection
    label = "step"
    confidence = 0.92
    st.session_state.label = label
    st.session_state.confidence = confidence
    
    st.caption("💡 Preset: Detecting a **STEP** with 92% confidence")
else:
    mock_mode = st.checkbox("Mock Mode", value=False)
    st.session_state.demo_mode = False
    st.session_state["mock_mode"] = mock_mode  # sync for vision.py
    st.session_state._auto_mock = False         # clear auto-fallback flag

# --- Mock Detection Controls (only shown when mock mode is on) ---
if mock_mode and not demo_mode:
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
                frame_placeholder.image(frame, channels="RGB", width="stretch")

                if not mock_mode and not demo_mode:
                    current_time = time.time()
                    if current_time - st.session_state.last_detection_time > 0.5:
                        print("ANALYZE CALLED")
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
    
    # Clear color coding: Green → clear, Yellow → object, Red → step/curb
    if st.session_state.label == "clear":
        st.markdown(
            '<div style="background-color: #28a745; color: white; padding: 20px; border-radius: 10px; text-align: center; font-size: 2rem; font-weight: bold;">✅ CLEAR</div>',
            unsafe_allow_html=True
        )
    elif st.session_state.label == "object":
        st.markdown(
            '<div style="background-color: #ffc107; color: black; padding: 20px; border-radius: 10px; text-align: center; font-size: 2rem; font-weight: bold;">⚠️ OBJECT</div>',
            unsafe_allow_html=True
        )
    else:  # step or curb
        st.markdown(
            f'<div style="background-color: #dc3545; color: white; padding: 20px; border-radius: 10px; text-align: center; font-size: 2rem; font-weight: bold;">🚨 {st.session_state.label.upper()}</div>',
            unsafe_allow_html=True
        )

    st.markdown("<br>", unsafe_allow_html=True)
    st.progress(int(st.session_state.confidence * 100))
    st.caption(f"Confidence: {format_confidence(st.session_state.confidence)}")
    
    print("camera_running:", st.session_state.camera_running)
    print("mock_mode (local):", mock_mode)
    print("st.session_state['mock_mode']:", st.session_state.get("mock_mode", False))
    print("demo_mode:", demo_mode)
    print("confidence:", st.session_state.confidence)
    
    if st.session_state.camera_running and not mock_mode:
        st.info("🔄 Analyzing environment...")
    
    if st.session_state.get("_auto_mock", False):
        st.warning("⚠️ Detection failed repeatedly — auto-switched to Mock Mode for stability.")
    
    # --- Visual Vibration Simulation ---
    if mode in ("Vibration Only", "Sound + Vibration") and st.session_state.label != "clear":
        st.markdown("""
            <div style="
                background-color: #222222;
                border: 3px dashed #ff4444;
                padding: 20px;
                margin-top: 15px;
                text-align: center;
                font-size: 1.5rem;
                font-weight: bold;
                color: #ff4444;
                border-radius: 10px;
                animation: pulse 1s infinite;
            ">
                📳 VIBRATION ACTIVE
            </div>

            <style>
            @keyframes pulse {
                0% { opacity: 1; }
                50% { opacity: 0.3; }
                100% { opacity: 1; }
            }
            </style>
        """, unsafe_allow_html=True)

# Trigger feedback (sound + simulated vibration)
if st.session_state.label != st.session_state.last_label:
    trigger_feedback(st.session_state.label, mode)
    st.session_state.last_label = st.session_state.label

