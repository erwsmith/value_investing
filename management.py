import pandas as pd
import json


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
    df_cash.replace("None", "0", inplace=True)

    # Reduce df to have only required columns, cast values as float
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
    df_income.replace("None", "0", inplace=True)

    # Reduce df to have only required columns, cast values as float
    df_income = df_income[["totalRevenue", "ebit", "ebitda", "incomeTaxExpense", "netIncome", "incomeBeforeTax"]]
    df_income = df_income.astype('float')

    # Calculate effective tax rate
    df_income["effectiveTaxRate"] = df_income["incomeTaxExpense"] / df_income["incomeBeforeTax"]

    # Calculate NOPAT
    # nopat = ebit * (1 - effective_tax_rate)
    df_income["nopat"] = df_income["ebit"] * (1 - df_income["effectiveTaxRate"])

    return df_balance, df_income, df_cash


def management(df_balance, df_income, df_cash):

    # COMBINE DATAFRAMES
    df = df_balance[["de_ratio", "current_ratio", "longTermDebt", 
                     "investedCapital", "commonStockSharesOutstanding"]].join(df_cash[["freeCashFlow", 
                     "nonOperatingCash"]]).join(df_income[["nopat"]])

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
    management_check = df["pass"].all()

    return management_check, df


def growth(df_balance, df_income, df_cash):

    # total revenue (Sales) growth rate
    df = df_income[["totalRevenue", "netIncome"]].join(df_balance[["commonStockSharesOutstanding", "totalShareholderEquity"]]).join(df_cash[["operatingCashflow"]])
    df.sort_index(inplace=True)

    # NOTE regarding pandas built-in percent change calculation: 
    # if the 2 values being compared are negative, and the new value is lower than the old, the output of pct_change() will be positive, which is VERY erroneous
    # pct_change example: 
    # df.insert(len(df.columns), "revenue_growth_bad", 100 * df["totalRevenue"].pct_change())

    # Better way of calculating percent change:
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
    df.insert(len(df.columns), "cashflow_growth", 100 * (df["operatingCashflow"] - df["operatingCashflow"].shift()) / abs(df["operatingCashflow"].shift()))

    # df_income = df_income[["totalRevenue", "ebit", "ebitda", "incomeTaxExpense", "netIncome", "incomeBeforeTax"]]
    df = df[["revenue_growth", "eps_growth", "bvps_growth", "cashflow_growth"]]
    df = df.transpose()
    df.drop([2017], axis=1, inplace=True)
    df["avg_growth"] = df.mean(axis=1)
    df["pass"] = df["avg_growth"] > 10

    # Company growth check
    growth_check = df["pass"].all()

    return growth_check, df



# b, i, c = read_jsons("MSFT")

# growth(b, i, c)
# management(b, i, c)