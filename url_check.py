import os
import urllib.parse
import requests
import json

"""
testing for successful lookup and json file creation for balance sheet, cash flow, and income statements.
"""

def lookup_balance_sheet(symbol):
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


def lookup_earnings(symbol):
    """
    lookup EPS history and save as .json file
    """
    try:
        api_key = os.environ.get("API_KEY")
        sym = urllib.parse.quote_plus(symbol)
        func = "EARNINGS"
        url = f"https://www.alphavantage.co/query?function={func}&symbol={sym}&apikey={api_key}"
        response = requests.get(url)
        response.raise_for_status()
        earnings = response.json()
        filepath = f"json_files/earnings_{sym}.json"
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(earnings, f, ensure_ascii=False, indent=4)

    except requests.RequestException:
        return None


def lookup_quote(symbol):
    """
    lookup price history and save as .json file
    """
    try:
        api_key = os.environ.get("API_KEY")
        sym = urllib.parse.quote_plus(symbol)
        func = "GLOBAL_QUOTE"
        url = f"https://www.alphavantage.co/query?function={func}&symbol={sym}&apikey={api_key}"
        response = requests.get(url)
        response.raise_for_status()
        quote = response.json()
        filepath = f"json_files/quote_{sym}.json"
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(quote, f, ensure_ascii=False, indent=4)

    except requests.RequestException:
        return None

def lookup(symbol, func):
    """
    request api function and save as .json file
    """
    try:
        api_key = os.environ.get("API_KEY")
        sym = urllib.parse.quote_plus(symbol)
        url = f"https://www.alphavantage.co/query?function={func}&symbol={sym}&apikey={api_key}"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        filepath = f"json_files/{func}_{sym}.json"
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    except requests.RequestException:
        return None


sym = "LRCX"
# lookup_balance_sheet(sym)
# lookup_cash_flow(sym)
# lookup_income_statement(sym)
# lookup_earnings(sym)
# lookup_quote(sym)
lookup(sym, "OVERVIEW")