import streamlit as st
from AVChatPro.helper import *
from streamlit_lottie import st_lottie



# Streamlit UI setup
st.set_page_config(layout="wide", page_title="ChatAudio", page_icon="🔊")

# Load Lottie animation for visual enhancement
lottie_url = "https://assets5.lottiefiles.com/packages/lf20_8ov2ghzv.json"  # Customize Lottie animation URL here
lottie_json = load_lottie_url(lottie_url)

# Display Lottie animation on top of the page
if lottie_json:
    st_lottie(lottie_json, speed=1, width=600, height=400, key="animation")

st.title("Chat with Your Audio/Video ")

# Input for selecting file type (audio/video)
input_type = st.selectbox("Select Input Type", ["Select", "Audio File", "YouTube Video"])

if input_type == "Audio File":
    # Audio file upload option
    audio_file = st.file_uploader("Upload Audio File", type=["wav", "mp3"])


    if st.button("Get the Transcript"):
        if audio_file:
            # Transcribe the uploaded audio
            st.info("Processing your audio...")
            audio_filename = audio_file.name
            with open(audio_filename, "wb") as f:
                f.write(audio_file.getbuffer())
            
            transcription = assemblyai_stt(audio_filename)
            
            if transcription:
                st.info(f"Transcription: {transcription}")
                chunks = get_text_chunks(transcription)
                get_vector_store(chunks)


elif input_type == "YouTube Video":
    # YouTube video URL input option
    input_source = st.text_input("Enter the YouTube video URL")

    if st.button("Get the Transcript"):
        if input_source:
            

            
            st.info("Your uploaded video")
                
                # Display the video thumbnail
                # Check if the URL is valid and display the thumbnail
            if input_source:
                
                    # Extract the video ID correctly from both youtube.com and youtu.be URLs
                    if "youtube.com" in input_source:
                        video_id = input_source.split("v=")[1].split("&")[0]  # Extract video ID after 'v='
                    elif "youtu.be" in input_source:
                        video_id = input_source.split("/")[-1]  # Extract video ID after the last '/'
                    else:
                        raise ValueError("Invalid YouTube URL format.")
                    
                    # Display the video thumbnail
                    st.image(f"https://img.youtube.com/vi/{video_id}/0.jpg", use_column_width=True)
                    st.success(f"Video ID: {video_id}") 
                
                # Download audio and transcribe

            transcription = extract_transcript(input_source)
                
            if transcription:
                    st.info(f"Transcription: {transcription}")
                    chunks = get_text_chunks(transcription)
                    get_vector_store(chunks)

# Main question and answer section
st.subheader("Ask Your Question About the Content")

query = st.text_area("Ask your Query here...")

if st.button("Ask"):
    if query:
    
        st.info(f"Your Query is: {query}")
        result = langchain_qa(query)
        st.success(f"Answer: {result}")


# Optional decoration for styling
st.markdown("""
    <style>
    .reportview-container .main .block-container{
        padding-top: 2rem;
        padding-right: 5rem;
        padding-left: 5rem;
        padding-bottom: 2rem;
    }
    .stButton > button {
        background-color: #4CAF50;
        color: white;
        border: none;
        padding: 15px 32px;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        font-size: 16px;
        border-radius: 4px;
    }
    .stTextArea textarea {
        font-size: 18px;
        padding: 10px;
    }
    </style>
""", unsafe_allow_html=True)