import streamlit as st
from AVChatPro.helper import *
from streamlit_lottie import st_lottie
import requests

# Function to load Lottie animation
def load_lottie_url(url):
    r = requests.get(url)
    if r.status_code == 200:
        return r.json()
    return None

# Page Configuration
st.set_page_config(page_title="Audio & Video Chat", layout="wide", page_icon="🔊")

# Sidebar - User Input
st.sidebar.header("🎤 Input Selection")
lottie_url = "https://assets5.lottiefiles.com/packages/lf20_8ov2ghzv.json"
lottie_json = load_lottie_url(lottie_url)

if lottie_json:
    st.sidebar.lottie(lottie_json, speed=1, width=250, height=200, key="animation")

input_type = st.sidebar.radio("Select Input Type", ["🎵 Audio File", "📹 YouTube Video"])

if input_type == "🎵 Audio File":
    audio_file = st.sidebar.file_uploader("Upload an Audio File", type=["wav", "mp3"])
    process_btn = st.sidebar.button("📜 Get Transcript")

elif input_type == "📹 YouTube Video":
    input_source = st.sidebar.text_input("Paste YouTube Video Link")
    process_btn = st.sidebar.button("📜 Get Transcript")

# Main Section - Chat Display
st.markdown("""
    <h1 style='text-align: center; color: #4A90E2;'>🔊 Chat with Your Audio/Video</h1>
    <p style='text-align: center; font-size: 18px;'>Interact with AI through audio and video inputs</p>
    <hr style='border: 1px solid #4A90E2;'>
    """, unsafe_allow_html=True)

if process_btn:
    if input_type == "🎵 Audio File" and audio_file:
        st.info("⏳ Processing your audio... Please wait.")
        audio_filename = audio_file.name
        with open(audio_filename, "wb") as f:
            f.write(audio_file.getbuffer())
        transcription = assemblyai_stt(audio_filename)
        if transcription:
            st.success("✅ Transcription Complete!")
            st.text_area("📝 Transcription Output:", transcription, height=150)
            chunks = get_text_chunks(transcription)
            get_vector_store(chunks)
    elif input_type == "📹 YouTube Video" and input_source:
        st.info("🔍 Fetching video details...")
        transcription = extract_transcript(input_source)
        if transcription:
                st.success("Transcription Complete!")
                st.text_area("Transcription Output:", transcription, height=150)
                chunks = get_text_chunks(transcription)
                get_vector_store(chunks)
        else:
            st.error("❌ Invalid YouTube URL. Please enter a valid YouTube link.")
    else:
        st.warning("⚠️ Please provide a valid input before proceeding.")

# Q&A Section
st.divider()
st.subheader("💬 Ask a Question About the Content")
query = st.text_area("❓ Type your query here...", height=100)

if st.button("🤖 Ask"):
    if query:
        st.info(f"🗨️ Your Query: {query}")
        result = langchain_qa(query)
        st.success(f"✅ Answer: {result}")
    else:
        st.warning("⚠️ Please enter a question before submitting.")

