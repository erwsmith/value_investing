import json
import pandas as pd

def read_financial_reports(sym):
    """
    Read financial report json files and get values to be used for management and growth calculations
    Includes Balance Sheet, Income Statement, and Cash Flow Statement
    """

    # Set number formatting for all dataframes to display as X.XX
    pd.options.display.float_format = '{:,.2f}'.format

    # lookup_functions = ["BALANCE_SHEET", "CASH_FLOW", "INCOME_STATEMENT", "OVERVIEW", "GLOBAL_QUOTE"]

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

    # return df_balance, df_income, df_cash

    print(df_balance)
    print(df_income)
    print(df_cash)

read_financial_reports("LRCX")