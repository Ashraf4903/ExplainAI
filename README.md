It is designed to work with any domain — technology, science, business, or conceptual topics — without requiring manual video editing.

 -## **LLM-Driven Blueprint Generation**
  - Primary: **Groq (LLaMA-3)**
  - Fallback: **Google Gemini**
  - Automatically decides scene count (3–6)

-## **Neural Voice Narration**
  - Uses **Edge-TTS (Microsoft Neural Voices)**
  - Natural, human-like speech
  - No paid TTS APIs required

-## **Smart Diagram Rendering**
  - Auto-generated flow diagrams (`A -> B -> C`)
  - Dynamic layout to prevent overlaps
  - Blueprint-style visuals

-## **Animated Video Output**
  - Subtle Ken-Burns style motion
  - Fade-in / fade-out transitions
  - Auto-synced visuals with narration

-## **Background Music Support**
  - Optional royalty-free background music
  - Automatically mixed at low volume

-## **Editable Scene Workflow**
  - Edit narration, visuals, and timing before rendering

-## **Production-Safe Rendering**
  - Audio trimmed after effects
  - Prevents MoviePy timing crashes
  - Automatic cleanup of temporary files

-## **Downloadable Script draft**
  - The narration script, visual script and the duration can be downloaded in CSV format 


🔑 API Keys Setup

Create a secrets.json file in the project root:

{
  "groq_api_key": "YOUR_GROQ_API_KEY",
  "gemini_api_key": "YOUR_GEMINI_API_KEY"
}

Supported Models

Groq → Primary (fast, free tier)

Gemini → Automatic fallback

## 🚀 How to Run

1.  **Clone the Repository**
    ```bash
    git clone <repo-url>
    cd ExplainAI
    ```

2.  **Install Requirements**
    ```bash
    pip install -r requirements.txt
    ```
    *(Dependencies: streamlit, moviepy, groq, google-generativeai, edge-tts, pillow,imageio-ffmpeg)*

    ⚠️ FFmpeg is required for MoviePy
    Make sure it’s installed and available in PATH.

3.  **Configure API Keys**
    Create a `secrets.json` file in the root directory:
    ```json
    {
      "groq_api_key": "gsk_...",
      "gemini_api_key": "AIza..."
    }
    ```

4.  **Launch Application**
    ```bash
    streamlit run app.py
    ```

- **How It Works**
  -Enter a topic (e.g. OAuth 2.0 Flow)
  -Click Draft Blueprint
  -AI generates a multi-scene explanation
  -Edit narration or visuals if needed
  -Click Render Final Video
  -MP4 video is generated and displayed

## ⚠️ Challenges Solved

* **Audio/Video Desync:** Early versions crashed when video effects (Zoom) extended clip duration beyond the audio file. **Solution:** Refactored the rendering pipeline to strictly bind clip duration to `audio_clip.duration` before applying effects.
* **JSON Parsing Errors:** LLMs often output "chatty" text. **Solution:** Implemented a regex-based `clean_json_output()` middleware to strip Markdown before parsing.
* **Text Appears Crossed / Struck:**Horizontal grid lines removed.Text rendering remains clean
* **MoviePy Audio Timing Errors:** Audio is trimmed after effects.Prevents Accessing time t= crashes

## **Future Scope**
* Add support for multi-speaker dialogue.
* Implement "Code Block" visualization for programming topics.
* More Visualtion editing options can be added with a custom details box for user
* Scene-level camera motion
* Dockerized deployment
* Cloud rendering support


## **System Architecture**
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

## **Project Structure**
ExplainAI-Pro/
│
├── app.py                # Main Streamlit application
├── secrets.json          # API keys (not committed)
├── assets/
│   └── bg_music.mp3      # Optional background music
├── README.md


👨 **Author**
- Ashraf Pathan