import os
import requests
import urllib.parse
import pandas as pd
import json

from flask import redirect, render_template, request, session
from functools import wraps

def usd(value):
    """Format value as USD."""
    return f"${value:,.2f}"


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


# Balance sheet numbers for management: 
# DEBT TO EQUITY RATIO
# TOTAL LIABILITIES / TOTAL SHAREHOLDER EQUITY

# CURRENT RATIO
# CURRENT ASSETS / CURRENT LIABILITIES

# DURABILITY
# LONG TERM DEBT / FREE CASH FLOW
# freeCashFlow = operatingCashflow (cash flow) - capitalExpenditures (cash flow)
# durability = longTermDebt (balance statement) / freeCashFlow

def read_jsons(sym):

    pd.options.display.float_format = '{:,.2f}'.format

    # BALANCE SHEET - read and setup dataframe
    bs_filepath = f"json_files/balance_sheet_{sym}.json"
    with open(bs_filepath, "r+") as f:
        data = f.read()

    # Process data and create clean dataframe
    balance_sheet = json.loads(data)
    annual_reports = balance_sheet["annualReports"]
    df_balance = pd.json_normalize(annual_reports)
    df_balance["fiscalDateEnding"] = pd.to_datetime(df_balance["fiscalDateEnding"])
    df_balance['year'] = pd.DatetimeIndex(df_balance['fiscalDateEnding']).year
    df_balance.set_index("year", inplace=True)

    # Reduce df to have only required columns, cast values as float
    df_balance.replace("None", "0", inplace=True)
    df_balance = df_balance[["totalLiabilities", "totalShareholderEquity", "totalCurrentLiabilities", 
                             "totalCurrentAssets", "longTermDebt", "capitalLeaseObligations", "shortTermDebt",
                             "commonStock", "retainedEarnings"]]
    df_balance = df_balance.astype('float')

    # Calculate de and current ratios:
    df_balance["de_ratio"] = df_balance["totalLiabilities"] / df_balance["totalShareholderEquity"]
    df_balance["current_ratio"] = df_balance["totalCurrentAssets"] / df_balance["longTermDebt"]

    # Calculate Invested Capital
    cols = ["totalShareholderEquity", "shortTermDebt", "longTermDebt", "capitalLeaseObligations"]
    df_balance["investedCapital"] = df_balance[cols].sum(axis=1)


    # CASH FLOW STATEMENT - read and setup dataframe
    cf_filepath = f"json_files/cash_flow_{sym}.json"
    with open(cf_filepath, "r") as f: 
        data = f.read()

    # Process data and create clean dataframe
    cash_flow = json.loads(data)
    annual_reports = cash_flow["annualReports"]
    df_cash = pd.json_normalize(annual_reports)
    df_cash["fiscalDateEnding"] = pd.to_datetime(df_cash["fiscalDateEnding"])
    df_cash['year'] = pd.DatetimeIndex(df_cash['fiscalDateEnding']).year
    df_cash.set_index("year", inplace=True)

    # Reduce df to have only required columns, cast values as float
    df_cash.replace("None", "0", inplace=True)
    df_cash = df_cash[["operatingCashflow", "capitalExpenditures", "cashflowFromInvestment", "cashflowFromFinancing"]]
    df_cash = df_cash.astype('float')

    # Calculate freeCashFlow
    df_cash["freeCashFlow"] = df_cash["operatingCashflow"] - df_cash["capitalExpenditures"]
    df_cash["nonOperatingCash"] = df_cash["cashflowFromInvestment"] + df_cash["cashflowFromFinancing"]


    # INCOME STATEMENT - read and setup dataframe
    income_filepath = f"json_files/income_statement_{sym}.json"
    with open(income_filepath, "r") as f: 
        data = f.read()

    # Process data and create clean dataframe
    income = json.loads(data)
    annual_reports = income["annualReports"]
    df_income = pd.json_normalize(annual_reports)
    df_income["fiscalDateEnding"] = pd.to_datetime(df_income["fiscalDateEnding"])
    df_income['year'] = pd.DatetimeIndex(df_income['fiscalDateEnding']).year
    df_income.set_index("year", inplace=True)

    # Reduce df to have only required columns, cast values as float
    df_income.replace("None", "0", inplace=True)
    df_income = df_income[["totalRevenue", "ebit", "ebitda", "incomeTaxExpense", "netIncome", "incomeBeforeTax"]]
    df_income = df_income.astype('float')

    # Calculate effective tax rate
    # effective_tax_rate = incomeTaxExpense / netIncome
    df_income["effectiveTaxRate"] = df_income["incomeTaxExpense"] / df_income["incomeBeforeTax"]

    # Calculate NOPAT
    # nopat = ebit * (1 - effective_tax_rate)
    df_income["nopat"] = df_income["ebit"] * (1 - df_income["effectiveTaxRate"])
    

    # COMBINE DATAFRAMES
    df = df_balance[["de_ratio", "current_ratio", "longTermDebt", "investedCapital"]]
    df = df.join(df_cash[["freeCashFlow", "nonOperatingCash"]]).join(df_income[["nopat"]])

    # Calculate durability
    df["durability"] = df["longTermDebt"] / df["freeCashFlow"]

    # Calculate return on invested capital %
    df["roic"] = 100 * (df["nopat"] / df["investedCapital"])

    # Set final columns
    df = df[["de_ratio", "current_ratio", "durability", "roic"]]

    # Sort by year
    df = df.sort_index()

    # transpose dataframe
    df = df.transpose()

    # Calculate 5 year average values
    df["5y_average"] = df.mean(axis=1)
    
    # Create pass/fail column and target colum
    df["pass"] = 0
    df["target"] = 0

    # Check average de ratio 
    de_avg = df.loc["de_ratio","5y_average"]
    df.loc[["de_ratio"],["pass"]] = (0 < de_avg) & (de_avg < 5)
    df.loc[["de_ratio"],["target"]] = f"0 < de ratio < 5"

    # Check average current ratio
    current_avg = df.loc["current_ratio","5y_average"]
    df.loc[["current_ratio"],["pass"]] = current_avg > 1
    df.loc[["current_ratio"],["target"]] = f"current ratio > 1"

    # Check average durability
    durability_avg = df.loc["durability","5y_average"]
    df.loc[["durability"],["pass"]] = durability_avg < 3
    df.loc[["durability"],["target"]] = f"durability > 1"

    # Check average roic
    roic_avg = df.loc["roic","5y_average"]
    df.loc[["roic"],["pass"]] = roic_avg > 10
    df.loc[["roic"],["target"]] = f"roic % > 10"

    # Mangement quality check
    management_check = False
    if df.loc["durability","pass"] and df.loc["current_ratio", "pass"] and df.loc["de_ratio", "pass"]:
        management_check = True
    
    return management_check, df

