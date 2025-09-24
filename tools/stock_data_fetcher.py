import yfinance as yf
import log
from langchain_core.tools import BaseTool
from pydantic import BaseModel, field_validator
from typing import Optional, Type

class stockPriceFetcherInput(BaseModel):
    symbol : str = None

class stockPriceFetcherOutput(BaseModel):
    current_price : float = None
    pe_ratio: float = None
    industry: str = "Unknown"
    desc: Optional[str] = ""

    @field_validator("current_price")
    @classmethod
    def check_current_price(cls, value):
        if value is not None and value < 0:
            return log.logger.error("Not able to fetch the value !!")
        return value
    
    @field_validator("pe_ratio")
    @classmethod
    def check_pe_ratio(cls, value):
        if value is not None and value < 0:
            return log.logger.error("Not able to fetch the value !!")
        return value
    
    @field_validator("industry")
    @classmethod
    def check_industry(cls, value):
        if value == "Unknown":
            return log.logger.error("Not able to fetch the value !!")
        return value
    

class stockPriceFetcherTool(BaseTool):
    name: str = "stock_price_fetcher"
    description: str = "Fetches the current price, pe ratio, industry and description of the company"
    args_schema : Type[BaseModel] = stockPriceFetcherInput
    def _run(self,symbol: str) -> str:
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
            
            validated_res = stockPriceFetcherOutput(**result)
            return validated_res.model_dump_json(indent=2)
        
        except Exception as e:
            log.logger.exception(f"Error fetching data for '{symbol}': {e}")
            raise


    def _arun(self, symbol:str):
        raise NotImplementedError("Not implemented async yet !!")