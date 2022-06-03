import re

var = "secret message"

Company_Name = re.search('main(.*)string', f"this is the main {var} string to search").group(1)

print(Company_Name)