from tools.stock_data_fetcher import stock_price_fetcher
import log
def fetch_symbol(script_name:str)->str:
    if "." in script_name:
        tick_symbol = script_name
    else:
        tick_symbol = stock_price_fetcher(script_name)

    if tick_symbol is None:
        log.logger.warning(f"Could not find the ticker symbol for {script_name}")
    
    return tick_symbol