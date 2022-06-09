import os
import requests
import urllib.parse
import pandas as pd

from flask import redirect, render_template, request, session
from functools import wraps
from yahoofinancials import YahooFinancials


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
    Look up balance sheet data for symbol.
    """
    # Contact alphavantage API
    try:
        api_key = os.environ.get("API_KEY")
        sym = urllib.parse.quote_plus(symbol)
        func = "BALANCE_SHEET"
        url = f"https://www.alphavantage.co/query?function={func}&symbol={sym}&apikey={api_key}"
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException:
        return None

    # Parse response
    try:
        balance_sheet = response.json()
        return {
            "totalLiabilities": balance_sheet["totalLiabilities"],
            "totalShareholderEquity": balance_sheet["totalShareholderEquity"],
            "totalCurrentLiabilities": balance_sheet["totalCurrentLiabilities"],
            "totalCurrentAssets": balance_sheet["totalCurrentAssets"],
            "longTermDebt": balance_sheet["longTermDebt"]
        }
    except (KeyError, TypeError, ValueError):
        return None

def lookup_cash_flow(symbol):
    """
    lookup cash flow data for symbol
    """
    # Contact alphavantage API
    try:
        api_key = os.environ.get("API_KEY")
        sym = urllib.parse.quote_plus(symbol)
        func = "CASH_FLOW"
        url = f"https://www.alphavantage.co/query?function={func}&symbol={sym}&apikey={api_key}"
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException:
        return None

    # Parse response
    try:
        cash_flow = response.json()
        return {
            "operatingCashflow": cash_flow["operatingCashflow"],
            "capitalExpenditures": cash_flow["capitalExpenditures"],
        }
    except (KeyError, TypeError, ValueError):
        return None


def usd(value):
    """Format value as USD."""
    return f"${value:,.2f}"


def yahoo(ticker):
    """Get data for symbol."""

    yf = YahooFinancials(ticker)

    # BALANCE STATEMENT DATA
    # get balance statement data from yahoo finance
    balance_statement = yf.get_financial_stmts('annual', 'balance')

    # get balance sheet history from statement
    ticker_bs = balance_statement['balanceSheetHistory'][ticker]

    # create and populate list of balance sheet history 
    balance_sheet_list = []
    for d in ticker_bs:
        balance_sheet_list.append(pd.DataFrame.from_dict(d, orient='index'))
    bs_table = pd.concat(balance_sheet_list)

    # save balance statement data to csv
    bs_table.to_csv("balance_statment.csv")


    # INCOME STATEMENT DATA
    income_statement = yf.get_financial_stmts('annual', 'income')
    ticker_is = income_statement['incomeStatementHistory'][ticker]
    income_statement_list = []
    for d in ticker_is:
        income_statement_list.append(pd.DataFrame.from_dict(d, orient='index'))
    is_table = pd.concat(income_statement_list)
    is_table.to_csv("income_statment.csv")


    # CASH FLOW DATA
    cash_flow = yf.get_financial_stmts('annual', 'cash')
    ticker_cf = cash_flow['cashflowStatementHistory'][ticker]
    cash_flow_list = []
    for d in ticker_cf:
        cash_flow_list.append(pd.DataFrame.from_dict(d, orient='index'))
    cf_table = pd.concat(cash_flow_list)
    cf_table.to_csv("cash_flow.csv")


def management():
    return None