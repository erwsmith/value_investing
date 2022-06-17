from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select

import time

path = "/usr/local/bin"
driver = webdriver.Chrome()

# # google search working example
# driver.get("https://www.google.com")
# time.sleep(1)
# search_box = driver.find_element_by_name("q")
# search_box.send_keys("funny cat meme")
# search_box.submit()
# time.sleep(2)
# driver.close()

# # books.toscrape webscraping sandbox example
# url = "https://books.toscrape.com/"
# driver.get(url)
# elements = driver.find_elements(By.CLASS_NAME, "price_color")
# e_list = []
# for e in elements:
#     e_list.append(e.text)
# print(e_list)
# driver.close()

# # non-functioning stub for yahoo finance
# sym = "LRCX"
# url = f"https://finance.yahoo.com/quote/LRCX/analysis?p={sym}"
# driver.get(url)
# select_element = driver.find_element(By.CLASS_NAME, "Ta(end) Py(10px)")
# select_object = Select(select_element)
# select_object.select_by_index(1)
# all_selected_options = select_object.all_selected_options
# print(all_selected_options)
# driver.close()