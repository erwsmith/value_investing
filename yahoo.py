from yahoofinancials import YahooFinancials
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

ticker = 'UFI'
yf = YahooFinancials(ticker)

# income statement data
# income_statement = yf.get_financial_stmts('annual', 'income')
# ticker_is = income_statement['incomeStatementHistory'][ticker]


# cash flow data
# cash_flow = yf.get_financial_stmts('annual', 'cash')
# ticker_cf = cash_flow['cashflowStatementHistory'][ticker]


# get balance statement data from yahoo finance
balance_statement = yf.get_financial_stmts('annual', 'balance')

# get balance sheet history from statement
ticker_bs = balance_statement['balanceSheetHistory'][ticker]

# create list for balance sheet history 
df_list = []
for d in ticker_bs:
    df_list.append(pd.DataFrame.from_dict(d, orient='index'))
df_bs = pd.concat(df_list)
# print(df_bs)

# save balance statement data to csv
# df_bs.to_csv("balance_statment.csv")

# calculate de ratio and create new column for it
df_bs['de_ratio'] = df_bs['totalLiab'] / df_bs['totalStockholderEquity']

# transpose de ratio column
col = df_bs['de_ratio'].agg('mean').transpose()

# create pass/fail bool for acceptable de ratio
result = (col < 5) & (col > 0)
# print(result)