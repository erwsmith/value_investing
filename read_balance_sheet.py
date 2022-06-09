import json
import pandas as pd
import numpy as np


def read_balance_sheet(sym):
    filepath = f"json_files/balance_sheet_{sym}.json"
    with open(filepath, "r") as f: 
        data = f.read()

    balance_sheet = json.loads(data)
    annual_reports = balance_sheet["annualReports"]
    df = pd.json_normalize(annual_reports)
    print(df)

# for report in annual_reports:
#     print(report["fiscalDateEnding"], report["totalLiabilities"])


# return {
#     "totalLiabilities": balance_sheet["totalLiabilities"],
#     "totalShareholderEquity": balance_sheet["totalShareholderEquity"],
#     "totalCurrentLiabilities": balance_sheet["totalCurrentLiabilities"],
#     "totalCurrentAssets": balance_sheet["totalCurrentAssets"],
#     "longTermDebt": balance_sheet["longTermDebt"]
# }


# # Parse response
#     try:
#         balance_sheet = response.json()
#         return {
#             "totalLiabilities": balance_sheet["totalLiabilities"],
#             "totalShareholderEquity": balance_sheet["totalShareholderEquity"],
#             "totalCurrentLiabilities": balance_sheet["totalCurrentLiabilities"],
#             "totalCurrentAssets": balance_sheet["totalCurrentAssets"],
#             "longTermDebt": balance_sheet["longTermDebt"]
#         }
#     except (KeyError, TypeError, ValueError):
#         return None

read_balance_sheet("UFI")