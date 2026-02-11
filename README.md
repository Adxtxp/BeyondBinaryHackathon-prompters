#  Multimodal Assistive Obstacle Detection
> **Problem Statement 1:** Designing an assistive solution that works across multiple abilities.

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue)](https://www.python.org/)
[![TensorFlow](https://img.shields.io/badge/TensorFlow-Keras-orange)](https://www.tensorflow.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-App-red)](https://streamlit.io/)
[![Status](https://img.shields.io/badge/Status-Prototype%20Ready-brightgreen)]()

## Table of Contents
- [The Problem (The Last Meter)](#-the-problem-the-last-meter)
- [Our Solution: Sensory Translation](#-our-solution-sensory-translation)
- [Technical Architecture (AI + Threading)](#-technical-architecture)
- [Scalability & Impact](#-scalability--impact)
- [Installation & Setup](#-installation--setup)
- [How to Use (Hybrid Mode)](#-how-to-use-hybrid-mode)

---

## The Problem: The "Last Meter" Gap
**2.2 billion people** live with vision impairments. While GPS apps (like Google Maps) excel at **Macro-Navigation** (Street-level routing), they fail at **Micro-Navigation** (Immediate hazards).

* **The "Last Meter" Problem:** GPS tells you to turn left, but not that there is a broken curb or stairs without a railing.
* **The "Deaf-Blind" Gap:** Most assistive apps rely on VoiceOver (Audio). This completely excludes users who are both deaf and blind.

---

## Our Solution: Sensory Translation
We built a **Multimodal Feedback Engine** that decouples "Detection" from "Experience."
1.  **AI Detection:** A custom Neural Network detects hazards in real-time.
2.  **Sensory Translation:** The app converts "Stairs" into the user's preferred language: **Sound**, **Vibration**, or **High-Contrast Visuals**.

---

## Technical Architecture
We prioritized **Real-Time AI**, **Privacy**, and **Offline Capability**.

### 1. Hybrid AI Engine
* **Live Detection:** We trained a **Convolutional Neural Network (CNN)** using TensorFlow Keras to detect **Stairs** and **Clear Paths** via the live webcam.
* **Offline Privacy:** The model runs locally on the CPU. No video data is sent to the cloud.

### 2. Threaded Feedback System
* **Non-Blocking Audio:** The Text-to-Speech engine runs on a background thread (`feedback.py`), ensuring the video feed never freezes while the app is speaking.
* **Cooldown Logic:** Prevents "Audio Spam" by ignoring repetitive detections for 3 seconds.

---

## Scalability & Impact
* **Hardware Agnostic:** The compressed Keras model is lightweight enough to run on mid-range smartphones ($50-$100) in developing nations.
* **Zero-Infrastructure:** Works entirely offline, making it scalable to rural areas with no internet.

---

## Installation & Setup

### Prerequisites
* Python 3.8+ 
* Webcam

### Steps
1.  **Clone the Repository**
    ```bash
    git clone https://github.com/Adxtxp/BeyondBinaryHackathon-prompters
    ```

2.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the App**
    ```bash
    streamlit run app.py
    ```

---

## How to Use (Hybrid Mode)
**For Judges:** We use a **Hybrid Demonstration** to show both our Real-Time AI and our extensive Feedback Logic.

### Phase 1: Live AI Mode (Stairs Detection)
1.  Uncheck **"Mock Mode"**.
2.  Point the camera at a real staircase (or a test image of stairs).
3.  The system will detect **"STEP"** using the Keras model and trigger an alert.

### Phase 2: Mock Mode (Scenario Testing)
*Since our current prototype model is specialized for Stairs, we use Mock Mode to demonstrate other hazards.*
1.  Check **"Mock Mode"**.
2.  Select **"Curb"** from the dropdown.
3.  **Test Accessibility:**
    * Toggle **"High Contrast"** to test low-vision support.
    * Switch to **"Vibration Only"** to see the haptic visualizer pulse for Deaf-Blind users.

---

### Hackathon Checklist
- [x] **Impact:** Addresses intersectional Deaf-Blind needs and the "Last Meter" problem.
- [x] **Technical:** Implements custom Keras Neural Network (AI) + Multithreading.
- [x] **Usability:** Includes High Contrast & Large Font modes.
- [x] **Scalability:** Offline-first architecture.

