import pandas as pd
import numpy as np


bs_table = pd.read_csv("/Users/Eric/repos/value_investing/balance_statment.csv", index_col=0)
cf_table = pd.read_csv("/Users/Eric/repos/value_investing/cash_flow.csv", index_col=0)
is_table = pd.read_csv("/Users/Eric/repos/value_investing/income_statement.csv", index_col=0)


# DEBT TO EQUITY RATIO
# TOTAL LIABILITIES / TOTAL STOCKHOLDER EQUITY
# these values are found on the balance sheet
de_table = pd.DataFrame()
de_table['de_ratio'] = bs_table['totalLiab'] / bs_table['totalStockholderEquity']
de_table.index.name = 'date'
de_table.sort_index(ascending=True, inplace=True)
de_table = de_table.transpose()

# pass/fail bool for average de ratio, a good de ratio is between 0 and 5
de_table['pass (0<de<5)'] = (de_table.loc['de_ratio'].mean() > 0) & (de_table.loc['de_ratio'].mean() < 5)
print(de_table)


# CURRENT RATIO
# CURRENT ASSETS / CURRENT LIABILITIES
current_table = pd.DataFrame()
current_table['current_ratio'] = bs_table['totalCurrentAssets'] / bs_table['totalCurrentLiabilities']
current_table.index.name = 'date'
current_table.sort_index(ascending=True, inplace=True)
current_table = current_table.transpose()

# pass/fail bool for average current ratio; a good current ratio is > 1
current_table['pass (>1)'] = current_table.loc['current_ratio'].mean() > 1
print(current_table)


# DURABILITY
# LONG TERM DEBT / FREE CASH FLOW
# free_cash_flow = totalCashFromOperatingActivities (cash flow) - capitalExpenditures (cash flow)
# durability = longTermDebt (balance statement) / free_cash_flow
durability_table = pd.DataFrame()
durability_table['durability'] = bs_table['longTermDebt'] / (cf_table['totalCashFromOperatingActivities'] - cf_table['capitalExpenditures'])
durability_table.index.name = 'date'
durability_table.sort_index(ascending=True, inplace=True)
durability_table = durability_table.transpose()

# pass/fail bool for average durability; good durability is < 3
durability_table['pass (<3)'] = durability_table.loc['durability'].mean() < 3
print(durability_table)