import yfinance as yf
from tools.technicals import calculate_rsi
import pandas as pd
import log
from data_cleaning import clean_data_history
from langchain_core.tools import tool

@tool
def stock_hist_data(symbol: str, period:str ='6mo')-> pd.DataFrame:
    """ It fetches the company's historical data for analysis"""
    tick = yf.Ticker(symbol)

    try:
        hist_data = tick.history(period=period)
        hist_data['EMA_10'] = hist_data['Close'].ewm(span=10,adjust=False).mean()
        hist_data['RSI_14'] = calculate_rsi(hist_data['Close'],14)
        clean_hist_data = clean_data_history(hist_data)
        return clean_hist_data
    
    except Exception as e:
        log.logger.exception(f"Error in fetching the historical data '{symbol}'as {e}")
        raise