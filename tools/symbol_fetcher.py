from tools.fetcher import fetch_stock_ticker
from langchain.tools import BaseTool
from pydantic import BaseModel, field_validator
from typing import Type
import log

class symbolFetcherInput(BaseModel):
    script_name : str 

class symbolFetcherOutput(BaseModel):
    tick_symbol: str = None

    @field_validator("tick_symbol")
    @classmethod
    def check_tick_symbol(cls, value):
        if value is None:
            return log.logger.warning("Symbol not found !!")
        
        return value
    
class symbolFetcherTool(BaseTool):
    name:str = "fetch_symbol"
    description:str = " Fetches the ticker symbol for a company"
    args_schema : Type[BaseModel] = symbolFetcherInput
    def _run(self,script_name:str)->str:
        try:
            if "." in script_name:
                tick_symbol = script_name
            else:
                tick_symbol = fetch_stock_ticker(script_name)

            if tick_symbol is None:
                log.logger.warning(f"Could not find the ticker symbol for {script_name}")
        
            validated_symbol = symbolFetcherOutput(tick_symbol=tick_symbol)
            return validated_symbol.model_dump_json(indent=2)
        
        except Exception as e:
            log.logger.exception(f"Data could not be fetched {e}")
            raise

    def _arun(self, script_name):
        raise NotImplementedError("Async not implemented !!")
