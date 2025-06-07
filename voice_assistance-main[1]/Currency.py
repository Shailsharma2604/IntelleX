# currency_converter.py
import requests

def convert_currency(amount, from_currency, to_currency):
    try:
        url = f"https://api.exchangerate.host/convert?from={from_currency.upper()}&to={to_currency.upper()}&amount={amount}"
        response = requests.get(url).json()
        result = response.get("result")
        if result:
            return f"{amount} {from_currency.upper()} is equal to {result:.2f} {to_currency.upper()}."
        return "Conversion failed."
    except:
        return "Error converting currency."
