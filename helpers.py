import os
import requests
import urllib.parse
import pandas as pd
import json

from flask import redirect, render_template, request, session
from functools import wraps


def apology(message, code=400):
    """Render message as an apology to user."""
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code


def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


def lookup_balance_sheet(symbol):
    """
    Look up balance sheets for last 5 years for symbol and save as .json file
    """
    try:
        api_key = os.environ.get("API_KEY")
        sym = urllib.parse.quote_plus(symbol)
        func = "BALANCE_SHEET"
        url = f"https://www.alphavantage.co/query?function={func}&symbol={sym}&apikey={api_key}"
        response = requests.get(url)
        response.raise_for_status()
        balance_sheet = response.json()
        filepath = f"json_files/balance_sheet_{sym}.json"
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(balance_sheet, f, ensure_ascii=False, indent=4)

    except requests.RequestException:
        return None
    

def lookup_cash_flow(symbol):
    """
    lookup cash flow data for last 5 years and save as .json file
    """
    try:
        api_key = os.environ.get("API_KEY")
        sym = urllib.parse.quote_plus(symbol)
        func = "CASH_FLOW"
        url = f"https://www.alphavantage.co/query?function={func}&symbol={sym}&apikey={api_key}"
        response = requests.get(url)
        response.raise_for_status()
        cash_flow = response.json()
        filepath = f"json_files/cash_flow_{sym}.json"
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(cash_flow, f, ensure_ascii=False, indent=4)

    except requests.RequestException:
        return None

def lookup_income_statement(symbol):
    """
    lookup income statement data for last 5 years and save as .json file
    """
    try:
        api_key = os.environ.get("API_KEY")
        sym = urllib.parse.quote_plus(symbol)
        func = "INCOME_STATEMENT"
        url = f"https://www.alphavantage.co/query?function={func}&symbol={sym}&apikey={api_key}"
        response = requests.get(url)
        response.raise_for_status()
        income_statement = response.json()
        filepath = f"json_files/income_statement_{sym}.json"
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(income_statement, f, ensure_ascii=False, indent=4)

    except requests.RequestException:
        return None

def usd(value):
    """Format value as USD."""
    return f"${value:,.2f}"