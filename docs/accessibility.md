# Multimodal Accessibility Logic

## Why Single-Mode Fails
Standard navigation apps rely heavily on **Audio** (Voiceover) or **Visuals** (Maps). This fails for:
- **Deaf-Blind Users:** Who cannot see maps or hear instructions.
- **Situational Disabilities:** A user walking near a loud construction site (Audio fails).

## Our Solution: Sensory Translation
We decouple "Detection" from "Feedback". The AI sees the world, but the *User* decides how to experience it.

### Modes
1.  **Sound + Vibration:**
    - *Best for:* Visually Impaired users.
    - *Feedback:* Spoken alerts ("Step Ahead") + Haptic Pulse.
    
2.  **Vibration Only (Haptic):**
    - *Best for:* Deaf-Blind users or noisy environments.
    - *Feedback:* Distinct vibration patterns for different hazards.
    - *Pattern 1 (Step):* Short-Short-Long (.._)
    - *Pattern 2 (Obstacle):* Heavy Buzz (___)

3.  **Sound Only (Default):**
    - *Best for:* Users with motor impairments sensitive to vibration.
    - *Feedback:* Clear, high-priority audio alerts.

4.  **Elderly Users:**
    - *Best for:* Older adults with declining vision, hearing, or mobility.
    - *Why it helps:* Falls from curbs and steps are a leading cause of injury in the elderly. Our system provides early, multi-sensory warnings that are:
      - **Loud and clear** (Sound mode with slower speech rate)
      - **Haptic** (Vibration for those with hearing loss)
      - **High contrast UI** and **Large Font** mode for caregivers or the user themselves
    - *Use case:* An elderly person walking with a cane receives a vibration pulse 2 seconds before reaching a curb, giving them time to stop safely.

5. **UI Accessibility**
We implemented "Accessibility-First" design patterns directly in the interface:
* **High Contrast Mode:** Switches to a pure Black/Yellow theme (WCAG AAA compliant colors) for users with Photophobia or low vision.
* **Large Font Mode:** Instantly scales text by 130% for elderly users.
