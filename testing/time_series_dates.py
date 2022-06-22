import json
import pandas as pd

pd.options.display.float_format = '{:,.2f}'.format
sym = "ALK"
func = "TIME_SERIES_MONTHLY_ADJUSTED"
filepath = f"/Users/Eric/repos/value_investing/json_files/{sym}_{func}.json"
with open(filepath, "r+") as f:
    data = f.read()

price_history = json.loads(data)
price_history_dict = {}
dates = []
i = 0

for i, date in enumerate(price_history["Monthly Adjusted Time Series"]):
    if i == 0 or i % 12 == 0:
        price_history_dict[date] = price_history["Monthly Adjusted Time Series"][date]["5. adjusted close"]
        i += 1
        dates.append(date)
    elif len(dates) == 6:
        break

df_price = pd.DataFrame.from_dict(price_history_dict, orient="index", columns=["price"])
df_price["date"] = df_price.index
df_price["date"] = pd.to_datetime(df_price["date"])
df_price["year"] = pd.DatetimeIndex(df_price["date"]).year
df_price.set_index("year", inplace=True)
df_price.drop(["date"], axis=1, inplace=True)
df_price = df_price.sort_index()

print(df_price)