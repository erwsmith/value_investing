import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

filepath = "/Users/Eric/repos/value_investing/balance_statment.csv"

data = pd.read_csv(filepath, index_col=0)

data['de_ratio'] = data['totalLiab'] / data['totalStockholderEquity']

col = data['de_ratio'].agg('mean').transpose()

result = (col < 5) & (col > 0)
print(result)
