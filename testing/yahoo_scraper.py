import os
import requests
from symtable import SymbolTable
import requests
import urllib.parse
import bs4

def yahoo_scraper():
    url = f"https://finance.yahoo.com/quote/LRCX/analysis?p=LRCX"
    # url = "https://finance.yahoo.com/quote/LRCX?p=LRCX"
    response = requests.get(url)
    soup = bs4.BeautifulSoup(response.text,'lxml')
    print(soup)
    # print(soup.select(".Ta\(end\) Py\(10px\)"))

    # for item in soup.select(".Ta\(end\) Py\(10px\)"):
    #     print(item.text)

    # for item in soup.select(".reportReactMarkupDiff has-scrolled"):
    #     print(item.text)

    # for tag in soup.find_all(True):
    #     if tag.name == "table":
    #         print(tag)

yahoo_scraper()