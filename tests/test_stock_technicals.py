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
    mock_tick.return_value = mock_ins
    mock_clean_data.return_value = mock_df

    res = stock_price_technicals("RVNL.NS")

    assert isinstance(res, pd.DataFrame)
    assert 'Revenue' in res.columns
    mock_clean_data.assert_called_once_with(mock_df)


@patch('tools.stock_technical_data.log')
@patch('tools.stock_technical_data.yf.Ticker')
def test_stock_price_technicals_log(mock_tick, mock_log):
    mock_ins = MagicMock()
    mock_ins.quarterly_financials = pd.DataFrame()
    mock_tick.return_value = mock_ins

    res = stock_price_technicals("RVNL.NS")
    assert res is None
    mock_log.logger.warning.assert_called_once()


@patch('tools.stock_technical_data.log')
@patch('tools.stock_technical_data.yf.Ticker')
def test_stock_price_technicals_except(mock_tick, mock_log):
    mock_ins = MagicMock()
    type(mock_ins).quarterly_financials = property(lambda _: (_ for _ in ()).throw(Exception("API Error !!")))
    mock_tick.return_value = mock_ins

    with pytest.raises(Exception, match="API Error"):
        stock_price_technicals("RVNL.NS")

    mock_log.logger.exception.assert_called_once()
