import requests
import requests_random_user_agent # pip install requests-random-user-agent
import pandas as pd
from bs4 import BeautifulSoup # pip install beautifulsoup4
import re
import sqlite3
from sqlite3 import Error
import os
import sys
from contextlib import closing # pip install contextlib2
import time
from dateutil import parser # pip install python-dateutil
from datetime import datetime
import csv

Company_CIK_Number = '707549'

def Get_Filing_Links():
    filing_parameters = {'action':'getcompany',
                        'CIK':Company_CIK_Number,
                        'type':'10-k',
                        'dateb':'',
                        'owner':'exclude',
                        'start':'',
                        'output':'',
                        'count':'100'}

    # request the url, and then parse the response.
    response = requests.get(url = r"https://www.sec.gov/cgi-bin/browse-edgar", params = filing_parameters)

    soup = BeautifulSoup(response.content, 'html.parser')

    # Find the document table that contains filing information.
    main_table = soup.find_all('table', class_='tableFile2')

    # The base URL will be used to construct document links URLs.
    sec_base_url = r"https://www.sec.gov"
    Company_Name_path=str(soup.find('span',{'class':'companyName'}))
    # print(Company_Name_path)

    if Company_Name_path != None:
        try:
            Company_Name = re.search('<span class="companyName">(.*)<acronym title',
                                        Company_Name_path).group(1)
            # print(Company_Name)
        except AttributeError:
            print("Could not find company name, \
                    assigning NULL value to company name.")
            Company_Name = None

    # loop through each row of table and extract filing numbers, links, etc.
    for row in main_table[0].find_all('tr'):
        # find all the rows under the 'td' element.
        cols = row.find_all('td')
        # If no information was detected, move on to the next row.
        if len(cols) != 0:
            # Get the text from the table.
            Filing_Type = cols[0].text.strip()
            Filing_Date = cols[3].text.strip()
            Filing_Number = cols[4].text.strip()
            Filing_Number = ''.join(e for e in Filing_Number if e.isalnum())

            # Get the URL path to the filing number.
            filing_number_path = cols[4].find('a')
            if filing_number_path != None:
                Filing_Number_Link = sec_base_url + filing_number_path['href']
            else:
                break

            # Get the URL path to the document.
            document_link_path = cols[1].find('a',
                                                {'href':True, 'id':'documentsbutton'})
            if document_link_path != None:
                Document_Link = sec_base_url + document_link_path['href']
            else:
                Document_Link = None

            # Get the account number.
            try:
                Account_Number= cols[2].text.strip()
                Account_Number = re.search('Acc-no:(.*)(34 Act)',
                                            Account_Number).group(1)
                Account_Number = ''.join(e for e in Account_Number if e.isalnum())
                # print(Account_Number)

            except Exception as e:
                """
                Add break if you don't want empty account number rows.
                If account number is not present, the interactive document
                link will not be available. If the interactive link is not
                present, we will not be able to extract the individual
                tables containing financial statements..
                """
                Account_Number = None
                # print(f'Could not retrieve the account number, \
                #         assigning NULL value.\n{e}')

            # Get the URL path to the interactive document.
            interactive_data_path = cols[1].find('a',
                                                    {'href':True, 'id':'interactiveDataBtn'})
            if interactive_data_path != None:
                Interactive_Data_Link = sec_base_url + interactive_data_path['href']
                # If the interactive data link exists, then so does the FilingSummary.xml link.
                Summary_Link_Xml = Document_Link.replace(f"/{Account_Number}",'')\
                                                .replace('-','')\
                                                .replace('index.htm' ,'/FilingSummary.xml')
            else:
                # break
                Interactive_Data_Link = None
                Summary_Link_Xml = None

            print(Company_Name, Company_CIK_Number, Account_Number, Filing_Type,
                            Filing_Number, Filing_Date, Document_Link, Interactive_Data_Link,
                            Filing_Number_Link, Summary_Link_Xml)

Get_Filing_Links()