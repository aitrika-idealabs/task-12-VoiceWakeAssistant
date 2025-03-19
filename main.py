import streamlit as st
import speech_recognition as sr
import pyttsx3
import requests
import re
import time

# Load API credentials from Streamlit secrets
GPT4O_API_ENDPOINT = st.secrets["GPT4O_API_ENDPOINT"]
GPT4O_API_KEY = st.secrets["GPT4O_API_KEY"]

# Initialize TTS engine
engine = pyttsx3.init()
engine.setProperty('rate', 150)  # Adjust speech speed

# Function to apply professional CSS styling
def apply_custom_css():
    st.markdown(
        """
        <style>
        body {
            background-color: #1c1c1c;
            color: #e0e0e0;
            font-family: 'Arial', sans-serif;
        }
        .stApp {
            background-color: #000000;
        }
        .css-18e3th9 {
            background-color: #222831;
            color: #e0e0e0;
        }
        .stButton > button {
            border-radius: 6px;
            background-color: #4a5568;
            color: white;
            padding: 8px 16px;
            font-size: 14px;
            border: none;
            transition: 0.3s;
        }
        .stButton > button:hover {
            background-color: #374151;
        }
        .stTextInput > div > div > input {
            border-radius: 6px;
            padding: 8px;
            font-size: 14px;
            background-color: #2d3748;
            color: white;
            border: 1px solid #4a5568;
        }
        .wake-word {
            color: #f0a500;
            font-weight: bold;
            font-size: 18px;
            margin-bottom: 10px;
        }
        .speech-text {
            font-size: 16px;
            font-weight: normal;
            color: #d1d5db;
            padding: 10px;
            border-left: 3px solid #4a5568;
            background-color: #2a2d36;
            border-radius: 4px;
            margin-bottom: 10px;
        }
        .ai-response {
            font-size: 16px;
            font-weight: normal;
            color: #ffffff;
            padding: 10px;
            border-left: 3px solid #f0a500;
            background-color: #333743;
            border-radius: 4px;
            margin-bottom: 10px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

# Function to convert text to speech
def text_to_speech(text):
    cleaned_text = re.sub(r'#(\S+)', " ", text)  # Remove special characters

    # Use st.empty() to reserve UI space
    # response_placeholder = st.empty()
    # response_placeholder.markdown(f'<div class="speech-text">Speaking: {cleaned_text}</div>', unsafe_allow_html=True)

    # Give Streamlit time to render
    time.sleep(3)

    # Run TTS
    engine.say(cleaned_text)
    engine.runAndWait()  

    # Clear the placeholder after speaking
    # response_placeholder.empty()

# Function to record speech and convert to text
def recognize_speech():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.write("Listening...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    try:
        text = recognizer.recognize_google(audio).lower()
        return text
    except sr.UnknownValueError:
        return None
    except sr.RequestError:
        return None

# Function to query GPT-4o
def ask_gpt4o(prompt):
    headers = {
        "Authorization": f"Bearer {GPT4O_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "messages": [
            {"role": "system", "content": "You are an AI assistant that provides concise and to-the-point answers."},
            {"role": "user", "content": prompt}],
        "max_tokens": 150
    }
    
    response = requests.post(GPT4O_API_ENDPOINT, headers=headers, json=payload)
    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    return "Sorry, I couldn't process your request."

# Apply custom CSS
apply_custom_css()

# Streamlit UI
st.title("VoiceWake Assistant")
st.write("Speak and interact with GPT-4o.")

# Default wake word
if "wake_word" not in st.session_state:
    st.session_state.wake_word = "hey assistant"

# Change wake word feature
if st.button("Change Custom Wake Word"):
    new_wake_word = st.text_input("Enter your new wake word:", value=st.session_state.wake_word)
    if new_wake_word:
        st.session_state.wake_word = new_wake_word.lower()
        st.success(f"Wake word changed to: {st.session_state.wake_word}")

st.markdown(f'<div class="wake-word">Current Wake Word: {st.session_state.wake_word}</div>', unsafe_allow_html=True)

# Listen for wake word
st.write("Say something...")
spoken_text = recognize_speech()

if spoken_text:
    st.markdown(f'<div class="speech-text">You said: {spoken_text}</div>', unsafe_allow_html=True)

    # Check for wake word
    while True:
        if st.session_state.wake_word in spoken_text:
            st.success("Wake word detected! Ask your question now...")
            
            # Listen for user query
            query_text = recognize_speech()

            if query_text:
                st.markdown(f'<div class="speech-text">You asked: {query_text}</div>', unsafe_allow_html=True)

                # Get GPT-4o response
                response_text = ask_gpt4o(query_text)
                st.markdown(f'<div class="ai-response">AI Response: {response_text}</div>', unsafe_allow_html=True)

                # Convert response to speech
                text_to_speech(response_text)  # Runs in the main thread
                time.sleep(7)  # Wait for TTS to finish speaking
            else:
                st.error("No query detected. Try again.")
    else:
        st.error("No wake word detected. Try again.")
else:
    st.error("Could not recognize speech. Try again.")
