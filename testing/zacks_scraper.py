import os
import requests
from symtable import SymbolTable
import requests
import urllib.parse
import bs4

def scrape_zacks():
    url = f"https://www.zacks.com/stock/quote/{sym}/detailed-earning-estimates"
    # url = "https://books.toscrape.com/"    
    response = requests.get(url)
    data = response.json()
    print(data)
    # print(response)
    # soup = bs4.BeautifulSoup(response.text,'lxml')
    # print(soup)

# scrape_zacks("LRCX")
scrape_zacks()