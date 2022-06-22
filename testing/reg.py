import re

# var = "secret message"

# Company_Name = re.search('main(.*)string', f"this is the main {var} string to search").group(1)

# print(Company_Name)


date = "2022-06-16"
print(re.search("^2022-06-", date).group())

# dates = ["2022-06-16", "2021-06-30", "2020-06-30", "2019-06-28", "2018-06-29", "2017-06-30"]
# print(date in dates)