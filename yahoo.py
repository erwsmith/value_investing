from yahoofinancials import YahooFinancials
import pandas as pd
import json

ticker = 'UFI'
yf = YahooFinancials(ticker)

# income statement data
# income_statement = yf.get_financial_stmts('annual', 'income')
# ticker_is = income_statement['incomeStatementHistory'][ticker]

# balance statement data
balance_statement = yf.get_financial_stmts('annual', 'balance')
ticker_bs = balance_statement['balanceSheetHistory'][ticker]
print(ticker_bs[0])

# df_list = []
# for d in ticker_bs:
#     df_list.append(pd.DataFrame.from_dict(d, orient='index'))
# df_bs = pd.concat(df_list)
# df_bs

# cash flow data
# cash_flow = yf.get_financial_stmts('annual', 'cash')
# ticker_cf = cash_flow['cashflowStatementHistory'][ticker]

# de_ratio = totalLiab / totalStockholderEquity