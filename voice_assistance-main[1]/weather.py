import os
import requests
import logging
import datetime

def get_weather_info(city):
    try:
        api_key = os.environ.get('WEATHERAPI_KEY')
        if not api_key:
            raise ValueError("WEATHERAPI_KEY not set in environment variables.")

        # WeatherAPI endpoint for current + 3-day forecast
        url = f"http://api.weatherapi.com/v1/forecast.json?key={api_key}&q={city}&days=4&aqi=no&alerts=no"

        res = requests.get(url, timeout=5)
        res.raise_for_status()
        data = res.json()

        # Current weather
        location = data['location']['name']
        current = data['current']
        current_weather = current['condition']['text']
        current_temp = current['temp_c']

        forecast_text = f"Weather for {location}\nCurrent: {current_weather}, {current_temp}°C\nForecast:"

        # 3-day forecast (excluding current day)
        for forecast_day in data['forecast']['forecastday'][1:4]:
            date_obj = datetime.datetime.strptime(forecast_day['date'], "%Y-%m-%d")
            day_name = date_obj.strftime('%A')
            day_temp = forecast_day['day']['avgtemp_c']
            day_desc = forecast_day['day']['condition']['text']
            forecast_text += f"\n{day_name}: {day_desc}, {day_temp}°C"

        logging.info(f"Weather info for {city}: {forecast_text}")
        return forecast_text

    except requests.exceptions.RequestException as req_err:
        logging.error(f"Request error: {req_err}")
    except Exception as e:
        logging.error(f"Unexpected error: {e}", exc_info=True)

    return "Unable to fetch weather forecast right now."
