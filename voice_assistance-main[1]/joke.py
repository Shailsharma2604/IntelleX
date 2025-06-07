import requests
import logging

def get_joke():
    headers = {'Accept': 'application/json'}

    # Primary Joke API
    try:
        res = requests.get('https://api.jokes.one/jod', headers=headers, timeout=5)
        res.raise_for_status()
        data = res.json()
        joke = data.get('contents', {}).get('jokes', [{}])[0].get('joke', {}).get('text')
        if joke:
            logging.info("Joke fetched from primary API.")
            return joke
    except Exception as e:
        logging.warning(f"Primary joke API failed: {e}")

    # Fallback Joke API
    try:
        res = requests.get('https://official-joke-api.appspot.com/random_joke', timeout=5)
        res.raise_for_status()
        data = res.json()
        joke = f"{data.get('setup', '')} {data.get('punchline', '')}"
        if joke.strip():
            logging.info("Joke fetched from fallback API.")
            return joke
    except Exception as e:
        logging.error(f"Fallback joke API failed: {e}", exc_info=True)

    return "Sorry, I couldn't fetch a joke at the moment."
