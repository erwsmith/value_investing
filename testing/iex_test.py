# THIS WORKS

import requests
from configparser import ConfigParser
import urllib.parse


def iex_get_quote(sym):
    """Look up quote for symbol."""

    # Contact iex API
    try:
        config = ConfigParser()
        config.read('/Users/Eric/repos/value_investing/config/keys_config.cfg')
        API_KEY = config.get('iex', 'publishable_token')
        url = f"https://cloud.iexapis.com/stable/stock/{urllib.parse.quote_plus(sym)}/quote?token={API_KEY}"
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException:
        return None

    # Parse response
    try:
        quote = response.json()
        # print(quote["latestPrice"])
        return {
            "name": quote["companyName"],
            "price": float(quote["latestPrice"]),
            "symbol": quote["symbol"]
        }
    except (KeyError, TypeError, ValueError):
        return None


print(iex_get_quote("LRCX"))