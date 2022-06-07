# Stock Analysis for Value Investing
#### Video Demo:  <URL HERE>
### Description:
This project implements a website that analyzes the “value” of a given company based on historical SEC filings. This tool allows the user to input a company’s ticker symbol, check the current price, and compare the current price to an estimated “sticker price” for the company based on value investing theory. 

From [investopedia:](https://www.investopedia.com/terms/v/valueinvesting.asp)

> Value investing is an investment strategy that involves picking stocks that appear to be trading for less than their intrinsic or book value. Value investors actively ferret out stocks they think the stock market is underestimating. They believe the market overreacts to good and bad news, resulting in stock price movements that do not correspond to a company's long-term fundamentals. The overreaction offers an opportunity to profit by buying stocks at discounted prices—on sale.

Value investing requires analysis of the financial position of a company using 5 key metrics to determine the estimated intrinsic value and “sticker price”. We want to see a comparison between the estimated sticker price and the current stock price. If the current stock price is much lower than the estimated sticker price, it may be a good time to buy!

### Specification

`scraper`
- Scrape public company data from [the SEC website](https://www.sec.gov/dera/data/financial-statement-data-sets.html). 10-k filings from the last 10 years should be downloaded and parsed if available. 

`management`
- Does the CEO buy stocks of the company? 
- Does the CEO own a large amount of stock?
- DE Ratio (0 < total liabilities/total shareholders’ equities < 5).
- Current Ratio (current assets/current liabilities > 1). 
- Durability (Long term debt/annual free cash flow < 3).

`key_metrics`
- Calculate the intrinsic value of a company based on the data available. 
- Return on Investment Capital. 
- Sales Growth Rate.
- Earnings Per Share Growth Rate.
- Equity Growth Rate (BVPS).
- Operating Cash Flow Growth Rate.

`sticker_price`
- Current EPS (TTM EPS).
- Future EPS growth rate (estimated).
- Based primarily on historical Equity (BVPS) growth rate, then on EPS, Sales, & Cash Flow growth rates.
- Compare to analyst’s 5 year projection [zacks.com - detailed estimates](https://www.zacks.com/stock/quote/NKE/detailed-estimates), use the lower of the 2.
- Future PE (estimated).
- Default future PE = EPS growth rate estimate x 2.
- Compare Default future PE to historical average PE, use lower of the 2.
- Minimum Acceptable Rate of Return % (Rule #1 MARR = 15%). value_investing
