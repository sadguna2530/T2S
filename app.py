import streamlit as st
import os
from dotenv import load_dotenv

# Load local environment variables if available
load_dotenv()

# Streamlit Page Config
st.set_page_config(
    page_title="T2S - Transcript to Instagram Scripts",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(90deg, #FF4B4B, #FF8F00, #7928CA);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        color: #888888;
        font-size: 1.05rem;
        margin-bottom: 1.5rem;
    }
    .script-box {
        background-color: #1a1c24;
        border: 1px solid #2d3139;
        border-radius: 10px;
        padding: 1.2rem;
        margin-bottom: 1rem;
    }
    .stat-badge {
        display: inline-block;
        background: #2a2e39;
        color: #00e5ff;
        padding: 0.2rem 0.6rem;
        border-radius: 6px;
        font-size: 0.85rem;
        font-weight: 600;
        margin-right: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# System Prompt tuned with few-shot Tanglish examples
SYSTEM_PROMPT = """You are an expert Instagram Reel and YouTube Shorts scriptwriter specializing in Telugu + English (Tanglish) tech and AI educational content.

Your tone is:
- Conversational, energetic, and relatable (like a friend explaining tech over tea).
- Natural spoken Tanglish (e.g., "Swiggy lo nokkina okka second lo...", "Brain undi kani hands levu", "Mee intlo taalam cheyyi").
- Simple, high-retention analogies (Swiggy, Master Chef, Type-C charger, Kitchen & Recipe, House keys).
- Clear, punchy hooks in the first 3 seconds.
- 4 to 6 concise lines max (fits 30-45 second video speaking pace).
- Ends with a memorable pro-tip/rule or next-episode teaser.

Few-shot examples of desired format:
Example 1:
**Day 5: How an app actually works**
Swiggy lo "Place order" nokkina okka second lo em jarugutundo telusa?
First: frontend, menu. Order teesukelle waiter: API. Vanta chese kitchen: backend. Store room: database.
Ee naalugu ardham aithe, AI build chese ye app aina chadavochu, fix cheyochu.
Plus oka rule: API key ante mee intlo taalam cheyyi. Evvarikee ivvakandi.

Example 2:
**Day 2: 75 years of AI history**
75 years of AI history-ni okkate class-lo cheppesam.
Antha 1950-lo okka question-tho start ayyindi: Can machines think?
Tarvata AI Winter, funding motham dry ayipoyindi. Malli 1997-lo Deep Blue, 2012-lo AlexNet.
Idi Day 2 maatrame. Repu Day 3-lo prompt engineering cheppabotunnam.

Example 3:
**Day 3: Prompt engineering**
Same AI, same tool. Kani prompt maaristhe, result motham maaripotundi.
Class-lo live-ga oka image-ni simple prompt-tho generate chesam. Tarvatha techniques use chesi generate chesam.
Idi Day 3 maatrame. Repu Day 4-lo vibe coding ante enti, Python introduction gurinchi cheptam.

Example 4:
**Day 5: LLMs and RAG Systems**
LLM ante oka master chef with no hands. Brain unna, pani cheyadaniki tools levu.
RAG system vachi, aa chef ki internet connectivity lanti hands isthundi.
Ippudu chef ki updated knowledge untundi, plus ye tool eppudu vadalo kuda telusu.
Idi Day 5 maatrame. Repu Day 6-lo MCP ante enti, daani gurinchi cheptam.

Example 5:
**Day 6: Model Context Protocol - MCP**
Model Context Protocol (MCP) ante oka universal USB-C adapter lanti di.
Idi lekapothe, prati tool ki separate ga code rayali. Unte, chips ni ye pantry lo aina plug cheyochu.
Idi Day 6 maatrame. Repu Day 7-lo AI agents ante enti, Python introduction gurinchi cheptam.

Example 6:
**Day 7: AI Agents & Prompt Injection**
AI agent ki hands unna, human approval lekunda payments lanti panulu cheyinchakudadu.
Security lekpote, prompt injection tho mee system ni break chesi data dongilinchachu.
Idi Day 7 maatrame. Repu Day 8-lo tool calling ante enti, Python introduction gurinchi cheptam.

When given a transcript:
1. Extract the best high-retention angles/ideas.
2. Produce 3 distinct Instagram Reel scripts in this exact Tanglish format.
3. Label each script clearly with a catchy title, Hook, Core Analogy, and Takeaway.
"""

# Initialize Session State
if "api_key" not in st.session_state:
    st.session_state.api_key = os.getenv("GEMINI_API_KEY", "")

if "generated_scripts" not in st.session_state:
    st.session_state.generated_scripts = ""

if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []

if "final_script" not in st.session_state:
    st.session_state.final_script = ""

if "transcript_text" not in st.session_state:
    st.session_state.transcript_text = ""

# Sidebar for Config & API Key
with st.sidebar:
    st.title("⚙️ Gemini Settings")
    
    # Check secrets or env first
    default_key = ""
    try:
        if "GEMINI_API_KEY" in st.secrets:
            default_key = st.secrets["GEMINI_API_KEY"]
    except Exception:
        pass

    if not default_key:
        default_key = os.getenv("GEMINI_API_KEY", "")
    if not default_key and st.session_state.api_key:
        default_key = st.session_state.api_key
        
    api_key_input = st.text_input(
        "Gemini API Key", 
        type="password", 
        value=default_key,
        help="Get a free key from Google AI Studio: https://aistudio.google.com"
    )
    if api_key_input:
        st.session_state.api_key = api_key_input

    models_list = [
        "gemini-3.8-flash",
        "gemini-3.5-flash-lite",
        "gemini-3.6-flash",
        "gemini-3.1-flash-lite",
        "gemini-2.0-flash",
        "gemini-1.5-flash",
        "Custom model..."
    ]
    
    selected_option = st.selectbox(
        "Gemini Model",
        options=models_list,
        index=0,
        help="Google AI Studio models. If one is unavailable, the app will offer fallbacks."
    )
    
    if selected_option == "Custom model...":
        model_name = st.text_input("Enter Model ID:", value="gemini-3.5-flash-lite")
    else:
        model_name = selected_option
    
    reel_length = st.select_slider(
        "Target Reel Duration",
        options=["30 seconds (Quick Hook)", "45 seconds (Standard)", "60 seconds (Detailed)"],
        value="45 seconds (Standard)"
    )
    
    st.markdown("---")
    st.markdown("""
    ### 📱 Quick Tips for Viral Reels
    - **Hook in first 2 seconds**: Start with a question or surprising statement.
    - **One concept per Reel**: Master Chef, Type-C, or Recipe.
    - **Tanglish balance**: 60% Telugu flow, 40% English tech terms.
    """)
    
    if st.button("🧹 Clear Conversation & Reset", use_container_width=True):
        st.session_state.transcript_text = ""
        st.session_state.generated_scripts = ""
        st.session_state.chat_messages = []
        st.session_state.final_script = ""
        st.rerun()

# Helper to detect audio MIME type
def get_mime_type(uploaded_file):
    if hasattr(uploaded_file, "type") and uploaded_file.type:
        return uploaded_file.type
    name = uploaded_file.name.lower()
    if name.endswith(".mp3"):
        return "audio/mp3"
    elif name.endswith(".wav"):
        return "audio/wav"
    elif name.endswith(".m4a"):
        return "audio/m4a"
    elif name.endswith(".ogg"):
        return "audio/ogg"
    elif name.endswith(".aac"):
        return "audio/aac"
    elif name.endswith(".mp4"):
        return "video/mp4"
    elif name.endswith(".mov"):
        return "video/quicktime"
    return "audio/mp3"

# Helper function to transcribe audio with Gemini
def transcribe_audio_with_gemini(audio_bytes, mime_type: str):
    key = st.session_state.api_key
    if not key:
        st.error("⚠️ Please enter your Gemini API Key in the sidebar or set GEMINI_API_KEY secret.")
        return None
        
    try:
        from google import genai
        from google.genai import types
        
        client = genai.Client(api_key=key)
        
        part = types.Part.from_bytes(
            data=audio_bytes,
            mime_type=mime_type
        )
        
        transcribe_prompt = """You are an advanced speech-to-text AI model.
Please transcribe the spoken content in this audio recording accurately.

Guidelines:
1. Accurately transcribe spoken Telugu, English, and natural Tanglish (Telugu mixed with English).
2. Automatically filter out conversational filler words ('ums', 'uhs', 'ahs', throat clearing, false starts, and accidental repetitions).
3. Preserve all technical terms (API, LLM, RAG, MCP, Database, Backend, Frontend, Server, Tokens, Cloud) and speaker analogies.
4. Add rough timestamps (e.g. [00:00], [00:30]) or logical paragraph breaks where topics transition.
5. Return the clean transcript text directly without introductory fluff.
"""
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=[part, transcribe_prompt]
            )
            return response.text
        except Exception as api_err:
            err_str = str(api_err)
            if any(term in err_str.upper() for term in ["NOT_FOUND", "404", "UNAVAILABLE", "NOT AVAILABLE", "RESOURCE_EXHAUSTED"]):
                st.warning(f"⚠️ Model `{model_name}` had an issue ({err_str[:90]}...). Trying fallback models...")
                candidate_models = ["gemini-3.8-flash", "gemini-3.5-flash-lite", "gemini-3.6-flash", "gemini-2.0-flash", "gemini-1.5-flash"]
                for fb in candidate_models:
                    if fb == model_name:
                        continue
                    try:
                        fb_response = client.models.generate_content(
                            model=fb,
                            contents=[part, transcribe_prompt]
                        )
                        st.success(f"✅ Transcribed successfully using fallback model `{fb}`!")
                        return fb_response.text
                    except Exception:
                        continue
            st.error(f"Error transcribing audio: {api_err}")
            return None
    except Exception as e:
        st.error(f"Error initializing Gemini client: {e}")
        return None

# Helper function to call Gemini
def call_gemini(prompt: str, chat_history=None):
    key = st.session_state.api_key
    if not key:
        st.error("⚠️ Please enter your Gemini API Key in the sidebar or set GEMINI_API_KEY secret.")
        return None
        
    try:
        from google import genai
        from google.genai import types
        
        client = genai.Client(api_key=key)
        
        # Build contents from history if in chat mode
        contents = []
        if chat_history:
            for msg in chat_history:
                contents.append(types.Content(
                    role="user" if msg["role"] == "user" else "model",
                    parts=[types.Part.from_text(text=msg["content"])]
                ))
            contents.append(types.Content(
                role="user",
                parts=[types.Part.from_text(text=prompt)]
            ))
        else:
            contents = prompt

        config = types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            temperature=0.8,
        )
        
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=contents,
                config=config
            )
            return response.text
        except Exception as api_err:
            err_str = str(api_err)
            # If model is unavailable / not found, try available fallbacks automatically
            if any(term in err_str.upper() for term in ["NOT_FOUND", "404", "UNAVAILABLE", "NOT AVAILABLE", "RESOURCE_EXHAUSTED"]):
                st.warning(f"⚠️ Model `{model_name}` had an issue ({err_str[:90]}...). Trying fallback models...")
                candidate_models = ["gemini-3.5-flash-lite", "gemini-3.6-flash", "gemini-3.1-flash-lite", "gemini-2.0-flash", "gemini-1.5-flash"]
                for fb in candidate_models:
                    if fb == model_name:
                        continue
                    try:
                        fb_response = client.models.generate_content(
                            model=fb,
                            contents=contents,
                            config=config
                        )
                        st.success(f"✅ Generated successfully using fallback model `{fb}`!")
                        return fb_response.text
                    except Exception:
                        continue
            # If all fallbacks fail or another error occurred, show the exact error
            st.error(f"Error calling Gemini: {api_err}")
            return None
    except Exception as e:
        st.error(f"Error initializing Gemini client: {e}")
        return None

# Main App Header
st.markdown('<div class="main-header">🎙️ Transcript ➔ Instagram Reel Scripts</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Convert Telugu/Tanglish lecture transcripts into viral 30-45s Instagram scripts with Gemini AI.</div>', unsafe_allow_html=True)

# Tabs
tab1, tab2, tab3 = st.tabs(["🎙️ 1. Input & Transcribe", "💬 2. Chat & Refine", "🎬 3. Final Script & Teleprompter"])

# TAB 1: INPUT & TRANSCRIBE
with tab1:
    st.subheader("Step 1: Provide Audio or Transcript")
    
    sample_transcript_snippet = """[00:00:30] llms and drag systems అంటే ఏంటి అని అంటే నార్మల్గా llms ఎలా work అవుతాయి just టెక్స్కిని predict చేస్తూ ఉంటాయి... and llm itself is a master chef with no hands.
దీనికి work చేయడానికి hands లేవు, brain మాత్రం ఒకటి ఉంది. Hands అంటే tools - internet connectivity, gmail, whatsapp connect చేయడం...
[00:09:00] Model context protocol (MCP) acts as a universal USB-C adapter to plug chips into any pantry..."""

    input_method = st.radio(
        "Choose Input Method:",
        ["🎙️ Audio / Voice Input (Gemini Speech-to-Text)", "✍️ Paste Text Transcript"],
        horizontal=True
    )
    
    if input_method == "🎙️ Audio / Voice Input (Gemini Speech-to-Text)":
        audio_choice = st.radio(
            "Audio Source:",
            ["📁 Upload Audio/Video File", "🎤 Record Live Voice (Microphone)"],
            horizontal=True
        )
        
        audio_bytes = None
        mime_type = "audio/mp3"
        
        if audio_choice == "📁 Upload Audio/Video File":
            uploaded_file = st.file_uploader(
                "Upload voice note, lecture recording, or video:",
                type=["mp3", "wav", "m4a", "ogg", "aac", "mp4", "mov"],
                help="Gemini automatically transcribes and filters out filler words ('ums', 'uhs')."
            )
            if uploaded_file is not None:
                audio_bytes = uploaded_file.read()
                mime_type = get_mime_type(uploaded_file)
                st.audio(audio_bytes, format=mime_type)
        else:
            voice_recording = st.audio_input("Tap microphone to record voice note:")
            if voice_recording is not None:
                audio_bytes = voice_recording.read()
                mime_type = "audio/wav"
                st.audio(audio_bytes, format="audio/wav")
                
        if audio_bytes is not None:
            col_t1, col_t2 = st.columns([1, 1])
            with col_t1:
                transcribe_btn = st.button("🎧 1. Transcribe Audio (Gemini STT)", type="primary", use_container_width=True)
            with col_t2:
                transcribe_and_gen_btn = st.button("⚡ Transcribe & Generate Reel Scripts Directly", use_container_width=True)
                
            if transcribe_btn or transcribe_and_gen_btn:
                with st.spinner("🤖 Gemini Speech-to-Text is transcribing and removing filler words ('ums', 'uhs')..."):
                    transcript_res = transcribe_audio_with_gemini(audio_bytes, mime_type)
                    if transcript_res:
                        st.session_state.transcript_text = transcript_res
                        st.success("✨ Audio transcribed cleanly!")
                        if transcribe_and_gen_btn:
                            with st.spinner("🚀 Generating Instagram scripts..."):
                                gen_prompt = f"""Target Length: {reel_length}

Here is the raw lecture transcript:
\"\"\"
{transcript_res}
\"\"\"

Convert this transcript into 3 to 4 distinct, viral Instagram Reel scripts in natural Tanglish (Telugu + English). 
Follow the exact style of the provided examples (Hook -> Analogy -> Core insight -> Pro rule / Teaser).
Make each script focus on one clear concept.
"""
                                script_res = call_gemini(gen_prompt)
                                if script_res:
                                    st.session_state.generated_scripts = script_res
                                    st.session_state.final_script = script_res
                                    st.session_state.chat_messages = [
                                        {"role": "user", "content": f"Generate Instagram scripts for this transcript:\n{transcript_res[:400]}..."},
                                        {"role": "assistant", "content": script_res}
                                    ]
                                    st.success("🎬 Scripts generated! Check below or head to 'Chat & Refine'.")

    else:
        # Paste Text Transcript
        col_s1, col_s2 = st.columns([3, 1])
        with col_s2:
            if st.button("📋 Load Sample (Day 12 Snippet)"):
                st.session_state.transcript_text = sample_transcript_snippet
                st.rerun()

    # Shared Editable Transcript Area
    st.markdown("#### 📜 Transcript (Review / Edit):")
    edited_transcript = st.text_area(
        "Transcript Content:",
        value=st.session_state.transcript_text,
        height=180,
        placeholder="Paste your transcript or transcribe audio/voice note above...",
        key="transcript_area"
    )
    st.session_state.transcript_text = edited_transcript

    if st.button("🚀 Generate Instagram Scripts", type="primary", use_container_width=True):
        if not edited_transcript.strip():
            st.warning("Please provide a transcript or record/upload audio first.")
        else:
            with st.spinner("🤖 Gemini is analyzing the transcript and creating viral Tanglish scripts..."):
                generation_prompt = f"""Target Length: {reel_length}

Here is the raw lecture transcript:
\"\"\"
{edited_transcript}
\"\"\"

Convert this transcript into 3 to 4 distinct, viral Instagram Reel scripts in natural Tanglish (Telugu + English). 
Follow the exact style of the provided examples (Hook -> Analogy -> Core insight -> Pro rule / Teaser).
Make each script focus on one clear concept (e.g. Master Chef with no hands, Type-C MCP adapter, Ingredients vs Recipe, or Prompt Injection).
"""
                result = call_gemini(generation_prompt)
                if result:
                    st.session_state.generated_scripts = result
                    st.session_state.final_script = result
                    st.session_state.chat_messages = [
                        {"role": "user", "content": f"Generate Instagram scripts for this transcript:\n{edited_transcript[:400]}..."},
                        {"role": "assistant", "content": result}
                    ]
                    st.success("✨ Scripts generated successfully! Head over to 'Chat & Refine' tab to customize.")

    if st.session_state.generated_scripts:
        st.markdown("### 🎯 Generated Instagram Scripts:")
        st.markdown(st.session_state.generated_scripts)

# TAB 2: CHAT & REFINE
with tab2:
    st.subheader("Step 2: Chat with Gemini to Polish & Customize")
    st.caption("Tell the AI to make changes: 'Make script 2 punchier', 'Add a Swiggy analogy', 'Translate hook into pure Telangana slang', or 'Shorten to 30 seconds'.")
    
    # Display chat history
    for message in st.session_state.chat_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
    # Chat input
    user_prompt = st.chat_input("E.g., Can you make the MCP Type-C analogy script shorter and funnier?")
    if user_prompt:
        st.session_state.chat_messages.append({"role": "user", "content": user_prompt})
        with st.chat_message("user"):
            st.markdown(user_prompt)
            
        with st.chat_message("assistant"):
            with st.spinner("Refining script..."):
                response = call_gemini(user_prompt, chat_history=st.session_state.chat_messages[:-1])
                if response:
                    st.markdown(response)
                    st.session_state.chat_messages.append({"role": "assistant", "content": response})
                    # Update final script suggestion
                    st.session_state.final_script = response

# TAB 3: FINAL SCRIPT & TELEPROMPTER
with tab3:
    st.subheader("Step 3: Final Script & Recording Teleprompter")
    
    col1, col2 = st.columns([3, 2])
    
    with col1:
        final_text = st.text_area(
            "Final Script for Recording (Editable):",
            value=st.session_state.final_script if st.session_state.final_script else st.session_state.generated_scripts,
            height=340
        )
        st.session_state.final_script = final_text
        
        # Word count & duration calculation
        word_count = len(final_text.split()) if final_text else 0
        est_duration_sec = round((word_count / 140) * 60) # average speech rate 140 wpm
        
        st.markdown(f"""
        <span class="stat-badge">📝 Words: {word_count}</span>
        <span class="stat-badge">⏱️ Est. Reel Duration: ~{est_duration_sec} seconds</span>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown("### 📢 Post Caption & Hashtags")
        if st.button("✨ Generate Caption & Hashtags"):
            if final_text:
                with st.spinner("Generating post caption..."):
                    caption_prompt = f"""Generate an engaging Instagram Reel caption and 10 viral tech hashtags for this script:\n\n{final_text}\n\nInclude a short Telugu hook, bullet summary, and CTA (e.g. Save this for later, comment 'AI' for notes)."""
                    caption_result = call_gemini(caption_prompt)
                    if caption_result:
                        st.markdown(caption_result)
            else:
                st.warning("Generate or paste a final script first.")

        st.markdown("---")
        st.download_button(
            label="📥 Download Script as Text",
            data=final_text,
            file_name="instagram_script.txt",
            mime="text/plain",
            use_container_width=True
        )

# Footer
st.markdown("---")
st.markdown(
    "<center style='color:#777; font-size: 0.85rem;'>Built with Streamlit & Google Gemini AI • Ready for Streamlit Community Cloud (streamlit.io)</center>",
    unsafe_allow_html=True
)
