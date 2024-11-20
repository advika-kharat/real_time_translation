import os
import time
import pygame
from gtts import gTTS
import streamlit as st
import speech_recognition as sr
from googletrans import LANGUAGES, Translator

# Streamlit state to accumulate all spoken text across runs
if "total_text" not in st.session_state:
    st.session_state.total_text = ""  # Initialize total text

# TRANSLATION
isTranslateOn = False

translator = Translator()  # Initialize the translator module.
pygame.mixer.init()  # Initialize the mixer module.

# Create a mapping between language names and language codes
language_mapping = {name: code for code, name in LANGUAGES.items()}


def get_language_code(language_name):
    return language_mapping.get(language_name, language_name)


def translator_function(spoken_text, from_language, to_language):
    return translator.translate(spoken_text, src=from_language, dest=to_language)


def text_to_voice(text_data, to_language):
    myobj = gTTS(text=text_data, lang=to_language, slow=False)
    myobj.save("cache_file.mp3")
    audio = pygame.mixer.Sound("cache_file.mp3")  # Load a sound.
    audio.play()
    os.remove("cache_file.mp3")


def main_process(output_placeholder, spoken_text_placeholder, translated_text_placeholder, from_language, to_language):
    global isTranslateOn

    while isTranslateOn:
        rec = sr.Recognizer()
        with sr.Microphone() as source:
            output_placeholder.text("Listening...")
            print("listening")
            rec.pause_threshold = 1
            audio = rec.listen(source, phrase_time_limit=10)

        try:
            output_placeholder.text("Processing...")
            spoken_text = rec.recognize_google(audio, language=from_language)
            st.session_state.total_text += spoken_text + " "  # Accumulate the spoken text
            # Display spoken text on the screen
            spoken_text_placeholder.text(f"Spoken text: {spoken_text}")

            output_placeholder.text("Translating...")
            translated_text = translator_function(spoken_text, from_language, to_language)

            # Display translated text on the screen
            translated_text_placeholder.text(f"Translated text: {translated_text.text}")

            text_to_voice(translated_text.text, to_language)

        except Exception as e:
            output_placeholder.text(f"Error: {e}")


# UI layout
st.title("Lecture Translation")

# Dropdowns for selecting languages
from_language_name = st.selectbox(
    "Select Source Language:", list(LANGUAGES.values()))
to_language_name = st.selectbox(
    "Select Target Language:", list(LANGUAGES.values()))

# Convert language names to language codes
from_language = get_language_code(from_language_name)
to_language = get_language_code(to_language_name)

# Button to trigger translation
start_button = st.button("Start")
stop_button = st.button("Stop")

# Placeholders for dynamic content
output_placeholder = st.empty()  # For status messages (listening, processing, etc.)
spoken_text_placeholder = st.empty()  # For displaying spoken text
translated_text_placeholder = st.empty()  # For displaying translated text

# Check if "Start" button is clicked
if start_button:
    if not isTranslateOn:
        isTranslateOn = True
        st.session_state.total_text = ""  # Reset the total text when starting
        main_process(output_placeholder, spoken_text_placeholder, translated_text_placeholder, from_language,
                     to_language)

# Check if "Stop" button is clicked
if stop_button:
    isTranslateOn = False
