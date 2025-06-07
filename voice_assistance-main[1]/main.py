from flask import Flask, request, jsonify, render_template, session
import threading, logging, datetime, os, random, smtplib, subprocess, webbrowser, requests, time
import pyttsx3, wikipedia, pyautogui, speedtest, psutil, cv2
from queue import Queue
import speech_recognition as sr
import pyscreenshot as ImageGrab
import platform
import logging
from playsound import playsound
from chat import chat
from video import record_video
from photo import capture_photo
from music import play_music, next_music, previous_music
from internet_speed import get_internet_speed
from joke import get_joke
from weather import get_weather_info
from my_email import send_email
from change_voice import change_voice
from news import get_news
from todo import add_task, remove_task, list_tasks
from timer import set_timer, set_alarm
from Currency import convert_currency

# Optional install of playsound for cross-platform music playing
try:
    from playsound import playsound
except ImportError:
    import subprocess
    subprocess.check_call(["pip", "install", "playsound"])
    from playsound import playsound

# Configuration
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'default_secret_key')

# Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# TTS Engine Setup
engine = pyttsx3.init()
voices = engine.getProperty('voices')
default_voice_id = voices[1].id if len(voices) > 1 else voices[0].id
speech_queue = Queue()

# Global flag to track music status
is_music_playing = False

# Background Thread: Speech Worker
def speech_worker():
    while True:
        item = speech_queue.get()
        if item is None:
            break
        text, speed, voice_id = item
        try:
            engine.setProperty('rate', speed)
            engine.setProperty('voice', voice_id or default_voice_id)
            engine.say(text)
            engine.runAndWait()
        except Exception as e:
            logging.error(f"Speech error: {e}")
        finally:
            speech_queue.task_done()

speech_thread = threading.Thread(target=speech_worker, daemon=True)
speech_thread.start()

def speak(text, speed=130, voice_id=None):
    if text:
        speech_queue.put((text, speed, voice_id or default_voice_id))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get-information', methods=['POST'])
def get_information():
    data = request.get_json()
    query = data.get('query', '').lower()
    voice_id = session.get('voice_id', data.get('voice', default_voice_id))
    output = ""

    try:
        output = process_command(query, voice_id)
        speak(output, voice_id=voice_id)
        return jsonify({'status': 'success', 'output': output})
    except Exception as e:
        output = "Error processing your request."
        logging.error(f"Command error: {e}")
        speak(output, voice_id=voice_id)
        return jsonify({'status': 'error', 'output': output})

@app.route('/stop', methods=['POST'])
def stop_action():
    global is_music_playing
    if is_music_playing:
        # If music is playing, stop it
        logging.info("Stopping music...")
        is_music_playing = False
        return jsonify({'status': 'success', 'output': 'Music stopped.'})
    else:
        return jsonify({'status': 'error', 'output': 'No music or action to stop.'})

@app.route('/shutdown', methods=['POST'])
def shutdown():
    logging.info("Shutting down IntelleX...")
    speech_queue.put(None)
    speech_thread.join(timeout=5)
    func = request.environ.get('werkzeug.server.shutdown')
    if func:
        func()
    return 'Server shutting down...'


# Add a new route to handle news requests
@app.route('/get-news', methods=['POST'])
def get_news_info():
    data = request.get_json()
    query = data.get('query', '').lower()
    voice_id = session.get('voice_id', data.get('voice', default_voice_id))
    
    try:
        news_output = get_news(query=query)  # Fetch news based on query
        speak(news_output, voice_id=voice_id)  # Read out the news
        return jsonify({'status': 'success', 'output': news_output})
    except Exception as e:
        logging.error(f"Error fetching news: {e}")
        speak("Sorry, I couldn't fetch the news at the moment.", voice_id=voice_id)
        return jsonify({'status': 'error', 'output': "Sorry, I couldn't fetch the news at the moment."})
    

def process_command(query, voice_id):
    global is_music_playing

    if 'hello' in query:
        return "Hello, welcome, I am IntelleX. How can I assist you?"
    elif 'open google' in query:
        return handle_search(query, 'search', 'google')
    elif 'open youtube' in query:
        return handle_search(query, 'search', 'youtube')
    elif 'open camera' in query:
        return open_application('camera')
    elif 'open whatsapp' in query:
        return open_application('whatsapp')
    elif 'open chrome' in query:
        return open_application('chrome')
    elif 'open brave' in query:
        return open_application('brave')
    elif 'open' in query:
        app_name = extract_query(query, 'open')
        return open_application(app_name)
    elif 'what is time right now' in query:
        return datetime.datetime.now().strftime("The time is %I:%M %p")
    elif 'what is date today' in query:
        return datetime.datetime.now().strftime("Today is %A, %B %d, %Y")
    elif 'play music' in query:
        is_music_playing = True
        threading.Thread(target=play_music).start()
        return "Playing music..."
    elif 'next song' in query or 'next music' in query:
        threading.Thread(target=next_music).start()
        return "Playing next song..."
    elif 'previous song' in query or 'previous music' in query:
        threading.Thread(target=previous_music).start()
        return "Playing previous song..."
    elif 'stop music' in query or 'stop' in query:
        response = stop_action()
        return response.get_json().get('output', 'Stopped.')
    elif 'change voice' in query:
        return "Voice changed." if change_voice(query, voice_id) else "Voice not recognized."
    elif 'send an email' in query:
        threading.Thread(target=send_email).start()
        return "Sending email."
    elif 'weather' in query:
        city = extract_query(query, 'weather in')
        return f"The weather in {city} is {get_weather_info(city)}."
    elif 'tell me a joke' in query:
        return get_joke()
    elif 'add task' in query:
        task = extract_query(query, 'add task')
        return add_task(task)
    elif 'remove task' in query:
        task = extract_query(query, 'remove task')
        return remove_task(task)
    elif 'list tasks' in query or 'show tasks' in query:
        return list_tasks()
    elif 'set a timer' in query:
        seconds = extract_duration(query, default=10)
        return set_timer(seconds)
    elif 'set an alarm' in query:
        seconds = extract_duration(query, default=10)
        return set_alarm(seconds)
    elif 'convert currency' in query:
        parts = query.split()
        try:
            amount = float(parts[2])
            from_currency = parts[3]
            to_currency = parts[5]
            return convert_currency(amount, from_currency, to_currency)
        except:
            return "Please use the format: convert currency 100 usd to inr"
    elif 'battery percentage' in query or 'battery status' in query:
        battery = psutil.sensors_battery()
        return f"Battery is at {battery.percent}%" if battery else "Battery status unavailable."
    elif 'wikipedia' in query:
        topic = query.replace('wikipedia', '').strip()
        return wikipedia.summary(topic, sentences=2)
    elif 'internet speed' in query:
        return get_internet_speed()
    elif 'screenshot' in query:
        ImageGrab.grab().save(os.path.join(os.getcwd(), 'screenshot.png'))
        return "Screenshot taken and saved."
    elif 'take a photo' in query or 'capture a photo' in query:
        return capture_photo()
    elif 'record a video' in query:
        duration = extract_duration(query, default=5)  # Extracts duration from query
        return record_video(duration)
    elif 'news' in query or 'headlines' in query:
        query_term = extract_query(query, 'news')  # Extracts any specific topic/query from the user's request
        news = get_news(query=query_term)  # Fetch the news based on the extracted query
        return news
    # elif 'medical' in query:
    #     subprocess.run(["streamlit", "run", r"C:\Users\shail\Desktop\Project\Multiple-Disease-Prediction-System-main\multiplediseaseprediction.py"])
    #     return "Launching the medical prediction system..."
    elif 'medical' in query:
        webbrowser.open("http://localhost:8501")
        return "Launching Medical Pridiction..."
    elif 'volume control' in query:
        subprocess.run(["python",r"C:\Users\shail\Desktop\Project\3 models\final1.py"])
        return "Launching Volume Control..."
    elif 'media control' in query:
        subprocess.run(["python",r"C:\Users\shail\Desktop\Project\3 models\final2.py"])
        return "Launching Media Control..."
    elif 'brightness control' in query:
        subprocess.run(["python",r"C:\Users\shail\Desktop\Project\3 models\final3.py"])
        return "Launching Brightness Control..."
    elif 'data processing' in query:
        webbrowser.open("https://www.kaggle.com/code/shail2604/hand-gesture-recognition")
        return "Launching Data Processing..."
    else:
        ans = chat(query)
        return ans

def open_application(app_name):
    try:
        app_mapping = {
            'camera': 'start microsoft.windows.camera:',  # For Windows Camera
            'whatsapp': 'whatsapp:',  # For WhatsApp (if installed)
            'chrome': 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',  # Full path to Chrome
            'brave': 'C:\\Program Files\\BraveSoftware\\Brave-Browser\\Application\\brave.exe',  # For Brave Browser
        }

        if app_name in app_mapping:
            app_command = app_mapping[app_name]
            if platform.system() == 'Windows':  # Adjusting the command for Windows
                subprocess.Popen([app_command], shell=True)
            else:  # For other OSes like macOS or Linux
                subprocess.Popen([app_command])
            return f"Opening {app_name.capitalize()}..."
        else:
            return f"{app_name.capitalize()} is not supported or not found."
    except Exception as e:
        logging.error(f"Error opening {app_name}: {e}")
        return f"An error occurred while trying to open {app_name}."

def handle_search(query, keyword, site):
    search = extract_query(query, keyword)
    if search:
        if site == 'google':
            webbrowser.open(f"https://www.google.com/search?q={search}")
            return f"Searching Google for {search}"
        elif site == 'youtube':
            webbrowser.open(f"https://www.youtube.com/results?search_query={search}")
            return f"Searching YouTube for {search}"
    else:
        url = "https://www.google.com" if site == 'google' else "https://www.youtube.com"
        webbrowser.open(url)
        return f"Opening {site.capitalize()}..."

def extract_query(query, keyword):
    if f'and {keyword}' in query:
        return query.split(f'and {keyword}')[-1].strip()
    return None

def extract_duration(query, default=5):
    try:
        if 'for' in query:
            return int(query.split('for')[-1].strip().split()[0])
    except:
        pass
    return default


if __name__ == '__main__':
    app.run(debug=True, port=5000)
