import pytest
from unittest.mock import MagicMock, patch
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from tools.stock_data_fetcher import stock_price_fetcher

"""
The test file actually tested the tools/stock_data_fetcher which takes 
Args:
    - symbol: Company's ticker symbol

Returns:
    - Current Price: Price trading at the moment
    - PE Ratio : Indicator for Valuation
    - Industry : which area the company works
    - Desc : Company Summary
"""
@pytest.fixture
def mock_tick_data():
    return {'info': {
            'regularMarketPrice': 150.0,
            'trailingPE': 20.5,
            'industry': 'Technology',
            'longBusinessSummary': 'A tech company that makes cool stuff.'
        },
        'fast_info': {
            'last_price': 152.5
        }
    }

# Test Case 1: Full Success
@patch('tools.stock_data_fetcher.yf.Ticker')
def test_stock_data(mock_ticker, mock_tick_data):
    mock_ins = MagicMock()
    mock_ins.info = mock_tick_data['info']
    mock_ins.fast_info = mock_tick_data['fast_info']
    mock_ticker.return_value = mock_ins

    res = stock_price_fetcher("RVNL.NS")
    assert res['current_price'] == 152.50
    assert res["pe_ratio"] == 20.5
    assert res["industry"] == "Technology"
    assert res["desc"] == "A tech company that makes cool stuff."

# Test Case 2: Missing Price
@patch('tools.stock_data_fetcher.yf.Ticker')
def test_stock_data_missing_price(mock_ticker):
    mock_ins = MagicMock()
    mock_ins.info = {
        'trailingPE': 15.0,
        'industry': 'Finance',
        'longBusinessSummary': 'A finance company.'
    }

    mock_ins.fast_info = {}
    mock_ticker.return_value = mock_ins

    res = stock_price_fetcher("XYZ")

    assert res["current_price"] is None
    assert res["pe_ratio"] == 15.0
    assert res["industry"] == "Finance"
    assert res["desc"] == "A finance company."


# Test Case 3: Ticker Fails

@patch('tools.stock_data_fetcher.yf.Ticker')
def test_stock_data_fails(mock_ticker):
    mock_ticker.side_effect = Exception("Data Source not found !!")
    with pytest.raises(Exception) as e :
        stock_price_fetcher("ERROR")

    assert "Data Source not found !" in str(e.value)


