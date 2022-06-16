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

# You can find company's CIK number at https://www.sec.gov/edgar/scearchedgar/companysearch.html
company_CIKs = ['707549']
# Enter what forms(s) you want to extract using the '10-K', '10-Q', '8-K' format.
filing_types = ['10-k']
# Enter the database name that you want to use and populate.
#The database will be automatically created if it does not exist.
db_name = 'lam.db'
# Specify the folder path for DB file. For example "C:\sqlite\db"
folder_path = r"/Users/Eric/99841919/CS50X/10_final/value_investing/data"
db_path = f"{folder_path}/{db_name}"
# Enter the date range for the filings in the 'YYYY-MM-DD' format
start_date = '2020-01-01'
end_date = '2022-01-01'


# Create a class to handle connection(s) to SQLite database(s).
class DB_Connection:

    # Initialize the object's attributes.
    def __init__(self, db_name, folder_path, db_path):
        self.db_name = db_name
        self.folder_path = folder_path

    # Create a directory for the DB file if the directory does not exist.
    def create_folder(self):
        if not os.path.exists(self.folder_path):
            os.makedirs(self.folder_path)
            print(f'Successfully created a new folder path {self.folder_path}.')
        else:
            print(f'Folder path {self.folder_path} already exists.')

    # Open connection to the database, if connection fails abort the program.
    # If the DB file does not already exist, it will be automatically created.
    @classmethod
    def open_conn(cls, db_path):
        try:
            cls.conn = sqlite3.connect(db_path)
            print(f'Successfully connected to the {db_path} database.')
            return cls.conn
        except sqlite3.Error as e:
            print(f'Error occurred, unable to connect to the {db_path} database.\
                    \n{e}\nAborting program.')
            # sys.exit(0) means the program is exiting without any errors
            # sys.exit(1) means there was an error.
            sys.exit(1)
    # Close connection to the database.
    @classmethod
    def close_conn(cls):
        try:
            cls.conn.commit()
            print('Committed transactions.')
            cls.conn.close()
            print('Closing all database connections.')
        except Exception as e:
            print(f'Unable to close database connection.\n{e}')


class Filing_Links:

    def __init__(self, company_CIKs, filing_types, start_date, end_date):
            self.company_CIKs = company_CIKs
            # Capitalize the letters of form type, since by default SQLite is case sensitive.
            self.filing_types = [item.upper() for item in filing_types]
            self.start_date = start_date
            self.end_date = end_date

    # Get available filings types for a specific company and their respective links.
    def Get_Filing_Links(self):
        try:
            for Company_CIK_Number in self.company_CIKs:
                for Filing_Type in self.filing_types:
                    # define our parameters dictionary
                    filing_parameters = {'action':'getcompany',
                                  'CIK':Company_CIK_Number,
                                  'type':Filing_Type,
                                  'dateb':'',
                                  'owner':'exclude',
                                  'start':'',
                                  'output':'',
                                  'count':'100'}

                    # request the url, and then parse the response.
                    response = requests.get(url = r"https://www.sec.gov/cgi-bin/browse-edgar",
                                            params = filing_parameters)
                    # Add 0.1 second time delay to comply with SEC.gov's 10 requests per second limit.
                    time.sleep(0.1)
                    soup = BeautifulSoup(response.content, 'html.parser')
                    # Find the document table that contains filing information.
                    main_table = soup.find_all('table', class_='tableFile2')
                    # The base URL will be used to construct document links URLs.
                    sec_base_url = r"https://www.sec.gov"
                    Company_Name_path=str(soup.find('span',{'class':'companyName'}))
                    if Company_Name_path != None:
                        try:
                            Company_Name = re.search('<span class="companyName">(.*)<acronym title',
                                                     Company_Name_path).group(1)
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

                            except Exception as e:
                                """
                                Add break if you don't want empty account number rows.
                                If account number is not present, the interactive document
                                link will not be available. If the interactive link is not
                                present, we will not be able to extract the individual
                                tables containing financial statements..
                                """
                                Account_Number = None
                                print(f'Could not retrieve the account number, \
                                        assigning NULL value.\n{e}')

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

                            self.info_to_sql(Company_Name, Company_CIK_Number, Account_Number,
                                             Filing_Type, Filing_Number, Filing_Date, Document_Link,
                                             Interactive_Data_Link, Filing_Number_Link, Summary_Link_Xml)
        except Exception as e:
            print(f"Could not retrieve the table containing the necessary information.\
                    \nAborting the program.\nIf index list is out of range, make sure \
                    that you entered the correct CIK number(s).\n{e}")
            sys.exit(1)

    # Migrate the DataFrame containing, filing and document links information to a local SQLite database.
    def info_to_sql(self, Company_Name, Company_CIK_Number, Account_Number,
                    Filing_Type, Filing_Number, Filing_Date, Document_Link,
                    Interactive_Data_Link, Filing_Number_Link, Summary_Link_Xml):

        with DB_Connection.open_conn(db_path) as conn:
            try:
                with closing(conn.cursor()) as cursor:
                    cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS filing_list (
                    filing_number integer PRIMARY KEY,
                    account_number integer,
                    company_name text NOT NULL,
                    cik integer NOT NULL,
                    filing_type text NOT NULL,
                    filing_date text NOT NULL,
                    document_link_html TEXT NOT NULL,
                    filing_number_link TEXT NOT NULL,
                    interactive_dash_link TEXT,
                    summary_link_xml TEXT
                    )
                    ;""")
            except ValueError as e:
                print(f"Error occurred while attempting to create filing_list table.\
                        \nAborting the program.\n{e}")
                sys.exit(1)
            else:
                print("Successfully created the table.")
                print(f"Migrating information for filing number {Filing_Number} to the SQL table.......")
                try:
                    # INSERT or IGNORE will insert a record if it does NOT duplicate an existing record.
                    with closing(conn.cursor()) as cursor:
                        cursor.execute(
                        """
                        INSERT or IGNORE INTO filing_list (
                        filing_number,
                        account_number,
                        company_name,
                        cik,
                        filing_type,
                        filing_date,
                        document_link_html,
                        filing_number_link,
                        interactive_dash_link,
                        summary_link_xml
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?) """
                        ,(
                        Filing_Number,
                        Account_Number,
                        Company_Name,
                        Company_CIK_Number,
                        Filing_Type,
                        Filing_Date,
                        Document_Link,
                        Filing_Number_Link,
                        Interactive_Data_Link,
                        Summary_Link_Xml
                         ))
                except ValueError as e:
                    print(f"Error occurred while attempting to insert values into the filing_list table.\n{e}")

        DB_Connection.close_conn()

connection1 = DB_Connection(db_name, folder_path, db_path)
connection1.create_folder()
filings1 = Filing_Links(company_CIKs, filing_types, start_date, end_date)
filings1.Get_Filing_Links()