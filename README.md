Stock Analysis for Value Investing
==================================

* * *

### [Video Demo](https://youtu.be/dQw4w9WgXcQ)

* * *

### Description

  

This project builds upon the CS50X finance problem set to implement a website that analyzes the “value” of a given company based on historical SEC filings. This tool allows the user to input a company’s ticker symbol, check the current price, and compare the current price to an estimated “sticker price” for the company based on value investing theory.

  

Value investing requires analysis of the financial position of a company using several key metrics to determine the estimated intrinsic value and “sticker price”. We want to see a comparison between the estimated sticker price and the current stock price. If the current stock price is much lower than the estimated sticker price, it may be a good time to buy!

  

From [investopedia.com](https://www.investopedia.com/terms/v/valueinvesting.asp):

> Value investing is an investment strategy that involves picking stocks that appear to be trading for less than their intrinsic or book value. Value investors actively ferret out stocks they think the stock market is underestimating. They believe the market overreacts to good and bad news, resulting in stock price movements that do not correspond to a company's long-term fundamentals. The overreaction offers an opportunity to profit by buying stocks at discounted prices—on sale.

* * *

### Specification

  

#### `helpers.py`

`lookup()`

*   This function takes in the company's ticker symbol and the desired API function, and outputs the response in json format.
*   The source of the data is [alphavantage.](https://www.alphavantage.co/)

`read_financial_reports()`

*   This function calls lookup() to get the company's financial reports from alphavantage:
*   Balance Sheet.
*   Cash Flow Statement.
*   Income Statement.
*   After reading in the financial reports, the following values are calculated:
    *   Debt to Equity (DE) Ratio.
    *   Current Ratio.
    *   Long Term Debt.
    *   Invested Capital.
    *   Shares Outstanding.
    *   Total Shareholder Equity.
    *   Free Cash Flow.
    *   Non Operating Cash.
    *   Operating Cash Flow.
    *   Net Operating Profit After Tax (NOPAT).
    *   Total Revenue.
    *   Net Income.
*   These values, required for evaluating company management and growth, are combined and returned as a single pandas dataframe.

`read_overview()`

*   This funciton calls lookup() to read in the company "overview" data from alphavantage.
*   The required data is normalized and returned as a pandas dataframe .

`management()`

*   This function takes in the financial reports dataframe and returns a management check and a dataframe with key values for evaluating company management:
*   DE Ratio (0 < total liabilities / total shareholder equity < 5).
*   Current Ratio (current assets / current liabilities > 1).
*   Durability (Long term debt / annual free cash flow < 3).
*   Return on Investment Capital (NOPAT / invested capital > 10%).

`growth()`

*   This function calculates 4 key growth rates and returns them as a pandas dataframe:
    *   Sales (Revenue) Growth Rate.
    *   Earnings Per Share Growth Rate.
    *   Equity (BVPS) Growth Rate.
    *   Operating Cash Flow Growth Rate.

`read_time_series_monthly()`

*   This function calls lookup() to get historical pricing data.
*   Data must be pared down to include only one sample per year over the last 5 years.
*   A pandas dataframe is returned with this 5 year pricing history.

`yahoo_growth()`

*   This function uses the selenium web automation package to scrape the analyst 5 year estimated growth rate from [yahoo finance](finance.yahoo.com).
*   Getting the desired data point required using the full xpath

`sticker_price()`

*   This function takes in the financial reports and overview dataframes and returns the company's sticker price and "safe price"
*   In order to find the sticker price, the following numbers are required:
    *   Current EPS (TTM EPS).
    *   Future EPS growth rate (estimated). This is based primarily on historical Equity (BVPS) growth rate, then on EPS, Sales, & Cash Flow growth rates.
        *   Compare to analyst’s 5 year growth projection obtained in yahoo\_growth(), use the lower of the 2.
    *   Future PE (estimated).
    *   Default future PE = EPS growth rate estimate x 2.
        *   Compare Default future PE to historical average PE, use lower of the 2.
    *   Minimum Acceptable Rate of Return % (Rule #1 MARR = 15%).
*   The "safe price" is simply the sticker price / 2. It is the recommended maximum purchase price, representing a "safe" discount

  

#### `app.py`

`evaluate()`

*   This function calls several functions from helpers.py to process company data, and returns the output at evaluated.html.
*   The discount value is calculated based on the sticker price and the current price. This determines if the company is undervalued, and if it is "fully discounted" (half off the sticker price).
*   The management of the company is evaluated, if the company passes all management checkes, the managment is rated as "wonderful"
*   The growth of the company is evaluated, if the company passes all growth checks, the company's growth is rated as "wonderful".
*   The data sent to evaluated.html allows the user to quickly see if the company is an attractive "buy" or not.
