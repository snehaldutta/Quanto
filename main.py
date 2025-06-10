import yfinance as yf
from ollama import chat
from typing import Dict, Callable
import pandas as pd
from test import fetch_stock_ticker
from technicals import calculate_rsi
import json

# System Prompt
sys_prompt: str = """ 
Your name is Harshad Mehta. You're a Bombay Stock Exchange (BSE) trader. You have been trading in BSE for 20 years. You have seen the 2008 market crash,
2016 market crash and 2020 market crash. You have been following the economic trends of India for the 2 years. From your experience of market crashes, research of the Indian Economy
and using the given tools:
    - stock_price_fetcher → fetches current stock price and P/E ratio.
    - stock_price_analyzer → fetches 6-months historical data with RSI data for every 14 days. 10 - days exponential moving averages (EMA) can be caculated.
    - stock_price_technicals → fetches the quarterly financial results of the company
Do both fundamental and technical analysis of the stock and try to be more precise using the above tools.
Analyze the stock and return:
1. Is the stock undervalued or overvalued?
2. Should the user buy or sell the stock now? (No ambigious response. Be clear !!)
3. Confidence score of your analysis (out of 100). 
## Follow the PARAMS strictly

PARAMS:
    - TEMPERATURE : 0.3 (Be deterministic)
"""
def fetch_symbol(script_name:str)->str:
    if "." in script_name:
        tick_symbol = script_name
    else:
        tick_symbol = fetch_stock_ticker(script_name)

    if tick_symbol is None:
        raise ValueError(f"Could not find the ticker symbol for {script_name}")
    
    return tick_symbol

# tool --> fetches the current stock price
def stock_price_fetcher(symbol: str) -> str:
    tick = yf.Ticker(symbol)
    price_attrs : list = ['regularMarketPrice', 'currentPrice', 'price']

    try:
        result : dict = {
            'current_price':None,
            'pe_ratio': None
        }
        for attr in price_attrs:
            if result['current_price'] is None and attr in tick.info and tick.info[attr] is not None:
                result['current_price'] = tick.info[attr]
            
        current_price = tick.fast_info.get('last_price')
        if current_price is not None:
            result['current_price'] = current_price
        
        if 'trailingPE' in tick.info and tick.info['trailingPE'] is not None:
            result['pe_ratio'] = tick.info['trailingPE']

        if result['current_price'] is None:
            raise Exception(f'Price not found for {symbol}')
        
        return result
    
    except Exception as e:
        raise Exception(f"Error fetching data for '{symbol}': {e}")

# tool --> fetches the historical data
def stock_price_analyzer(symbol: str, period:str ='6mo')-> pd.DataFrame:
    tick = yf.Ticker(symbol)

    try:
        hist_data = tick.history(period=period)
        hist_data['EMA_10'] = hist_data['Close'].ewm(span=10,adjust=False).mean()
        hist_data['RSI_14'] = calculate_rsi(hist_data['Close'],14)
        return hist_data
    
    except Exception as e:
        raise Exception(f"Error in fetching the historical data '{symbol}'as {e}")
    

def stock_price_technicals(symbol:str)-> pd.DataFrame:
    tick = yf.Ticker(symbol)
    
    try:
       quarter_results = tick.quarterly_financials
       if quarter_results is None or quarter_results.empty:
            raise ValueError(f"No valid quarterly results found for {symbol}")
       
       else:
           return quarter_results
    except Exception as e:
        raise ValueError(f'Data not found for the symbol {symbol}')
    
# tool configs
stock_price_fetcher_tool = {
    'type': 'function',
    'function': {
        'name': 'stock_price_fetcher',
        'description': 'Get the current stock price **and** P/E ratio for any symbol',
        'parameters': {
            'type': 'object',
            'required': ['symbol'],
            'properties': {
                'symbol': {'type': 'string', 'description': 'The company ticker symbol (e.g., Tata Steel, Hindustan Aeronautics Limited etc.)'},
            },
        },
    },
}
stock_price_analyzer_tool = {
    'type': 'function',
    'function': {
        'name': 'stock_price_analyzer',
        'description': 'Get the historical data and RSI for any symbol',
        'parameters': {
            'type': 'object',
            'required': ['symbol'],
            'properties': {
                'symbol': {'type': 'string', 'description': 'The company ticker symbol (e.g., Tata Steel, Hindustan Aeronautics Limited etc.)'},
            },
        },
    },
}

stock_price_technicals_tool = {
    'type': 'function',
    'function': {
        'name': 'stock_price_technicals',
        'description': 'Get the quarterly financial data for any symbol',
        'parameters': {
            'type': 'object',
            'required': ['symbol'],
            'properties': {
                'symbol': {'type': 'string', 'description': 'The company ticker symbol (e.g., Tata Steel, Hindustan Aeronautics Limited etc.)'},
            },
        },
    },
}

#list of available tools 
available_functions: Dict[str, Callable]= {
    'stock_price_fetcher': stock_price_fetcher,
    'stock_price_analyzer':stock_price_analyzer,
    'stock_price_technicals': stock_price_technicals
}

stock_name: str = input("Name of the comapny : ")
symbol : str = fetch_symbol(stock_name)
prompt : str = f"Here are the financials for {stock_name}. Use **P/E ratio**, revenue, operating income, net income, historical data, RSI and EMA with the current price** to judge whether it's undervalued or overvalued.\n"
"Don't ignore the P/E ratio. Also, give a clear buy/sell signal and a confidence score out of 100."
response = chat(
    model='qwen3:1.7b',
    messages=[
        {'role':'system','content':sys_prompt},
        {'role': 'user', 'content':prompt}
    ],
    tools=[stock_price_fetcher_tool, stock_price_analyzer_tool, stock_price_technicals_tool]
)

tool_output = {}
if response.message.tool_calls:
    for tool in response.message.tool_calls:
        if function_to_call := available_functions.get(tool.function.name):
            print('Calling function:', tool.function.name)
            # print('Arguments:', tool.function.arguments)
            tool_args = tool.function.arguments
            tool_args['symbol'] = symbol
            tool_args.pop('script_name',None)
            print('Arguments:', tool_args)
            res = function_to_call(**tool_args)
        

            def format_tool_response(res):
                """
                Format tool output (DataFrame or dict) into a readable string.
                Cleans NaN values and limits rows for DataFrame output.
                """
                if isinstance(res, pd.DataFrame):
                    # Drop all-NaN columns and rows
                    res_cleaned = res.dropna(axis=1, how='all').dropna(axis=0, how='all')
                    return res_cleaned.tail(20).to_string()
                
                elif isinstance(res, dict):
                    return '\n'.join(f'{k}: {v}' for k, v in res.items())
                
                else:
                    return json.dumps(res, indent=2)
                  
            res_str = format_tool_response(res)
            tool_output[tool.function.name] = res_str

        else:
            print('Function', tool.function.name, 'not found')


tool_output_msgs = [
    {'role': 'tool', 'tool_name': tool.function.name, 'content': tool_output[tool.function.name]}
    for tool in response.message.tool_calls
]
print("=== Tool Calls ===")
print(response.message.tool_calls)
print("=== Tool Outputs ===")
for msg in tool_output_msgs:
    print(msg)
# Final chat with tool results for analysis
final_response = chat(
    model='qwen3:1.7b',
    messages=[
        {'role': 'system', 'content': sys_prompt},
        {'role': 'user', 'content': prompt},
        *tool_output_msgs
    ]
)

print("\n--- Final Recommendation ---")
print(final_response.message.content)