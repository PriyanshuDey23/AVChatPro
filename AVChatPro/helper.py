from pathlib import Path
import os
from dotenv import load_dotenv
from pytube import YouTube
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.prompts import PromptTemplate
from langchain.chains.question_answering import load_qa_chain
import assemblyai as aai
import google.generativeai as genai
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from youtube_transcript_api import YouTubeTranscriptApi
import requests

# Function to load Lottie animation
def load_lottie_url(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

# Load environment variables
load_dotenv()

# Set up API keys
ASSEMBLY_API_KEY = os.getenv('ASSEMBLY_API_KEY')
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')

# Configure Google Gemini API
genai.configure(api_key=GOOGLE_API_KEY)

# Initialize embedding model
embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

# Function to download audio from YouTube
def save_audio(url):
    yt = YouTube(url)
    video = yt.streams.filter(only_audio=True).first()
    out_file = video.download()
    base, ext = os.path.splitext(out_file)
    file_name = base + '.mp3'
    try:
        os.rename(out_file, file_name)
    except WindowsError:
        os.remove(file_name)
        os.rename(out_file, file_name)
    return Path(file_name).stem + '.mp3'

# Function for  speech-to-text (Video)
# Function to extract transcript from YouTube video
def extract_transcript(youtube_video_url):
    # Check if URL is in 'youtu.be' format and extract video ID
    if "youtu.be" in youtube_video_url:
        video_id = youtube_video_url.split("/")[-1]
    # Check if URL is in 'youtube.com' format and extract video ID
    elif "youtube.com" in youtube_video_url:
        video_id = youtube_video_url.split("v=")[1].split("&")[0]  # Ensure video ID is properly split
    else:
        raise ValueError("Invalid YouTube URL format.")
    
    # Fetch the transcript of the video
    transcript_data = YouTubeTranscriptApi.get_transcript(video_id=video_id)
    
    # Combine all the transcript texts into a single string
    transcript = " ".join([item["text"] for item in transcript_data])
    
    return transcript




# Function for Assembly AI speech-to-text (Audio)
aai.settings.api_key = ASSEMBLY_API_KEY

def assemblyai_stt(audio_file):
    transcriber = aai.Transcriber()
    config = aai.TranscriptionConfig(speaker_labels=True)
    transcript = transcriber.transcribe(audio_file, config)
    
    if transcript.status == aai.TranscriptStatus.error:
        print(f"Transcription failed: {transcript.error}")
        return None
    
    return transcript.text

# Function to split text into chunks
def get_text_chunks(text):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=1000)
    return text_splitter.split_text(text)

# Function to store chunks in a vector database
def get_vector_store(chunks):
    vectorstore = FAISS.from_texts(chunks, embedding=embeddings)
    vectorstore.save_local("faiss_index")

# Function to create the conversational chain
def get_conversational_chain(context, user_question):
    prompt_template = "Given the context: {context}, answer the following question: {user_question}"
    model = ChatGoogleGenerativeAI(model="gemini-1.5-pro-002", temperature=0.2)
    prompt = PromptTemplate(template=prompt_template, input_variables=["context", "user_question"])
    return load_qa_chain(model, chain_type="stuff", prompt=prompt)

# User input processing
def langchain_qa(user_question):
    # Load the FAISS index
    new_db = FAISS.load_local("faiss_index", embeddings=embeddings, allow_dangerous_deserialization=True)
    docs = new_db.similarity_search(user_question)
    
    # Combine the documents into a context
    context = " ".join([doc.page_content for doc in docs])
    
    # Get the conversational chain
    chain = get_conversational_chain(context, user_question)
    
    # Get the response from the chain
    response = chain(
        {"input_documents": docs, "user_question": user_question},
        return_only_outputs=True
    )
    return response["output_text"]