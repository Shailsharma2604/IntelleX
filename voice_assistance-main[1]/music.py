import os
import random
import logging
import pygame
from playsound import playsound
from gtts import gTTS
import pyttsx3
from queue import Queue

engine = pyttsx3.init()
voices = engine.getProperty('voices')
default_voice_id = voices[1].id if len(voices) > 1 else voices[0].id
speech_queue = Queue()

# Global variables to manage music state
music_dir = r"C:\Users\shail\Desktop\Project\voice_assistance-main[1]\music"
supported_formats = ('.mp3', '.wav', '.ogg')
playlist = []
current_index = -1

def speak(text, speed=130, voice_id=None):
    if text:
        speech_queue.put((text, speed, voice_id or default_voice_id))

def load_playlist():
    global playlist
    if not os.path.exists(music_dir):
        speak("Music folder not found.")
        logging.warning(f"Directory does not exist: {music_dir}")
        return []

    playlist = [
        os.path.join(music_dir, f)
        for f in os.listdir(music_dir)
        if f.lower().endswith(supported_formats)
    ]
    return playlist

def play_music(index=None):
    global current_index

    if not playlist:
        load_playlist()
    if not playlist:
        speak("No supported music files found.")
        return

    if index is None:
        index = random.randint(0, len(playlist) - 1)

    if index < 0 or index >= len(playlist):
        speak("No more songs in this direction.")
        return

    try:
        current_index = index
        song = playlist[current_index]
        song_name = os.path.basename(song)

        speak(f"Now playing: {song_name}")
        logging.info(f"Playing song: {song_name}")

        pygame.mixer.init()
        pygame.mixer.music.load(song)
        pygame.mixer.music.play()
    except Exception as e:
        logging.error(f"Error playing music: {e}")
        speak("Sorry, I couldn't play the song.")

def next_music():
    if not playlist:
        load_playlist()
    if current_index + 1 < len(playlist):
        play_music(current_index + 1)
    else:
        speak("You are at the last song.")

def previous_music():
    if not playlist:
        load_playlist()
    if current_index - 1 >= 0:
        play_music(current_index - 1)
    else:
        speak("You are at the first song.")
