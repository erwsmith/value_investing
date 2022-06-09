import json

with open("balance_sheet.json", "r") as f: 
    data = f.read()

balance_sheet = json.loads(data)
annual_reports = balance_sheet["annualReports"]

for report in annual_reports:
    print(report["fiscalDateEnding"], report["totalLiabilities"])
    

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