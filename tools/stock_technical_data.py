import yfinance as yf
import pandas as pd
import log
from data_cleaning import clean_data_quarterly
from langchain_core.tools import tool

@tool
def stock_price_technicals(symbol:str)-> pd.DataFrame:
    tick = yf.Ticker(symbol)
    
    try:
       quarter_results = tick.quarterly_financials
       if quarter_results is None or quarter_results.empty:
            log.logger.warning(f"No valid quarterly results found for {symbol}")
       
       else:
           clean_quater_data = clean_data_quarterly(quarter_results)
           return clean_quater_data
    except Exception as e:
        log.logger.exception(f'Data not found for the symbol {symbol}: {e}')
        raise