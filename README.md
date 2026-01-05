# ExplainAI Pro - Automated Video Synthesis System

**Developed by:** [Ashraf Pathan]

**ExplainAI Pro** is an end-to-end AI video synthesis system that automatically converts any topic into a professional explainer video using Large Language Models, neural text-to-speech, animated diagrams, and video composition. It is designed to work with any domain—technology, science, business, or conceptual topics—without requiring manual video editing.

## Features

* **LLM-Driven Blueprint Generation:** Automatically decides scene count (3–6) using **Groq (LLaMA-3)** as the primary engine and **Google Gemini** as a fallback.
* **Neural Voice Narration:** Utilizes **Edge-TTS (Microsoft Neural Voices)** to provide natural, human-like speech without paid TTS APIs.
* **Smart Diagram Rendering:** Auto-generates blueprint-style flow diagrams (`A -> B -> C`) with dynamic layouts to prevent overlaps.
* **Animated Video Output:** Produces MP4 videos with subtle Ken-Burns style motion, fade transitions, and auto-synced visuals.
* **Production-Safe Rendering:** Audio is trimmed after effects to prevent crashes, and temporary files are automatically cleaned up.
* **Editable Scene Workflow:** Allows users to edit narration, visuals, and timing before final rendering.
* **Downloadable Script Draft:** Narration scripts, visual descriptions, and durations can be downloaded in CSV format.
* 
## 🎥 Demo Output

[![Watch the Demo Of Output](https://drive.google.com/file/d/1uvF3jWQbZhYCtNPgt6LUQDrtObRZghR0/view?usp=sharing)
## Prerequisites

* **Python 3.9** or higher
* **FFmpeg** (Required for MoviePy, must be available in PATH)
* **API Keys:** Groq Cloud API and Google Generative AI

## Setup

1.  **Clone the Repository:**
    ```bash
    git clone <repo-url>
    cd ExplainAI
    ```

2.  **Install Requirements:**
    ```bash
    pip install -r requirements.txt
    ```
    *(Dependencies: streamlit, moviepy, groq, google-generativeai, edge-tts, pillow, imageio-ffmpeg)*

3.  **Configure API Keys:**
    Create a `secrets.json` file in the root directory:
    ```json
    {
      "groq_api_key": "gsk_...",
      "gemini_api_key": "AIza..."
    }
    ```

4.  **Run:**
    ```bash
    streamlit run app.py
    ```

## Workflow (How to Run)

1.  **Launch:** Run the application command (`streamlit run app.py`).
2.  **Input:** Enter a topic (e.g., "OAuth 2.0 Flow").
3.  **Draft:** Click "Draft Blueprint". The AI generates a multi-scene explanation.
4.  **Edit:** Review and edit the narration or visuals if needed.
5.  **Render:** Click "Render Final Video". The system generates and displays the final MP4 video.

## File Structure

* `app.py`: Main application script containing the UI logic (Streamlit), AI integration, and video rendering pipeline.
* `secrets.json`: Stores sensitive API keys (Groq and Gemini) securely (ignored by Git).
* `requirements.txt`: Lists all Python dependencies required to run the project.
* `.gitignore`: Specifies files and directories to be ignored by Git (e.g., secrets, temporary files).
* `assets/`: Directory for storing static assets like background music (`bg_music.mp3`).
* `README.md`: Project documentation and setup instructions.

## Challenges Solved

* **Audio/Video Desync:** Refactored the rendering pipeline to strictly bind clip duration to `audio_clip.duration`, preventing crashes when video effects extended beyond the audio file.
* **JSON Parsing Errors:** Implemented a regex-based `clean_json_output()` middleware to strip Markdown from "chatty" LLM outputs.
* **Text Rendering:** Removed horizontal grid lines to ensure text appears clean and readable (preventing the "struck-through" look).
* **Timing Crashes:** Audio is trimmed after effects are applied to prevent `Accessing time t=` crashes in MoviePy.

## System Architecture

```text
 User Topic
     ↓    
 Groq (LLaMA-3)  →  Gemini (Fallback)
     ↓    
 Scene Blueprint (JSON)
     ↓       
 Edge-TTS Narration
     ↓       
 Diagram Renderer (PIL)
     ↓
 Animated Video (MoviePy)
     ↓
 Final MP4 Output
