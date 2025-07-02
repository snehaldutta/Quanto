from langchain_ollama import ChatOllama
from langgraph.prebuilt import create_react_agent
from langgraph_supervisor import create_supervisor
from tools.stock_data_fetcher import stockPriceFetcherTool
from tools.stock_hist_data import stockHistDataTool
from tools.symbol_fetcher import symbolFetcherTool
from tools.stock_technical_data import stockTechnicalsTool
from langchain_core.messages import HumanMessage

with open("sys_prompt_langgraph.txt","r") as file:
    sys_prompt = file.read()

llm = ChatOllama(
    model="qwen3:1.7b",
    num_ctx=8000,
    temperature=0.10,
    extract_reasoning=True,
    system=sys_prompt
)
fundamentals_analyst = create_react_agent(
    model=llm,
    tools=[symbolFetcherTool(),stockPriceFetcherTool()],
    name="transfer_to_fundamentals_expert"
)

technicals_analyst = create_react_agent(
    model=llm,
    tools=[symbolFetcherTool(),stockHistDataTool(), stockTechnicalsTool()],
    name="transfer_to_technicals_expert"
)

wrkflw = create_supervisor(
    [fundamentals_analyst, technicals_analyst],
    model=llm
)

stock_name = "Rail Vikas Nigam Limited"
query = f"""Should I buy or sell {stock_name}? 
Please provide a detailed stock recommendation that includes:
1. Valuation status (undervalued or overvalued),
2. A clear BUY or SELL action (no ambiguity),
3. A confidence score from 0 to 100 based on technicals, fundamentals, and market conditions,
4. Brief industry or company-level context that justifies your position."""
app = wrkflw.compile()
res = app.invoke({
    "messages": [HumanMessage(content=query)]
})

print(res['messages'][-1].content)
print(fundamentals_analyst.name)
print(technicals_analyst.name)