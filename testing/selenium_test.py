from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select

import time

path = "/usr/local/bin"
options = Options()
options.headless = True
options.add_argument("--window-size=192,120")
driver = webdriver.Chßrome(options=options)

# yahoo finance
sym = "LRCX"
url = f"https://finance.yahoo.com/quote/LRCX/analysis?p={sym}"
driver.get(url)
full_xpath = "/html/body/div[1]/div/div/div[1]/div/div[3]/div[1]/div/div[1]/div/div/section/table[6]/tbody/tr[5]/td[2]"
element = driver.find_element(by=By.XPATH, value=full_xpath)
print(element.text)
driver.close()

# google search working example
# driver.get("https://www.google.com")
# time.sleep(1)
# search_box = driver.find_element_by_name("q")
# search_box.send_keys("funny cat meme")
# search_box.submit()
# time.sleep(2)
# driver.close()

# books.toscrape webscraping sandbox working example
# url = "https://books.toscrape.com/"
# driver.get(url)
# elements = driver.find_elements(By.CLASS_NAME, "price_color")
# e_list = []
# for e in elements:
#     e_list.append(e.text)
# print(e_list)
# driver.close()

# books.toscrape webscraping sandbox another working example, using full XPATH
# url = "https://books.toscrape.com/"
# driver.get(url)
# element = driver.find_element(by=By.XPATH, value="/html/body/div/div/div/div/section/div[2]/ol/li[2]/article/div[2]/p[1]")
# print(element.text)
# driver.close()