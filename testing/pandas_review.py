import pandas as pd

data = {'Country': ['Denmark'] * 3 + ['Sweden'] * 3,
        'Year': [2000, 2010, 2020, 2000, 2010, 2020],
        'Population': [5.3, 5.5, 5.8, 8.8, 9.3, 10.2]}

df = pd.DataFrame(data)

# print(df)
# print(df['Population'])
# print(df.iloc[1:2])
# print(df.loc[1:2])

print(df.loc[1:2, 'Year'])
