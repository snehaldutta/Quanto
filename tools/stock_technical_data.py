import yfinance as yf
import pandas as pd

def stock_price_technicals(symbol:str)-> pd.DataFrame:
    tick = yf.Ticker(symbol)
    
    try:
       quarter_results = tick.quarterly_financials
       if quarter_results is None or quarter_results.empty:
            raise ValueError(f"No valid quarterly results found for {symbol}")
       
       else:
           return quarter_results
    except Exception as e:
        raise ValueError(f'Data not found for the symbol {symbol}')