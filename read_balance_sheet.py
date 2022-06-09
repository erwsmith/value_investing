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
    df.set_index("fiscalDateEnding", inplace=True)
    df = df[["totalLiabilities", "totalShareholderEquity", "totalCurrentLiabilities", "totalCurrentAssets", "longTermDebt"]]
    # df = df[["totalLiabilities", "totalShareholderEquity", "totalCurrentLiabilities", "totalCurrentAssets"]]
    df = df.astype('float')
    df["de_ratio"] = df["totalLiabilities"] / df["totalShareholderEquity"]
    print(df)

read_balance_sheet("UFI")