import pandas as pd
import pytest
from unittest.mock import MagicMock, patch
from tools.stock_hist_data import stock_hist_data

@patch('tools.stock_hist_data.clean_data_history')
@patch('tools.stock_hist_data.calculate_rsi')
@patch('tools.stock_hist_data.yf.Ticker')
def test_stock_hist_data(mock_tick, mock_cal_rsi, mock_clean_data):
    mock_df = pd.DataFrame(
        {
            'Close':[20,30,35,22,19],
            'Open': [56,18,20,25,17]
        }
    )
    mock_ins = MagicMock()
    mock_ins.history.return_value = mock_df
    mock_tick.return_value = mock_ins

    mock_cal_rsi.return_value = [30, 40, 50, 60, 70]
    mock_clean_data.return_value = mock_df

    res = stock_hist_data("RVNL.NS")

    assert isinstance(res, pd.DataFrame)
    assert 'EMA_10' in res.columns
    assert 'RSI_14' in res.columns
    mock_ins.history.assert_called_once_with(period="6mo")
    mock_cal_rsi.assert_called_once()
    mock_clean_data.assert_called_once()