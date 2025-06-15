import requests
import time 
import log
def fetch_stock_ticker(company_name: str) -> str:
    if "." in company_name:
        return company_name
    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/115.0.0.0 Safari/537.36'
    }
    url = f"https://query2.finance.yahoo.com/v1/finance/search?q={company_name}"
    response = requests.get(url, headers=headers)
    log.logger.info(f"Response status: {response.status_code}")
    if response.status_code == 429:
        print("Rate limit hit. Retrying after 60 seconds...")
        time.sleep(60)
        response = requests.get(url, headers=headers)
        log.logger.info(f"Response status: {response.status_code}")

    if response.status_code != 200:
        log.logger.warning("Company not found !!")
    data = response.json()
    quotes = data.get("quotes",[])
    for quote in quotes:
        if quote.get('longname', '').strip().lower() == company_name.strip().lower() and quote.get("symbol", "").endswith('.NS'):
            return quote['symbol']
        
        if quote.get('longname', '').strip().lower() == company_name.strip().lower() and quote.get("symbol", "").endswith('.BO'):
            return quote['symbol']
        
    # 3. Fallback to any .NS ticker
    for quote in quotes:
        if quote.get("symbol", "").endswith(".NS"):
            return quote["symbol"]
    # 4. Final fallback
    if quotes:
        return quotes[0]["symbol"]
    
    if not quotes:
        return None
