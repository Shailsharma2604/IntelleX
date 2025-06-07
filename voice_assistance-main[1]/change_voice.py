import smtplib
import logging
import os
from email.message import EmailMessage
from dotenv import load_dotenv
import pyttsx3
from queue import Queue
import threading
from flask import session



engine = pyttsx3.init()
voices = engine.getProperty('voices')
default_voice_id = voices[1].id if len(voices) > 1 else voices[0].id
speech_queue = Queue()

def speak(text, speed=130, voice_id=None):
    """Queue the text to be spoken."""
    if text:
        speech_queue.put((text, speed, voice_id or default_voice_id))



def change_voice(query, voices):
    query = query.lower()
    
    if 'female' in query:
        if len(voices) > 1:
            session['voice_id'] = voices[1].id
            speak("Voice changed to female.", voice_id=voices[1].id)
            return True
        else:
            speak("Female voice not available.")
            return False

    elif 'male' in query:
        if len(voices) > 0:
            session['voice_id'] = voices[0].id
            speak("Voice changed to male.", voice_id=voices[0].id)
            return True
        else:
            speak("Male voice not available.")
            return False

    speak("No valid voice change command detected.")
    return False
