import yfinance as yf
from technicals import calculate_rsi
import pandas as pd

def stock_hist_data(symbol: str, period:str ='6mo')-> pd.DataFrame:
    tick = yf.Ticker(symbol)

    try:
        hist_data = tick.history(period=period)
        hist_data['EMA_10'] = hist_data['Close'].ewm(span=10,adjust=False).mean()
        hist_data['RSI_14'] = calculate_rsi(hist_data['Close'],14)
        return hist_data
    
    except Exception as e:
        raise Exception(f"Error in fetching the historical data '{symbol}'as {e}")