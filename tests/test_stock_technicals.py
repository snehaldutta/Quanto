import pandas as pd
from tools.stock_technical_data import stock_price_technicals
import pytest
from unittest.mock import MagicMock, patch

@patch('tools.stock_technical_data.clean_data_quarterly')
@patch('tools.stock_technical_data.yf.Ticker')
def test_stock_price_technicals(mock_tick, mock_clean_data):
    mock_df = pd.DataFrame(
        {
            'Revenue': [100, 200],
             'Profit': [20, 50]
        }
    )

    mock_ins = MagicMock()
    mock_ins.quarterly_financials = mock_df
    mock_tick.return_value = mock_df

    