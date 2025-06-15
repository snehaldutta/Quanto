import yfinance as yf
import pandas as pd
import log
from data_cleaning import clean_data_quarterly
from langchain_core.tools import BaseTool
from pydantic import BaseModel, field_validator, ConfigDict
from typing import Type, Dict, Any

class stockTechnicalsInput(BaseModel):
    symbol: str

class stockTechnicalsOutput(BaseModel):
    clean_data: pd.DataFrame =None
    model_config = ConfigDict(arbitrary_types_allowed=True)

    @field_validator("clean_data")
    @classmethod
    def check_quarter_data(cls, value):
        if value is not None:
            not_na = value.isna().sum().sum()
            if not_na != 0:
                return log.logger.warning("NAN values present !!")
            return value
        
class stockTechnicalsTool(BaseTool):
    name : str = "stock_price_technicals"
    description: str = "It fetches the quarterly data of a company"
    args_schema: Type[BaseModel] = stockTechnicalsInput
    def _run(self,symbol:str)-> Dict[str, Any]:
        tick = yf.Ticker(symbol)
        
        try:
            quarter_results = tick.quarterly_financials
            if quarter_results is None or quarter_results.empty:
                    log.logger.warning(f"No valid quarterly results found for {symbol}")
            
            else:
                clean_quater_data = clean_data_quarterly(quarter_results)
                validated_quarter_data = stockTechnicalsOutput(clean_data=clean_quater_data)
                val_data = validated_quarter_data.clean_data
                inp_data = val_data.reset_index()
                return {
                    # 'markdown_df': inp_data.to_markdown(index=False),
                    "json_df": inp_data.to_json(orient='records')
                }
        except Exception as e:
            log.logger.exception(f'Data not found for the symbol {symbol}: {e}')
            raise


    def _arun(self, symbol:str):
        raise NotImplementedError("Async not implemented !!")