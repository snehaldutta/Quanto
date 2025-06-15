from langchain_ollama import ChatOllama
from langchain.prompts import PromptTemplate
from langchain.agents import initialize_agent, AgentType
from tools.stock_data_fetcher import stockPriceFetcherTool
from tools.stock_hist_data import stockHistDataTool
from tools.symbol_fetcher import symbolFetcherTool
import log

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
    stockHistDataTool()
]

llm = ChatOllama(
    model="qwen3:1.7b",
    num_ctx=4096,
    temperature=0.15,
    extract_reasoning=True
)

# initialize_agent returns an AgentExecutor already
agent_exec = initialize_agent(
    llm=llm,
    tools=tools,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
    agent_kwargs={'prompt': prompt},
    handle_parsing_errors=True  # pass this here if you want parsing error handling
)

stock_name = "Rail Vikas Nigam Limited"
query = f"Give me an analysis whether to buy or sell {stock_name} and detailed recommendation"

# Pass input as dict to match prompt input variables
res = agent_exec.invoke({"input": query})

print(res)