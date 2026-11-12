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
**Day 12: LLM is a Master Chef with no hands**
LLM ki antha telusu, kani okka email kooda enduku pampaledo telusa?
Endukante LLM ante hands leni oka Master Chef lantidi. Brain undi, recipes anni telusu, kani vegetable cut cheyadaniki hands levu!
Ah hands e mana "Tools & APIs" — Weather API, Gmail, WhatsApp connectivity.
Brain ki tools connect chesthene, AI real world lo panulu chestundi.

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

    model_name = st.selectbox(
        "Gemini Model",
        options=["gemini-2.5-flash", "gemini-1.5-flash", "gemini-2.5-pro"],
        index=0,
        help="gemini-2.5-flash is fast and recommended for quick creative writing."
    )
    
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
        st.session_state.generated_scripts = ""
        st.session_state.chat_messages = []
        st.session_state.final_script = ""
        st.rerun()

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
        
        response = client.models.generate_content(
            model=model_name,
            contents=contents,
            config=config
        )
        return response.text
    except Exception as e:
        st.error(f"Error calling Gemini: {e}")
        return None

# Main App Header
st.markdown('<div class="main-header">🎙️ Transcript ➔ Instagram Reel Scripts</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Convert Telugu/Tanglish lecture transcripts into viral 30-45s Instagram scripts with Gemini AI.</div>', unsafe_allow_html=True)

# Tabs
tab1, tab2, tab3 = st.tabs(["📝 1. Generate Scripts", "💬 2. Chat & Refine", "🎬 3. Final Script & Teleprompter"])

# TAB 1: GENERATE
with tab1:
    st.subheader("Step 1: Paste Your Transcript")
    
    sample_transcript_snippet = """[00:00:30] llms and drag systems అంటే ఏంటి అని అంటే నార్మల్గా llms ఎలా work అవుతాయి just టెక్స్కిని predict చేస్తూ ఉంటాయి... and llm itself is a master chef with no hands.
దీనికి work చేయడానికి hands లేవు, brain మాత్రం ఒకటి ఉంది. Hands అంటే tools - internet connectivity, gmail, whatsapp connect చేయడం...
[00:09:00] Model context protocol (MCP) acts as a universal USB-C adapter to plug chips into any pantry..."""

    transcript_input = st.text_area(
        "Raw Transcript (Telugu / English / Mix):",
        height=220,
        placeholder="Paste your rough video transcript here...",
        value=""
    )
    
    col_a, col_b = st.columns([1, 4])
    with col_a:
        generate_btn = st.button("🚀 Generate Scripts", type="primary", use_container_width=True)
    with col_b:
        if st.button("📋 Load Sample Transcript (Day 12 Snippet)"):
            transcript_input = sample_transcript_snippet
            st.rerun()

    if generate_btn:
        if not transcript_input.strip():
            st.warning("Please paste a transcript first.")
        else:
            with st.spinner("🤖 Gemini is analyzing the transcript and creating viral Tanglish scripts..."):
                generation_prompt = f"""Target Length: {reel_length}

Here is the raw lecture transcript:
\"\"\"
{transcript_input}
\"\"\"

Convert this transcript into 3 to 4 distinct, viral Instagram Reel scripts in natural Tanglish (Telugu + English). 
Follow the exact style of the provided examples (Hook -> Analogy -> Core insight -> Pro rule / Teaser).
Make each script focus on one clear concept (e.g. Master Chef with no hands, Type-C MCP adapter, Ingredients vs Recipe, or Prompt Injection).
"""
                result = call_gemini(generation_prompt)
                if result:
                    st.session_state.generated_scripts = result
                    st.session_state.final_script = result
                    # Reset chat with initial generation
                    st.session_state.chat_messages = [
                        {"role": "user", "content": f"Generate Instagram scripts for this transcript:\n{transcript_input[:400]}..."},
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
