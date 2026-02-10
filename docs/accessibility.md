# Multimodal Accessibility Logic

## Why Single-Mode Fails
Standard navigation apps rely heavily on **Audio** (Voiceover) or **Visuals** (Maps). This fails for:
- **Deaf-Blind Users:** Who cannot see maps or hear instructions.
- **Situational Disabilities:** A user walking near a loud construction site (Audio fails).

## Our Solution: Sensory Translation
We decouple "Detection" from "Feedback". The AI sees the world, but the *User* decides how to experience it.

### Modes
1.  **Sound + Vibration (Default):**
    - *Best for:* Visually Impaired users.
    - *Feedback:* Spoken alerts ("Step Ahead") + Haptic Pulse.
    
2.  **Vibration Only (Haptic):**
    - *Best for:* Deaf-Blind users or noisy environments.
    - *Feedback:* Distinct vibration patterns for different hazards.
    - *Pattern 1 (Step):* Short-Short-Long (.._)
    - *Pattern 2 (Obstacle):* Heavy Buzz (___)

3.  **Sound Only:**
    - *Best for:* Users with motor impairments sensitive to vibration.
    - *Feedback:* Clear, high-priority audio alerts.