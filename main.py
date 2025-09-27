from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.agents import initialize_agent, AgentType
from tools.stock_data_fetcher import stockPriceFetcherTool
from tools.stock_hist_data import stockHistDataTool
from tools.symbol_fetcher import symbolFetcherTool
from tools.stock_technical_data import stockTechnicalsTool
from dotenv import load_dotenv
import warnings
import log
import os
import json
load_dotenv() 
warnings.filterwarnings("ignore")

API_K = os.getenv('API_KEY')
BASE_U = os.getenv('BASE_URL')

with open('prompts/system_prompt_v1.json', 'r') as file:
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
    stockPriceFetcherTool(),
    stockHistDataTool(),
    stockTechnicalsTool()
]
try:
    log.logger.info("Initialising the model .....")
    llm = ChatOpenAI(
        api_key=API_K,
        base_url=BASE_U,
        model="meta-llama/llama-3.3-8b-instruct:free",
        temperature=0.10
    )
    log.logger.info("✅ Initialised successfully !!")

except Exception as e:
    log.logger.error("❌ Not initialised successfully")
    raise
# initialize_agent returns an AgentExecutor already
agent_exec = initialize_agent(
    llm=llm,
    tools=tools,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
    agent_kwargs={'prompt': prompt},
    handle_parsing_errors=True  
)

stock_name = "Radico Khaitan Limited"
query = f"""Should I buy or sell {stock_name}? 
Please provide a detailed stock recommendation that includes:
1. Valuation status (undervalued or overvalued),
2. A clear BUY or SELL action (no ambiguity),
3. A confidence score from 0 to 100 based on technicals, fundamentals, and market conditions,
4. Brief industry or company-level context that justifies your position."""

res = agent_exec.invoke({"input": query})

print(res['output'])