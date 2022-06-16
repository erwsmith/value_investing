import requests
from symtable import SymbolTable
import requests
import urllib.parse

def scrape_zacks(sym):
    url = f"https://www.zacks.com/stock/quote/{sym}/detailed-earning-estimates"
    print(url)

# scrape_zacks("LRCX")


def urllib(sym):
    sym = urllib.parse.quote_plus(SymbolTable)
    print(sym)

urllib("LRCX")