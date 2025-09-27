from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.agents import initialize_agent, AgentType
from tools.stock_hist_data import stockHistDataTool
from tools.symbol_fetcher import symbolFetcherTool
from dotenv import load_dotenv
import log
import os
load_dotenv() 

API_K = os.getenv('API_KEY')
BASE_U = os.getenv('BASE_URL')

tools = [
    symbolFetcherTool(),
    stockHistDataTool()
]
csv_agent = initialize_agent(

)