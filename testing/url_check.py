import os
import urllib.parse
import requests
import json

"""
testing for successful requests to alphavantage and json file creation of 5 main functions
lookup_functions = ["BALANCE_SHEET", "CASH_FLOW", "INCOME_STATEMENT", "GLOBAL_QUOTE", "OVERVIEW"]
"""

def lookup(sym, func):
    """
    request api function and save as .json file
    """
    try:
        api_key = os.environ.get("API_KEY")
        sym = urllib.parse.quote_plus(sym)
        url = f"https://www.alphavantage.co/query?function={func}&symbol={sym}&apikey={api_key}"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        filepath = f"json_files/{sym}_{func}.json"
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    except requests.RequestException:
        return None


sym = "LRCX"
lookup_functions = ["BALANCE_SHEET", "CASH_FLOW", "INCOME_STATEMENT", "OVERVIEW", "GLOBAL_QUOTE"]
for func in lookup_functions:
    lookup(sym, func)

# IF MORE ALPHAVANTAGE REQUESTS NEED TO BE MADE:
# Wait 1 minute after doing 5 requests
# import time
# time.sleep(60)
# lookup_functions = [""]
# for func in lookup_functions:
#     lookup(sym, func)