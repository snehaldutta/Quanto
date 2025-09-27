from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.agents import initialize_agent, AgentType
from tools.stock_hist_data import stockHistDataTool
from tools.symbol_fetcher import symbolFetcherTool
from dotenv import load_dotenv
import log
import os
import json
import warnings
load_dotenv() 

warnings.filterwarnings("ignore")

API_K = os.getenv('API_KEY')
BASE_U = os.getenv('BASE_URL')

with open('prompts/csv_agent_prompt_v1.json', 'r') as file:
    sys_prompt = json.load(file)

system_prom = json.dumps(sys_prompt, indent=2)
suffix = """Question: {input}
{agent_scratchpad}"""

prompt = PromptTemplate(
    input_variables=['input', 'agent_scratchpad'],
    template=f"{system_prom}\n\n{suffix}"
)

tools = [
    symbolFetcherTool(),
    stockHistDataTool()
]
try:
    log.logger.info("Initialising the model .....")
    llm = ChatOpenAI(
        api_key=API_K,
        base_url=BASE_U,
        model="qwen/qwen3-8b:free",
        temperature=0.10
    )
    log.logger.info("✅ Initialised successfully !!")

except Exception as e:
    log.logger.error("❌ Not initialised successfully")
    raise

csv_agent = initialize_agent(
    llm=llm,
    tools=tools,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
    agent_kwargs={'prompt': prompt},
    handle_parsing_errors=True 
)

stock_name = "Radico Khaitan Limited"
query = f"""Analyze {stock_name} and provide a JSON output with the following fields:
1. valuation_status: whether the stock is undervalued or overvalued,
2. action: a decisive BUY or SELL recommendation (no ambiguity),
3. confidence_score: an integer from 0 to 100 based on RSI and EMA signals,
4. technical_summary: calculated RSI value, EMA trend (bullish/bearish/neutral), and momentum insights,
5. insights: plain-language reasoning about the stock's trend, support/resistance, and momentum.

Only output valid JSON, nothing else."""

res = csv_agent.invoke({"input": query})

print(res['output'])