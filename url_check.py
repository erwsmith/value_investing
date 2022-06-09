import os
import urllib.parse
import requests
import json

def url_check():
    api_key = os.environ.get("API_KEY")
    sym = urllib.parse.quote_plus('IBM')
    func = "BALANCE_SHEET"
    url = f"https://www.alphavantage.co/query?function={func}&symbol={sym}&apikey={api_key}"
    response = requests.get(url)
    balance_sheet = response.json()

    with open("balance_sheet.json", "w", encoding="utf-8") as f:
        json.dump(balance_sheet, f, ensure_ascii=False, indent=4)

    annual_reports = balance_sheet["annualReports"]

    # for report in annual_reports:
    #     print(report["fiscalDateEnding"], report["totalLiabilities"])
        

    # return {
    #     "totalLiabilities": balance_sheet["totalLiabilities"],
    #     "totalShareholderEquity": balance_sheet["totalShareholderEquity"],
    #     "totalCurrentLiabilities": balance_sheet["totalCurrentLiabilities"],
    #     "totalCurrentAssets": balance_sheet["totalCurrentAssets"],
    #     "longTermDebt": balance_sheet["longTermDebt"]
    # }


url_check()