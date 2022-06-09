import json

# Parse response
try:
    cash_flow = response.json()
    return {
        "operatingCashflow": cash_flow["operatingCashflow"],
        "capitalExpenditures": cash_flow["capitalExpenditures"],
    }
except (KeyError, TypeError, ValueError):
    return None