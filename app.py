import streamlit as st
import json
import os
import re
import textwrap
import google.generativeai as genai
from PIL import Image, ImageDraw, ImageFont
import PIL.Image
from groq import Groq
import asyncio
import edge_tts
from moviepy.audio.AudioClip import CompositeAudioClip
from moviepy.video.fx.resize import resize
from moviepy.video.VideoClip import ImageClip
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.video.compositing.concatenate import concatenate_videoclips
from moviepy.video.fx.fadein import fadein
from moviepy.video.fx.fadeout import fadeout


# Fix for older Pillow versions (ensures high-quality image resizing)
if not hasattr(PIL.Image, 'ANTIALIAS'):
    PIL.Image.ANTIALIAS = PIL.Image.LANCZOS

# Setup for the Streamlit page layout
st.set_page_config(page_title="ExplainAI Pro", page_icon="⚡", layout="wide")
st.markdown("""
<style>
    /* 1. Global Text Scale - Bumps up all standard text */
    html, body, [class*="css"] {
        font-size: 26px !important; 
    }

    /* 2. Titles and Headers */
    h1 { font-size: 68px !important; }
    h2 { font-size: 38px !important; }
    h3 { font-size: 32px !important; }

    /* 3. Input Box Styling */
    .stTextInput > div > div > input {
        font-size: 26px !important;
        height: 55px !important;
        border-radius: 8px;
    }
    .stTextInput label {
        font-size: 22px !important;
        font-weight: bold;
        margin-bottom: 10px;
    }

    /* 4. Button Styling */
    .stButton > button {
        width: 100%;
        height: 55px !important;
        font-size: 22px !important;
        font-weight: 700 !important;
        border-radius: 8px;
    }

    /* 5. Data Editor / Table Styling */
    div[data-testid="stDataEditor"] table {
        font-size: 18px !important;
    }
    div[data-testid="stDataEditor"] th {
        font-size: 20px !important; /* Table Headers */
        font-weight: bold;
    }
    div[data-testid="stDataEditor"] td {
        font-size: 18px !important; /* Table Cells */
    }

    /* 6. Success/Error Messages (The Green/Red Boxes) */
    .stAlert {
        font-size: 20px !important;
    }
    
    /* 7. Hide Streamlit Footer */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)


# # ---API CONFIGURATION ---
def load_api_keys():
    try:
        with open("secrets.json", "r") as f: return json.load(f)
    except FileNotFoundError: return {}

SECRETS = load_api_keys()
GEMINI_KEY = SECRETS.get("gemini_api_key", "").strip()
GROQ_KEY = SECRETS.get("groq_api_key", "").strip()


# --- AI Dummy offline script for fallback ---
def get_fallback_script(topic):
    return [
        {
            "narration": f"We are entering Demo Mode for {topic}. Please check your API keys.", 
            "visual_text": "DEMO MODE | KEYS MISSING", 
            "duration": 5
        },
        {
            "narration": "Without a valid API key, I can only show this default visualization.", 
            "visual_text": "No Key -> Generic Output", 
            "duration": 6
        },
        {
            "narration": "Add your keys in secrets.json to unlock the full AI explanation.", 
            "visual_text": "Add Keys -> Get Intelligence", 
            "duration": 6
        }
    ]

def clean_json_output(text):
    """Helper to strip markdown and extra text from AI response"""
    text = text.replace("```json", "").replace("```", "").strip()
    # Find the first '[' and last ']' to handle chatty intros/outros
    start = text.find('[')
    end = text.rfind(']') + 1
    if start != -1 and end != -1:
        text = text[start:end]
    return text

# Blueprint Generation (Groq → Gemini → Fallback)
def get_ai_script(topic):

    system_prompt = f"""
    You are a Senior educator and systems thinker.
    Task: Create a video blueprint explaining the '{topic}' and the INTERNAL MECHANISM of: '{topic}'.
    
    You can explain ANY topic clearly by:
    - Identifying whether the topic is technical, scientific, conceptual, or procedural
    - Explaining its internal working, process flow, or underlying logic accordingly
    - Adapting language to be simple, accurate, and structured
    - Avoiding unnecessary jargon

    Your goal is to create a clear, visual, step-by-step explanation suitable for an explainer video.

    SCENE RULES:
    - **Determine the scene count yourself** based on complexity (Minimum 3, Maximum 6).
    - If the topic is simple, use 3 scenes. If complex, use 5-6 scenes.
    
    VISUAL RULES:
    - You MUST use "->" to show flow (e.g., "User -> API -> DB").
    - Keep visuals simple (max 3 nodes).
    
    Format: JSON List [{{"narration": "...", "visual_text": "A -> B", "duration": 6}}]
    """
    
    #Groq (Preferred because it's fast)
    if GROQ_KEY:
        try:
            client = Groq(api_key=GROQ_KEY)
            response = client.chat.completions.create(
                model="groq/compound",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Explain: {topic}"} # FIX: Added User Role
                ],
                temperature=0.4
            )
            raw_content = response.choices[0].message.content
            clean_content = clean_json_output(raw_content) # FIX: Apply cleaning
            return json.loads(clean_content)
        except Exception as e:
            st.sidebar.warning(f"Groq failed → {e}")

    # --- GEMINI (FALLBACK) ---
    if GEMINI_KEY:
        try:
            genai.configure(api_key=GEMINI_KEY)
            model = genai.GenerativeModel("gemini-2.5-flash")
            response = model.generate_content(system_prompt)
            clean = response.text.replace("```json", "").replace("```", "").strip()
            return json.loads(clean)
        except Exception as e:
            st.sidebar.warning(f"Gemini failed → {e}")

# If both fail then we return the demo script
    return get_fallback_script(topic)

#Used Text-to-Speech (Edge-TTS)

async def edge_tts_generate(text, filename):
    communicate = edge_tts.Communicate(
        text=text,
        voice="en-IN-NeerjaNeural",  # Natural Indian accent
        rate="+5%",
        pitch="+0Hz"
    )
    await communicate.save(filename)

def generate_voiceover(text, index):
    filename = f"temp_audio_{index}.mp3"
    asyncio.run(edge_tts_generate(text, filename))
    return filename


# Diagram Rendering Engine used for drawing diagrams
def draw_smart_diagram(draw, width, height, text, font):
    BOX_COLOR = (0, 255, 240)     # Neon Cyan
    TEXT_COLOR = (0, 0, 0)        # Black
    ARROW_COLOR = (255, 255, 255) # White

    if "->" in text:
        # Split the flow into individual nodes
        parts = text.split("->")
        parts = [p.strip() for p in parts[:3]] 
        
        
        total_group_width = 0
        nodes = [] # Stores (lines, box_w, box_h)
        
        # To Measure text size to determine box sizes
        for part in parts:
            # Wrap long text so boxes don't get too wide
            lines = textwrap.wrap(part, width=18)
            
            # Used to Find widest line in this box
            max_line_w = 0
            for line in lines:
                w = font.getlength(line)
                if w > max_line_w: max_line_w = w
            
            box_w = max_line_w + 50 # Padding sides
            box_h = (len(lines) * 50) + 40 
            
            nodes.append({"lines": lines, "w": box_w, "h": box_h})
            total_group_width += box_w
        
        # Calculate Starting X to center everything
        gap = 60
        total_width_with_gaps = total_group_width + (gap * (len(parts) - 1))
        current_x = (width - total_width_with_gaps) // 2
        y_center = height // 2
        
        # To DRAW boxes and arrows
        for i, node in enumerate(nodes):
            box_w = node["w"]
            box_h = node["h"]
            lines = node["lines"]
            
            x1 = current_x
            y1 = y_center - (box_h // 2)
            x2 = x1 + box_w
            y2 = y1 + box_h
            
            # To Draw Box
            draw.rectangle([x1, y1, x2, y2], outline=BOX_COLOR, width=5)
            
            # to centre text inside box
            text_start_y = y1 + 20
            for line in lines:
                line_w = font.getlength(line)
                line_x = x1 + (box_w - line_w) // 2 
                draw.text((line_x, text_start_y), line, font=font, fill=BOX_COLOR)
                text_start_y += 50


            # To Draw Arrow to next box
            if i < len(nodes) - 1:
                arrow_start_x = x2 + 10
                arrow_end_x = arrow_start_x + gap - 20
                draw.line([(arrow_start_x, y_center), (arrow_end_x, y_center)], fill=ARROW_COLOR, width=5)
                draw.polygon([(arrow_end_x, y_center), (arrow_end_x - 15, y_center - 10), (arrow_end_x - 15, y_center + 10)], fill=ARROW_COLOR)
                
            current_x += box_w + gap
                
    else:
        lines = textwrap.wrap(text, width=25)
        total_h = len(lines) * 80
        y = (height - total_h) // 2 
        for line in lines:
            w = font.getlength(line)
            x = (width - w) // 2
            draw.text((x, y), line, font=font, fill=BOX_COLOR)
            y += 80

def create_blueprint_image(text, filename):
    width, height = 1280, 720
    img = Image.new('RGB', (width, height), color=(15, 20, 25))
    draw = ImageDraw.Draw(img)
    
    for x in range(0, width, 40): draw.line((x, 0, x, height), fill=(25, 30, 40), width=1)
    for y in range(0, height, 40): draw.line((0, y, width, y), fill=(25, 30, 40), width=1)

    try: font = ImageFont.truetype("arial.ttf", 40) 
    except: font = ImageFont.load_default() 
    
    draw_smart_diagram(draw, width, height, text, font)
    img.save(filename)

# Used for MOTION EFFECTS

def slide_up_effect(clip):
    # Moves the image slightly up over time 
    return clip.set_position(lambda t: ('center', 'center'))


# Used for video rendering 
def render_video(blueprint, topic_name):
    clips = []
    progress_bar = st.progress(0)
    status_text = st.empty()
    temp_files = []

    for i, scene in enumerate(blueprint):
        progress_bar.progress((i + 1) / len(blueprint))
        status_text.markdown(f"**⚡ Rendering Scene {i+1}...**")
        
        audio_path = generate_voiceover(scene["narration"], i)
        temp_files.append(audio_path)
        audio_clip = AudioFileClip(audio_path)
        
        viz_path = f"temp_viz_{i}.png"
        create_blueprint_image(scene["visual_text"], viz_path)
        temp_files.append(viz_path)

        duration = audio_clip.duration

        clip = ImageClip(viz_path).set_duration(duration)
        clip = clip.set_audio(audio_clip)
        clip = clip.set_position(('center', 'center'))
        clip = fadein(clip, 0.4)
        clip = fadeout(clip, 0.4)
        
        clips.append(clip)
    status_text.text("Stitching Final Video...")
    final_video = concatenate_videoclips(clips, method="compose")

    # Add background music if available
    bg = "assets/bg_music.mp3"
    if os.path.exists(bg):
            music = AudioFileClip(bg).volumex(0.04).set_duration(final_video.duration)
            final_video = final_video.set_audio(CompositeAudioClip([final_video.audio, music]))

    ## creating filename for saving the file
    clean_name = re.sub(r'[^a-zA-Z0-9_]', '', topic_name.strip().replace(" ", "_"))
    output_filename = f"ExplainAI_{clean_name}.mp4"
    
    final_video.write_videofile(output_filename, fps=24)
    
    for f in temp_files: 
        if os.path.exists(f): os.remove(f)
            
    return output_filename
    
    


st.title("ExplainAI")
st.markdown("**Automated Video Generation**")

with st.container():
    col1, col2 = st.columns([3, 1])
    with col1:
        topic = st.text_input("Topic to Deep Dive:", placeholder="e.g. Websockets")
    with col2:
        st.write("") 
        st.write("") 
        if st.button("✨ Draft Blueprint", type="primary"):
            with st.spinner("Analyzing Architecture..."):
                st.session_state['blueprint'] = get_ai_script(topic)
                st.session_state['current_topic'] = topic

# To Only show the editor if a blueprint has been generated
if 'blueprint' in st.session_state:
    st.divider()
    
    ## To Check if we are in Demo Mode (missing keys)
    first_slide_text = st.session_state['blueprint'][0]['visual_text']
    if "DEMO MODE" in first_slide_text:
        st.error("🚨 DEMO MODE ACTIVE: Keys missing or Quota exceeded.")
    else:
        total_duration = sum(scene['duration'] for scene in st.session_state['blueprint'])
        st.success(f" AI Generated a {len(st.session_state['blueprint'])}-Scene Blueprint |  Total Duration: {total_duration}s")

    # For making Editable Table for the User
    edited_blueprint = st.data_editor(
        st.session_state['blueprint'],
        num_rows="dynamic",
        use_container_width=True,
        column_config={
            "narration": st.column_config.TextColumn("🗣️ Narration", width="large"),
            "visual_text": st.column_config.TextColumn("📺 Visual Text (Use -> for arrows)", width="medium"),
            "duration": st.column_config.NumberColumn("⏱️ Seconds", min_value=3, max_value=60)
        }
    )
    
    st.write("")
    if st.button("🚀 Render Final Video", type="primary", use_container_width=True):
        with st.spinner("Synthesizing Diagrams..."):
            try:
                # Pass current topic to renderer
                video_file = render_video(edited_blueprint, st.session_state.get('current_topic', 'Topic'))
                st.balloons()
                st.success(f" Video Saved as: {video_file}")
                st.video(video_file)
            except Exception as e:
                st.error(f"Render Failed: {e}")