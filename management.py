import pandas as pd
import numpy as np

# DEBT TO EQUITY RATIO
# TOTAL LIABILITIES / TOTAL STOCKHOLDER EQUITY
# these values are found on the balance sheet
bs_table['de_ratio'] = bs_table['totalLiab'] / bs_table['totalStockholderEquity']

# transpose de ratio column
de_col = bs_table['de_ratio'].agg('mean').transpose()

# create pass/fail bool for acceptable de ratio
# a good de ratio is between 0 and 5
de_result = (de_col < 5) & (de_col > 0)
# print(de_result)


# CURRENT RATIO
# CURRENT ASSETS / CURRENT LIABILITIES
bs_table['current_ratio'] = bs_table['totalCurrentAssets'] / bs_table['totalCurrentLiabilities']
# print(bs_table[['totalCurrentAssets', 'totalCurrentLiabilities', 'current_ratio']])
current_col = bs_table['current_ratio'].agg('mean').transpose()
current_result = current_col > 1
# print(current_col)
# print(current_result)


# DURABILITY
# free_cash_flow = totalCashFromOperatingActivities (cash flow) - capitalExpenditures (cash flow)
# durability = longTermDebt (balance statement) / free_cash_flow




