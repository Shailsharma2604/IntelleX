from google import genai
from dotenv import load_dotenv
import os

# Load the .env file
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY is not set in the environment variables.")

client = genai.Client(api_key=GEMINI_API_KEY)

def chat(message):
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=message,
    )
    
    # Return the response text
    return response.text
