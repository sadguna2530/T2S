# 🎙️ T2S - Transcript to Instagram Scripts (Tanglish AI Studio)

A Streamlit application powered by **Google Gemini AI** that converts raw Telugu / Tanglish tech lecture transcripts into viral 30–45 second Instagram Reels and YouTube Shorts scripts.

---

## 🚀 Features

- **🎙️ Audio & Voice Input (Gemini Speech-to-Text)**:
  - **Upload Audio/Video files**: Supports MP3, WAV, M4A, OGG, AAC, MP4, and MOV (voice notes, lecture videos, meetings).
  - **Live Microphone Recording**: Tap the mic to record directly in the browser.
  - **Smart Filler Word Removal**: Gemini automatically filters out filler words ("ums", "uhs", pauses) while accurately preserving natural spoken Tanglish/Telugu.
- **Direct Transcript Ingestion**: Paste rough text transcripts or load lecture snippets.
- **Tanglish Prompt Architecture**: Specially engineered with few-shot examples to maintain high retention, conversational Telugu flow, and punchy hooks.
- **Interactive Chat & Refinement**: Chat with Gemini to tweak the hook, shorten lines, add analogies (like Swiggy, Biryani, Type-C charger), or switch slang.
- **Teleprompter & Reel Estimator**: Live word counter and estimated speaking time (~140 wpm).
- **Post Caption & Hashtags Generator**: One-click generation of Instagram captions and viral hashtags.

---

## 🛠️ Local Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-username/T2S.git
   cd T2S
   ```

2. **Create a virtual environment (optional but recommended)**:
   ```bash
   python -m venv .venv
   # Windows:
   .venv\Scripts\activate
   # Mac/Linux:
   source .venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up API Key**:
   Create a `.env` file from `.env.example`:
   ```bash
   cp .env.example .env
   ```
   Add your Gemini API key (from [Google AI Studio](https://aistudio.google.com)):
   ```env
   GEMINI_API_KEY="AIzaSy..."
   ```

5. **Run the Streamlit app**:
   ```bash
   streamlit run app.py
   ```

---

## 🌐 Deploy to Streamlit Community Cloud (streamlit.io)

1. Push your repository to **GitHub**:
   ```bash
   git init
   git add .
   git commit -m "Initial commit for T2S"
   git branch -M main
   git remote add origin https://github.com/<your-username>/<your-repo-name>.git
   git push -u origin main
   ```

2. Go to [share.streamlit.io](https://share.streamlit.io) and log in with GitHub.
3. Click **"New app"** and select:
   - **Repository**: `<your-username>/<your-repo-name>`
   - **Branch**: `main`
   - **Main file path**: `app.py`
4. In **Advanced Settings -> Secrets**, add your Gemini API key:
   ```toml
   GEMINI_API_KEY = "AIzaSy..."
   ```
5. Click **Deploy!** 🚀
