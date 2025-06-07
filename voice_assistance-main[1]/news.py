from dotenv import load_dotenv
import os
import requests
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

def speak(text, speed=130, voice_id=None):
    """Queue the text to be spoken."""
    if text:
        speech_queue.put((text, speed, voice_id or default_voice_id))


# Load environment variables from the .env file
load_dotenv()

# Fetch your News API key from the environment variable
NEWS_API_KEY = os.getenv('NEWS_API_KEY')

# News API URL
NEWS_API_URL = "https://newsapi.org/v2/top-headlines"

# Function to get news headlines
def get_news(query=None, country="us"):
    params = {
        'apiKey': NEWS_API_KEY,
        'country': country,
        'q': query if query else '',  # If query is provided, filter by that, else get all news
        'pageSize': 5  # Limit the number of results
    }
    response = requests.get(NEWS_API_URL, params=params)
    data = response.json()
    
    if data["status"] == "ok" and "articles" in data:
        articles = data["articles"]
        news = ""
        for article in articles:
            news += f"Title: {article['title']}\n"
            news += f"Description: {article['description']}\n"
            news += f"Source: {article['source']['name']}\n"
            news += f"Link: {article['url']}\n\n"
        return news
    else:
        return "Sorry, I couldn't fetch the news at the moment."


