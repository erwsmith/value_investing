import os
import requests
import urllib.parse
import pandas as pd
import json

from symtable import SymbolTable
from configparser import ConfigParser
from flask import redirect, render_template, request, session
from functools import wraps
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select


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


def iex_get_quote(sym):
    """Look up quote for symbol."""

    # Contact iex API
    try:
        config = ConfigParser()
        config.read('config/keys_config.cfg')
        API_KEY = config.get('iex', 'publishable_token')
        url = f"https://cloud.iexapis.com/stable/stock/{urllib.parse.quote_plus(sym)}/quote?token={API_KEY}"
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException:
        return None

    # Parse response
    try:
        quote = response.json()
        return {
            "name": quote["companyName"],
            "price": float(quote["latestPrice"]),
            "symbol": quote["symbol"]
        }
    except (KeyError, TypeError, ValueError):
        return None


def lookup(sym, func):
    """
    Requests data from alphavantage and json file creation of 5 main functions
    lookup_functions = ["BALANCE_SHEET", "CASH_FLOW", "INCOME_STATEMENT", "OVERVIEW"]
    """
    try:
        # get API_KEY from local .cfg file
        config = ConfigParser()
        config.read('config/keys_config.cfg')
        API_KEY = config.get('alphavantage', 'API_KEY')
        url = f"https://www.alphavantage.co/query?function={func}&symbol={sym}&apikey={API_KEY}"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        # return data

        # create json files for the response data
        filepath = f"json_files/{sym}_{func}.json"
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    except requests.RequestException:
        return None


def read_financial_reports(sym):
    """
    Read financial report json files and get values to be used for management and growth calculations
    Includes Balance Sheet, Income Statement, and Cash Flow Statement
    """

    # Set number formatting for all dataframes to display as X.XX
    pd.options.display.float_format = '{:,.2f}'.format

    # lookup_functions = ["BALANCE_SHEET", "CASH_FLOW", "INCOME_STATEMENT", "OVERVIEW"]

    # BALANCE SHEET - read and setup dataframe
    func = "BALANCE_SHEET"
    filepath = f"json_files/{sym}_{func}.json"
    with open(filepath, "r+") as f:
        data = f.read()

    # Process data and create clean dataframe
    balance_sheet = json.loads(data)
    annual_reports = balance_sheet["annualReports"]
    df_balance = pd.json_normalize(annual_reports)
    df_balance["fiscalDateEnding"] = pd.to_datetime(df_balance["fiscalDateEnding"])
    df_balance['year'] = pd.DatetimeIndex(df_balance['fiscalDateEnding']).year
    df_balance.set_index("year", inplace=True)
    df_balance.replace("None", "0", inplace=True)

    # Reduce df to have only required columns, cast values as float
    df_balance = df_balance[["totalLiabilities", "totalShareholderEquity", "totalCurrentLiabilities", 
                             "totalCurrentAssets", "longTermDebt", "capitalLeaseObligations", "shortTermDebt",
                             "commonStock", "retainedEarnings", "commonStockSharesOutstanding"]]
    df_balance = df_balance.astype('float')

    # Calculate de and current ratios:
    df_balance["de_ratio"] = df_balance["totalLiabilities"] / df_balance["totalShareholderEquity"]
    df_balance["current_ratio"] = df_balance["totalCurrentAssets"] / df_balance["longTermDebt"]

    # Calculate Invested Capital
    cols = ["totalShareholderEquity", "shortTermDebt", "longTermDebt", "capitalLeaseObligations"]
    df_balance["investedCapital"] = df_balance[cols].sum(axis=1)


    # CASH FLOW STATEMENT - read and setup dataframe
    func = "CASH_FLOW"
    filepath = f"json_files/{sym}_{func}.json"
    with open(filepath, "r") as f: 
        data = f.read()

    # Process data and create clean dataframe
    cash_flow = json.loads(data)
    annual_reports = cash_flow["annualReports"]
    df_cash = pd.json_normalize(annual_reports)
    df_cash["fiscalDateEnding"] = pd.to_datetime(df_cash["fiscalDateEnding"])
    df_cash['year'] = pd.DatetimeIndex(df_cash['fiscalDateEnding']).year
    df_cash.set_index("year", inplace=True)
    df_cash.replace("None", "0", inplace=True)

    # Reduce df to have only required columns, cast values as float
    df_cash = df_cash[["operatingCashflow", "capitalExpenditures", "cashflowFromInvestment", "cashflowFromFinancing"]]
    df_cash = df_cash.astype('float')

    # Calculate freeCashFlow
    df_cash["freeCashFlow"] = df_cash["operatingCashflow"] - df_cash["capitalExpenditures"]
    df_cash["nonOperatingCash"] = df_cash["cashflowFromInvestment"] + df_cash["cashflowFromFinancing"]


    # INCOME STATEMENT - read and setup dataframe
    func = "INCOME_STATEMENT"
    filepath = f"json_files/{sym}_{func}.json"
    with open(filepath, "r") as f: 
        data = f.read()

    # Process data and create clean dataframe
    income = json.loads(data)
    annual_reports = income["annualReports"]
    df_income = pd.json_normalize(annual_reports)
    df_income["fiscalDateEnding"] = pd.to_datetime(df_income["fiscalDateEnding"])
    df_income['year'] = pd.DatetimeIndex(df_income['fiscalDateEnding']).year
    df_income.set_index("year", inplace=True)
    df_income.replace("None", "0", inplace=True)

    # Reduce df to have only required columns, cast values as float
    df_income = df_income[["totalRevenue", "ebit", "ebitda", "incomeTaxExpense", "netIncome", "incomeBeforeTax"]]
    df_income = df_income.astype('float')

    # Calculate effective tax rate
    df_income["effectiveTaxRate"] = df_income["incomeTaxExpense"] / df_income["incomeBeforeTax"]

    # Calculate NOPAT
    # nopat = ebit * (1 - effective_tax_rate)
    df_income["nopat"] = df_income["ebit"] * (1 - df_income["effectiveTaxRate"])

    # COMBINE DATAFRAMES
    df_financials = df_balance[["de_ratio", "current_ratio", "longTermDebt", "investedCapital", "commonStockSharesOutstanding", "totalShareholderEquity"]].join(df_cash[["freeCashFlow", "nonOperatingCash", "operatingCashflow"]]).join(df_income[["nopat", "totalRevenue", "netIncome"]])

    return df_financials


def read_overview(sym):

    # Set number formatting for all dataframes to display as X.XX
    pd.options.display.float_format = '{:,.2f}'.format

    # COMPANY OVERVIEW - read and setup dataframe
    func = "OVERVIEW"
    filepath = f"json_files/{sym}_{func}.json"
    with open(filepath, "r+") as f:
        data = f.read()

    # Process data and create clean dataframe
    overview = json.loads(data)
    df_overview = pd.json_normalize(overview)
    df_overview.replace("None", "0", inplace=True)
    
    return df_overview


def management(df_financials):
    """
    Calculate values to check company management quality
    """

    # rename df for convenience
    df = df_financials

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
    df.loc[["current_ratio"],["target"]] = f"1 < current ratio"

    # Check average durability
    durability_avg = df.loc["durability","5y_average"]
    df.loc[["durability"],["pass"]] = (durability_avg < 3) & (durability_avg > 0)
    df.loc[["durability"],["target"]] = f"0 < durability < 3"

    # Check average roic
    roic_avg = df.loc["roic","5y_average"]
    df.loc[["roic"],["pass"]] = roic_avg > 10
    df.loc[["roic"],["target"]] = f"10 < roic %"

    # Mangement quality check
    management_check = df["pass"].all()

    return management_check, df


def growth(df_financials):
    """
    Calculate values to check company growth history
    """

    df = df_financials[["totalRevenue", "netIncome", "commonStockSharesOutstanding", "totalShareholderEquity", "operatingCashflow"]]
    df = df.sort_index()

    # NOTE regarding pandas built-in percent change calculation: 
    # if the 2 values being compared are negative, and the new value is lower than the old, the output of pct_change() will be positive, which is VERY erroneous
    # pct_change example: 
    # df.insert(len(df.columns), "revenue_growth_bad", 100 * df["totalRevenue"].pct_change())

    # Better way of calculating percent change:
    # total revenue (Sales) growth rate
    df.insert(len(df.columns), "revenue_growth", 100 * (df["totalRevenue"] - df["totalRevenue"].shift()) / abs(df["totalRevenue"].shift()))

    # Earnings Per Share Growth Rate.
    # (net income - preferred dividends) / commonStockSharesOutstanding
    # TODO preferred dividends? Haven't found yet, but this seems to only make a minor change when looking as MSFT
    df.insert(len(df.columns), "eps", df["netIncome"] / df["commonStockSharesOutstanding"])
    df.insert(len(df.columns), "eps_growth", 100 * (df["eps"] - df["eps"].shift()) / abs(df["eps"].shift()))
    
    # Equity Growth Rate (BVPS).
    # totalShareholderEquity / commonStockSharesOutstanding
    df.insert(len(df.columns), "bvps", df["totalShareholderEquity"] / df["commonStockSharesOutstanding"])
    df.insert(len(df.columns), "bvps_growth", 100 * (df["bvps"] - df["bvps"].shift()) / abs(df["bvps"].shift()))

    # Operating Cash Flow Growth Rate.
    # operatingCashflow
    df.insert(len(df.columns), "cashflow_growth", 
              100 * (df["operatingCashflow"] - df["operatingCashflow"].shift()) / abs(df["operatingCashflow"].shift()))
    df = df[["eps", "revenue_growth", "eps_growth", "bvps_growth", "cashflow_growth"]]
    df = df.transpose()
    df["avg_growth"] = df.mean(axis=1)
    df["pass"] = df["avg_growth"] > 10

    return df


def read_time_series_monthly(sym):
    # Set number formatting for all dataframes to display as X.XX
    pd.options.display.float_format = '{:,.2f}'.format

    # Historical Price data: TIME_SERIES_MONTHLY_ADJUSTED - read and setup dataframe
    func = "TIME_SERIES_MONTHLY_ADJUSTED"
    filepath = f"json_files/{sym}_{func}.json"
    with open(filepath, "r+") as f:
        data = f.read()

    # Process data and create list of annual historical prices in JUNE, same month as financial report data
    price_history = json.loads(data)
    price_history_list = []
    dates = ["2022-06-16", "2021-06-30", "2020-06-30", "2019-06-28", "2018-06-29", "2017-06-30"]
    for date in dates:
        price_history_list.append(price_history["Monthly Adjusted Time Series"][date]["5. adjusted close"])
    
    # create and format dataframe of historical pricing
    d = {'date': dates, 'price': price_history_list}
    df_price = pd.DataFrame(d)
    df_price["date"] = pd.to_datetime(df_price["date"])
    df_price['year'] = pd.DatetimeIndex(df_price['date']).year
    df_price.set_index("year", inplace=True)
    df_price.drop(['date'], axis=1, inplace=True)
    df_price = df_price.sort_index()

    return df_price


def yahoo_growth(sym):
    """Use selenium to obtain analyst growth rate from yahoo finance"""
    
    # driver setup
    options = Options()
    options.headless = True
    options.add_argument("--window-size=192,120")
    driver = webdriver.Chrome(options=options)
    
    # get table element using full xpath
    url = f"https://finance.yahoo.com/quote/{sym}/analysis?p={sym}"
    driver.get(url)
    full_xpath = "/html/body/div[1]/div/div/div[1]/div/div[3]/div[1]/div/div[1]/div/div/section/table[6]/tbody/tr[5]/td[2]"
    element = driver.find_element(by=By.XPATH, value=full_xpath)
    analystGrowthRate = float(element.text.replace("%", ""))
    driver.close()
    
    # analystGrowthRate = .1

    return analystGrowthRate


def sticker_price(df_financials, df_overview):
    """
    Calculate company "Sticker Price" or the estimated actual value, and the "Margin of Safety Price" to compare to current price
    """

    # Set number formatting for all dataframes to display as X.XX    
    pd.options.display.float_format = '{:,.2f}'.format

    # get bvps growth rate from growth()
    df_growth = growth(df_financials)
    bvpsGrowthRate = df_growth.loc["bvps_growth", "avg_growth"]

    # get from alphavantage OVERVIEW
    currentEPS = float(df_overview.loc[0, "EPS"])

    # calculate average PE ratio (EPS/price)
    df_pe = pd.DataFrame(df_growth.drop(["avg_growth", "pass"], axis=1).transpose()["eps"])
    sym = df_overview.loc[0, "Symbol"]
    price = read_time_series_monthly(sym)
    df_pe = price.join(df_pe)
    df_pe.loc[[2022],["eps"]] = currentEPS
    df_pe = df_pe.astype('float')
    df_pe["pe"] = df_pe["price"] / df_pe["eps"]
    avgPE = df_pe["pe"].mean()

    # get analyst growth rate from yahoo finance
    try:
        analystGrowthRate = yahoo_growth(sym)
        
        # set projected growth rate, cap at 15%
        growthRate = min(analystGrowthRate, bvpsGrowthRate)
        if growthRate > .15:
            growthRate = .15

    except:
        growthRate = bvpsGrowthRate
    
    # calculate estimated EPS 10 years from now  
    futureEPS = currentEPS * ((1 + growthRate)**10)
    
    # calculate estimated price in 10 years
    defaultPE = growthRate * 200
    futureMarketPrice = futureEPS * min(avgPE, defaultPE)

    # apply Minimum Acceptable Rate of Return of 15%
    stickerPrice = futureMarketPrice / 4
    safePrice = stickerPrice / 2

    return float(f"{stickerPrice:.2f}"), float(f"{safePrice:.2f}")



# FUNCTION TESTING

# sym = "MSFT"

# df = read_financial_reports(sym)

# print(df)

# print(management(df))

# _, d = growth(df)
# print(d)

# o = read_overview(sym)
# print(o)

# print(sticker_price(df, o))

# print(read_quote(sym))

# print(iex_get_quote(sym))

# sym = "UFI"
# lookup_functions = ["BALANCE_SHEET", "CASH_FLOW", "INCOME_STATEMENT", "OVERVIEW"]
# for func in lookup_functions:
#     lookup(sym, func)

# lookup("UFI", "TIME_SERIES_MONTHLY_ADJUSTED")

# print(read_time_series_monthly("LRCX"))