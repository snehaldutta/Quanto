from langchain_ollama import ChatOllama
from langchain.prompts import PromptTemplate
from langchain.agents import initialize_agent, AgentType
from tools.stock_data_fetcher import stockPriceFetcherTool
from tools.stock_hist_data import stockHistDataTool
from tools.symbol_fetcher import symbolFetcherTool
from tools.stock_technical_data import stockTechnicalsTool

with open('system_prompt.txt', 'r') as file:
    sys_prompt = file.read()

suffix = """Question: {input}
{agent_scratchpad}"""

prompt = PromptTemplate(
    input_variables=['input', 'agent_scratchpad'],
    template=f"{sys_prompt}\n\n{suffix}"
)

tools = [
    symbolFetcherTool(),
    stockPriceFetcherTool(),
    stockHistDataTool(),
    stockTechnicalsTool()
]

llm = ChatOllama(
    model="qwen3:1.7b",
    num_ctx=8000,
    temperature=0.10,
    extract_reasoning=True
)

# initialize_agent returns an AgentExecutor already
agent_exec = initialize_agent(
    llm=llm,
    tools=tools,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
    agent_kwargs={'prompt': prompt},
    handle_parsing_errors=True  
)

stock_name = "Rail Vikas Nigam Limited"
query = f"""Should I buy or sell {stock_name}? 
Please provide a detailed stock recommendation that includes:
1. Valuation status (undervalued or overvalued),
2. A clear BUY or SELL action (no ambiguity),
3. A confidence score from 0 to 100 based on technicals, fundamentals, and market conditions,
4. Brief industry or company-level context that justifies your position."""

res = agent_exec.invoke({"input": query})

# print(res)