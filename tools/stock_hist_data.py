import yfinance as yf
from tools.technicals import calculate_rsi
import pandas as pd
import log
from data_cleaning import clean_data_history
from langchain_core.tools import BaseTool
from pydantic import BaseModel, field_validator
from typing import Type, Any, Dict
class stockHistDataInput(BaseModel):
    symbol : str
class stockHistDataOuput(BaseModel):
    clean_data: pd.DataFrame = None

    @field_validator
    @classmethod
    def check_clean_data(cls,value: pd.DataFrame):
        if value is not None:
            not_na = value.isna().sum().sum()
            if not_na != 0:
                return log.logger.warning("NAN values present !!")

        return value
class stockHistDataTool(BaseTool):
    name = "stock_hist_data"
    description = "It fetches the company's historical data for analysis"
    args_schema: Type[BaseModel] = stockHistDataInput
    def _run(self, symbol: str, period:str ='6mo')-> Dict[str, Any]:

        tick = yf.Ticker(symbol)

        try:
            hist_data = tick.history(period=period)
            hist_data['EMA_10'] = hist_data['Close'].ewm(span=10,adjust=False).mean()
            hist_data['RSI_14'] = calculate_rsi(hist_data['Close'],14)
            clean_hist_data = clean_data_history(hist_data)

            validated_data = stockHistDataOuput(clean_data=clean_hist_data)
            val_data = validated_data.clean_data
            inp_data = val_data.tail(20).reset_index()
            return {
                "markdown_data": inp_data.to_markdown(index=False),
                'json_data': inp_data.to_json(orient='records')
            }

        except Exception as e:
            log.logger.exception(f"Error in fetching the historical data '{symbol}'as {e}")
            raise
    
    def _arun(self, symbol:str):
        raise NotImplementedError("Async is not implemented !!")