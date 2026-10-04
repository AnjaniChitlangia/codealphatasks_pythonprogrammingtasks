# Stock Portfolio Tracker

A Python program that calculates your total investment using a hardcoded
dictionary of stock prices.

## Features
- Enter stock name, quantity and the price you bought at
- Shows amount invested, current amount and profit/loss for each stock and in total
- Year-by-year expected value over the number of years you plan to hold
- Target selling price (default 15% if holding more than 10 years, otherwise 12%)
  with the amount you'd get if sold at target
- Step-by-step calculation of the estimated amount and expected return at the end
- Custom scenario: choose your own rate and tenure (default 15% for 10+ years, 12% for less)
- Top 3 stocks to consider, ranked from the sample data, with an optional budget split
- Save results to `.txt` and/or `.csv`

## Run
```
python portfolio_tracker.py
```

`portfolio_report.txt` and `portfolio_report.csv` are sample outputs.

> Prices and return rates are sample values for learning, not live data or financial advice.
