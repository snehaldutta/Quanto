import yfinance as yf

def stock_price_fetcher(symbol: str) -> str:
    tick = yf.Ticker(symbol)
    price_attrs : list = ['regularMarketPrice', 'currentPrice', 'price']

    try:
        result : dict = {
            'current_price':None,
            'pe_ratio': None
        }
        for attr in price_attrs:
            if result['current_price'] is None and attr in tick.info and tick.info[attr] is not None:
                result['current_price'] = tick.info[attr]
            
        current_price = tick.fast_info.get('last_price')
        if current_price is not None:
            result['current_price'] = current_price
        
        if 'trailingPE' in tick.info and tick.info['trailingPE'] is not None:
            result['pe_ratio'] = tick.info['trailingPE']

        if result['current_price'] is None:
            raise Exception(f'Price not found for {symbol}')
        
        return result
    
    except Exception as e:
        raise Exception(f"Error fetching data for '{symbol}': {e}")