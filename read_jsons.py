
import json
import pandas as pd

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

    # BALANCE SHEET - read and setup dataframe
    bs_filepath = f"json_files/balance_sheet_{sym}.json"
    with open(bs_filepath, "r+") as f:
        data = f.read()

    # Process data and create clean dataframe
    balance_sheet = json.loads(data)
    annual_reports = balance_sheet["annualReports"]
    print(annual_reports)
    df_balance = pd.json_normalize(annual_reports)
    df_balance["fiscalDateEnding"] = pd.to_datetime(df_balance["fiscalDateEnding"])
    df_balance['year'] = pd.DatetimeIndex(df_balance['fiscalDateEnding']).year
    df_balance.set_index("year", inplace=True)
    # print(df_balance)

    # Reduce df to have only required columns, cast values as float
    df_balance.replace("None", "0", inplace=True)
    df_balance = df_balance[["totalLiabilities", "totalShareholderEquity", "totalCurrentLiabilities", "totalCurrentAssets", "longTermDebt", "capitalLeaseObligations"]]
    df_balance = df_balance.astype('float')

    # Calculate de and current ratios:
    df_balance["de_ratio"] = df_balance["totalLiabilities"] / df_balance["totalShareholderEquity"]
    df_balance["current_ratio"] = df_balance["totalCurrentAssets"] / df_balance["longTermDebt"]
    df_balance["invested_capital"] = df_balance["totalShareholderEquity"] + df_balance["longTermDebt"] + df_balance["capitalLeaseObligations"]

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
    df_cash = df_cash[["operatingCashflow", "capitalExpenditures"]]
    df_cash = df_cash.astype('float')

    # Calculate freeCashFlow
    df_cash["freeCashFlow"] = df_cash["operatingCashflow"] - df_cash["capitalExpenditures"]
    # print(df_cash)
    

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
    df_income = df_income[["ebit", "incomeTaxExpense", "netIncome"]]
    df_income = df_income.astype('float')

    # Calculate effective tax rate
    # effective_tax_rate = incomeTaxExpense / netIncome
    df_income["effectiveTaxRate"] = df_income["incomeTaxExpense"] / df_income["netIncome"]

    # Calculate NOPAT
    # nopat = ebit * (1 - effective_tax_rate)
    df_income["nopat"] = df_income["ebit"] * (1 - df_income["effectiveTaxRate"])
    # print(df_income)
    
    # COMBINE DATAFRAMES
    df = df_balance[["de_ratio", "current_ratio", "longTermDebt", "invested_capital"]]
    df = df.join(df_cash[["freeCashFlow"]]).join(df_income[["nopat"]])

    # Calculate durability
    df["durability"] = df["longTermDebt"] / df["freeCashFlow"]

    # Calculate ROIC
    df["roic"] = df["nopat"] / df["invested_capital"]

    # Set final columns
    df = df[["de_ratio", "current_ratio", "durability", "roic"]]


    # Sort by year, transpose, and calculate 5 year average values
    df = df.sort_index().transpose()
    df["5y_average"] = df.mean(axis=1)
    
    # Create pass/fail column and note colum
    df["pass"] = 0
    df["note"] = 0

    # Check average de ratio 
    de_avg = df.loc["de_ratio","5y_average"]
    df.loc[["de_ratio"],["pass"]] = (0 < de_avg) & (de_avg < 5)
    df.loc[["de_ratio"],["note"]] = f"0 < de ratio < 5"

    # Check average current ratio
    current_avg = df.loc["current_ratio","5y_average"]
    df.loc[["current_ratio"],["pass"]] = current_avg > 1
    df.loc[["current_ratio"],["note"]] = f"current ratio > 1"

    # Check average durability
    durability_avg = df.loc["durability","5y_average"]
    df.loc[["durability"],["pass"]] = durability_avg < 3
    df.loc[["durability"],["note"]] = f"durability > 1"

    # Mangement quality check
    management_check = False
    if df.loc["durability","pass"] and df.loc["current_ratio", "pass"] and df.loc["de_ratio", "pass"]:
        management_check = True

    # print(df)

read_jsons("UFI")