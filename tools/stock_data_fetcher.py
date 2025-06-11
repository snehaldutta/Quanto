import yfinance as yf
import log
from langchain_core.tools import tool
@tool
def stock_price_fetcher(symbol: str) -> str:
    """Fetches the current price, pe ratio, industry and description of the company """
    tick = yf.Ticker(symbol)
    price_attrs : list = ['regularMarketPrice', 'currentPrice', 'price']

    try:
        result : dict = {
            'current_price':None,
            'pe_ratio': None,
            'industry': None,
            'desc': None
        }
        for attr in price_attrs:
            if result['current_price'] is None and attr in tick.info and tick.info[attr] is not None:
                result['current_price'] = tick.info[attr]
            
        current_price = tick.fast_info.get('last_price')
        if current_price is not None:
            result['current_price'] = current_price
        
        if 'trailingPE' in tick.info and tick.info['trailingPE'] is not None:
            result['pe_ratio'] = tick.info['trailingPE']

        if 'industry' in tick.info and tick.info['industry'] is not None:
            result['industry'] = tick.info['industry']

        if 'longBusinessSummary' in tick.info and tick.info['longBusinessSummary'] is not None:
            result['desc'] = tick.info['longBusinessSummary'] 

        if result['current_price'] is None:
            log.logger.warning(f'Price not found for {symbol}')
        
        return result
    
    except Exception as e:
        log.logger.exception(f"Error fetching data for '{symbol}': {e}")
        raise