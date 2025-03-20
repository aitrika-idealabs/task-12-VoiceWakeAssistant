import streamlit as st
import requests
import os
import tempfile
import io
from io import BytesIO

# Apply custom CSS for Apple-inspired minimalist design
def apply_custom_css():
    st.markdown("""
    <style>
    /* Main container styling */
    .main .block-container {
        max-width: 900px;
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* Header styling */
    h1 {
        font-weight: 700 !important;
        text-align: center !important;
        margin-bottom: 0.5rem !important;
    }
    
    h1 span.blue-text {
        color: #3b82f6 !important;
    }
    
    /* Subtitle styling */
    .subtitle {
        color: #6b7280;
        text-align: center;
        margin-bottom: 2.5rem;
        font-size: 1.1rem;
        line-height: 1.5;
    }
    
    /* Card styling for mic interface */
    .mic-card {
        background-color: white;
        border-radius: 15px;
        padding: 3rem 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        margin: 0 auto;
        max-width: 800px;
    }
    
    /* Microphone button styling */
    .stAudio {
        margin: 0 auto;
        display: block;
    }
    
    /* Wake word input styling */
    div[data-testid="stForm"] {
        background-color: #f8fafc;
        border-radius: 12px;
        padding: 1rem;
        margin-bottom: 2rem;
        border: 1px solid #e2e8f0;
    }
    
    .stTextInput > div > div > input {
        border-radius: 12px;
    }
    
    .stButton > button {
        border-radius: 12px;
        background-color: #3b82f6;
        color: white;
        font-weight: 500;
    }
    
    /* Status message styling */
    .status-msg {
        text-align: center;
        margin: 1rem 0;
        font-size: 1.1rem;
    }
    
    # /* Hide default Streamlit elements */
    # #MainMenu {visibility: hidden;}
    # footer {visibility: hidden;}
    # .stDeployButton {display:none;}
    
    /* Checkbox styling */
    .stCheckbox {
        text-align: center;
    }
    
    /* Center text */
    .centered-text {
        text-align: center;
    }
    
    /* Audio response styling */
    .stAudio > div > div {
        margin: 0 auto;
    }
    
    </style>
    """, unsafe_allow_html=True)

# Load API credentials from Streamlit secrets
WHISPER_API_URL = st.secrets["WHISPER_API_URL"]
WHISPER_API_KEY = st.secrets["WHISPER_API_KEY"]
GPT4O_API_ENDPOINT = st.secrets["GPT4O_API_ENDPOINT"]
GPT4O_API_KEY = st.secrets["GPT4O_API_KEY"]

# Initialize session state for wake word
if 'wake_word' not in st.session_state:
    st.session_state.wake_word = "hey assistant"

if 'is_listening' not in st.session_state:
    st.session_state.is_listening = False

# Function to transcribe audio using OpenAI Whisper API
def transcribe_audio_whisper(audio_bytes):
    headers = {
        "Authorization": f"Bearer {WHISPER_API_KEY}"
    }
    
    # Handle different possible input types
    try:
        # If audio_bytes is already a file-like object
        if hasattr(audio_bytes, 'read'):
            audio_file = audio_bytes
        # If audio_bytes is bytes
        elif isinstance(audio_bytes, bytes):
            audio_file = BytesIO(audio_bytes)
        # If it's something else, try to convert it
        else:
            audio_file = BytesIO(audio_bytes)
        
        audio_file.name = "recording.wav"  # Give the file a name
    except Exception as e:
        st.error(f"Error processing audio: {str(e)}")
        return f"Error processing audio: {str(e)}"
    
    files = {
        'file': ('recording.wav', audio_file, 'audio/wav')
    }
    
    try:
        # Send POST request to Whisper API
        response = requests.post(
            WHISPER_API_URL, 
            headers=headers, 
            files=files
        )
        
        # Check the response status code
        if response.status_code == 200:
            # Return the transcription text if available
            return response.json().get("text", "No transcription found.")
        else:
            return f"Transcription failed with status code {response.status_code}: {response.text}"
    
    except Exception as e:
        return f"An error occurred: {str(e)}"

# Function to check for wake word
def check_for_wake_word(transcribed_text):
    wake_word = st.session_state.wake_word.lower()
    transcribed_text = transcribed_text.lower()
    
    # Check if wake word is in the transcribed text
    if wake_word in transcribed_text:
        # Remove the wake word from the command
        command = transcribed_text.replace(wake_word, "", 1).strip()
        return True, command
    
    return False, ""

# Function to query GPT-4o
def ask_gpt4o(prompt):
    headers = {
        "Authorization": f"Bearer {GPT4O_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "gpt-4o",
        "messages": [
            {"role": "system", "content": "You are an AI assistant that provides concise and to-the-point answers."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 150
    }
    
    response = requests.post(GPT4O_API_ENDPOINT, headers=headers, json=payload)
    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    return "Sorry, I couldn't process your request."

# Function to convert text to speech using OpenAI TTS


# Function to change wake word
def change_wake_word():
    new_wake_word = st.session_state.new_wake_word
    if new_wake_word:
        st.session_state.wake_word = new_wake_word
        st.success(f"Wake word changed to: '{new_wake_word}'")

# Apply custom CSS
apply_custom_css()

# Streamlit UI with custom styling
st.markdown('<h1>Voice Assistant with <span class="blue-text">Custom Wake Words</span></h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">A minimalist, elegant voice assistant that responds to your own custom wake words.<br>Designed with Apple-inspired aesthetics and attention to detail.</p>', unsafe_allow_html=True)

# Wake word settings directly below the title
with st.form("wake_word_form", clear_on_submit=True):
    st.markdown(f'<p class="centered-text">Current wake word: <b>{st.session_state.wake_word}</b></p>', unsafe_allow_html=True)
    col1, col2 = st.columns([3, 1])
    with col1:
        st.text_input("Set a new wake word:", key="new_wake_word")
    with col2:
        submitted = st.form_submit_button("Update Wake Word")
    if submitted:
        change_wake_word()

# Main UI
# st.markdown('<div class="mic-card">', unsafe_allow_html=True)

# Center status message
st.markdown(f'<p class="status-msg">Say the wake word to activate me...</p>', unsafe_allow_html=True)

# Toggle for active listening mode - centered
col1, col2, col3 = st.columns([1, 1, 1])


st.markdown('<p class="status-msg" style="color: #3b82f6;">Click "Record" when you want to speak.</p>', unsafe_allow_html=True)
# Center the audio input
st.markdown('<div style="display: flex; justify-content: center;">', unsafe_allow_html=True)
audio_bytes = st.audio_input(label="", key="voice_input")
st.markdown('</div>', unsafe_allow_html=True)

if audio_bytes:
    # Processing message
    st.markdown('<p class="status-msg">Processing your speech...</p>', unsafe_allow_html=True)
    
    # Transcribe recorded speech using Whisper API
    transcribed_text = transcribe_audio_whisper(audio_bytes)
    
    # Check for wake word
    wake_word_detected, command = check_for_wake_word(transcribed_text)
    
    # Display transcription in italics
    st.markdown(f'<p style="text-align: center; font-style: italic; margin: 1rem 0;">"{transcribed_text}"</p>', unsafe_allow_html=True)
    
    if wake_word_detected:
        st.markdown('<p class="status-msg" style="color: #22c55e;">Wake word detected! Processing your request...</p>', unsafe_allow_html=True)
        
        if command:
            # Process the command with GPT-4o
            response_text = ask_gpt4o(command)
            
            # Display response with better styling
            st.markdown(f'<p style="text-align: center; font-weight: bold; margin: 1rem 0;">{response_text}</p>', unsafe_allow_html=True)
        else:
            st.markdown('<p class="status-msg" style="color: #3b82f6;">I heard the wake word, but no command was given. Please try again.</p>', unsafe_allow_html=True)
    else:
        st.markdown(f'<p class="status-msg" style="color: #f59e0b;">Wake word not detected. Please start your request with "{st.session_state.wake_word}".</p>', unsafe_allow_html=True)

# Close the card div
st.markdown('</div>', unsafe_allow_html=True)
