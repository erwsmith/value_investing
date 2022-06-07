from yahoofinancials import YahooFinancials
import pandas as pd
import numpy as np

ticker = 'UFI'
yf = YahooFinancials(ticker)

# BALANCE STATEMENT DATA
# get balance statement data from yahoo finance
balance_statement = yf.get_financial_stmts('annual', 'balance')

# get balance sheet history from statement
ticker_bs = balance_statement['balanceSheetHistory'][ticker]

# create and populate list of balance sheet history 
balance_sheet_list = []
for d in ticker_bs:
    balance_sheet_list.append(pd.DataFrame.from_dict(d, orient='index'))
bs_table = pd.concat(balance_sheet_list)

# save balance statement data to csv
bs_table.to_csv("balance_statment.csv")


# INCOME STATEMENT DATA
income_statement = yf.get_financial_stmts('annual', 'income')
ticker_is = income_statement['incomeStatementHistory'][ticker]
income_statement_list = []
for d in ticker_is:
    income_statement_list.append(pd.DataFrame.from_dict(d, orient='index'))
is_table = pd.concat(income_statement_list)
is_table.to_csv("income_statment.csv")


# CASH FLOW DATA
cash_flow = yf.get_financial_stmts('annual', 'cash')
ticker_cf = cash_flow['cashflowStatementHistory'][ticker]
cash_flow_list = []
for d in ticker_cf:
    cash_flow_list.append(pd.DataFrame.from_dict(d, orient='index'))
cf_table = pd.concat(cash_flow_list)
cf_table.to_csv("cash_flow.csv")