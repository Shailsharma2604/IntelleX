import smtplib
import logging
import os
from email.message import EmailMessage
from dotenv import load_dotenv
import pyttsx3
from queue import Queue
import threading

# Load environment variables from .env file
load_dotenv()

# Initialize text-to-speech engine
engine = pyttsx3.init()
voices = engine.getProperty('voices')
default_voice_id = voices[1].id if len(voices) > 1 else voices[0].id
speech_queue = Queue()

def speak(text, speed=130, voice_id=None):
    """Queue the text to be spoken."""
    if text:
        speech_queue.put((text, speed, voice_id or default_voice_id))

def send_email(recipient, subject, body):
    """Send email using credentials from environment variables."""
    try:
        # Fetch email credentials from environment
        email_address = os.getenv('EMAIL_USER')
        email_password = os.getenv('EMAIL_PASS')

        # Check if credentials are provided
        if not email_address or not email_password:
            raise ValueError("Email credentials not found in environment variables.")

        # Create email message
        msg = EmailMessage()
        msg['From'] = email_address
        msg['To'] = recipient
        msg['Subject'] = subject
        msg.set_content(body)

        # Send email using SMTP
        with smtplib.SMTP('smtp.example.com', 587) as server:  # Change SMTP server if needed
            server.starttls()
            server.login(email_address, email_password)
            server.send_message(msg)

        # Confirm successful email sending
        speak("Email sent successfully.")
    except smtplib.SMTPException as smtp_err:
        logging.error(f"SMTP error: {smtp_err}")
        speak("SMTP error occurred while sending the email.")
    except ValueError as val_err:
        logging.error(f"ValueError: {val_err}")
        speak("Missing email credentials in environment.")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        speak("Failed to send email due to an unexpected error.")

def send_email_in_thread(recipient, subject, body):
    """Function to send email in a separate thread."""
    email_thread = threading.Thread(target=send_email, args=(recipient, subject, body))
    email_thread.start()

# Example usage of the thread-based email sending function:
# send_email_in_thread('recipient@example.com', 'Subject Example', 'Body of the email.')
