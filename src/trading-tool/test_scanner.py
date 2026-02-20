import pytest
from unittest.mock import patch, MagicMock
from typing import Dict, Any, Generator, List, Optional
from datetime import datetime, timedelta
from tao_bounce_scanner import run_tao_of_trading_scan
from storage import ScannerConfig

@pytest.fixture
def mock_get_scanner_data() -> Generator[MagicMock, None, None]:
    """
    Mocks the TradingView Query.get_scanner_data method to return controlled test data.
    Why: To isolate the scanner logic from the external TradingView API, ensuring deterministic tests.
    """
    with patch("tradingview_screener.Query.get_scanner_data") as mock_get_data:
        yield mock_get_data

def get_default_stock_data() -> Dict[str, Any]:
    """
    Returns a dictionary representing a stock that meets ALL Bounce 2.0 criteria.
    Why: specific tests can modify just one attribute to verify individual filter logic.
    """
    # Set default earnings date to far future (safe)
    safe_earnings_date = (datetime.now() + timedelta(days=100)).timestamp()
    
    return {
        "name": "GOOD_STOCK",
        "close": 700.0,
        "SMA200": 600.0,
        "ADX": 25.0,
        "EMA8": 680.0,
        "EMA21": 670.0,
        "EMA34": 660.0,
        "EMA55": 650.0,
        "EMA89": 640.0,
        "Stoch.K": 30.0,
        "ATR": 30.0,
        "relative_volume_10d_calc": 1.5,
        "RSI2": 15.0,         # Bullish Trigger: Curr > 10
        "RSI2[1]": 5.0,       # Bullish Trigger: Prev <= 10
        "earnings_release_next_date": safe_earnings_date
    }

def Should_FilterStock_When_ADXIsBelowThreshold(mock_get_scanner_data: MagicMock) -> None:
    """
    Verifies that stocks with ADX < 20 are filtered out.
    Why: ADX < 20 indicates a weak trend. Bounce 2.0 requires a strong trend.
    """
    stock_data = get_default_stock_data()
    stock_data["ADX"] = 19.0
    mock_data = [None, [stock_data]]
    mock_get_scanner_data.return_value = mock_data

    with patch("tao_bounce_scanner.get_writer") as mock_get_writer:
        mock_writer = MagicMock()
        mock_get_writer.return_value = mock_writer
        run_tao_of_trading_scan(ScannerConfig(output_type="log"))
        mock_writer.write.assert_not_called()

def Should_NotFilterStock_When_ADXIsAboveThreshold(mock_get_scanner_data: MagicMock) -> None:
    """
    Verifies that stocks with ADX >= 20 are retained.
    Why: Ensures valid candidates are not accidentally removed by the ADX filter.
    """
    stock_data = get_default_stock_data()
    stock_data["ADX"] = 20.0
    mock_data = [None, [stock_data]]
    mock_get_scanner_data.return_value = mock_data

    with patch("tao_bounce_scanner.get_writer") as mock_get_writer:
        mock_writer = MagicMock()
        mock_get_writer.return_value = mock_writer
        run_tao_of_trading_scan(ScannerConfig(output_type="log"))
        mock_writer.write.assert_called_once()

def Should_FilterStock_When_CloseIsBelowSMA200(mock_get_scanner_data: MagicMock) -> None:
    """
    Verifies that stocks trading below the 200 SMA are filtered out.
    Why: We only trade in the direction of the long-term trend (Bullish).
    """
    stock_data = get_default_stock_data()
    stock_data["SMA200"] = 750.0
    mock_data = [None, [stock_data]]
    mock_get_scanner_data.return_value = mock_data

    with patch("tao_bounce_scanner.get_writer") as mock_get_writer:
        mock_writer = MagicMock()
        mock_get_writer.return_value = mock_writer
        run_tao_of_trading_scan(ScannerConfig(output_type="log"))
        mock_writer.write.assert_not_called()

def Should_NotFilterStock_When_CloseIsAboveSMA200(mock_get_scanner_data: MagicMock) -> None:
    """
    Verifies that stocks trading above the 200 SMA are retained.
    Why: Confirms we are selecting stocks in a long-term uptrend.
    """
    stock_data = get_default_stock_data()
    mock_data = [None, [stock_data]]
    mock_get_scanner_data.return_value = mock_data

    with patch("tao_bounce_scanner.get_writer") as mock_get_writer:
        mock_writer = MagicMock()
        mock_get_writer.return_value = mock_writer
        run_tao_of_trading_scan(ScannerConfig(output_type="log"))
        mock_writer.write.assert_called_once()

def Should_FilterStock_When_EMAsAreNotBullishlyStacked(mock_get_scanner_data: MagicMock) -> None:
    """
    Verifies that stocks are filtered if EMAs are not in valid order (8 > 21 > 34 > 55 > 89).
    Why: EMA stacking confirms the consistency of the trend momentum.
    """
    stock_data = get_default_stock_data()
    stock_data["EMA8"] = 660.0 # Below EMA21 (670)
    mock_data = [None, [stock_data]]
    mock_get_scanner_data.return_value = mock_data

    with patch("tao_bounce_scanner.get_writer") as mock_get_writer:
        mock_writer = MagicMock()
        mock_get_writer.return_value = mock_writer
        run_tao_of_trading_scan(ScannerConfig(output_type="log"))
        mock_writer.write.assert_not_called()

def Should_NotFilterStock_When_EMAsAreBullishlyStacked(mock_get_scanner_data: MagicMock) -> None:
    """
    Verifies that stocks with properly stacked EMAs are retained.
    Why: Validates the core trend definition of the strategy.
    """
    stock_data = get_default_stock_data()
    mock_data = [None, [stock_data]]
    mock_get_scanner_data.return_value = mock_data

    with patch("tao_bounce_scanner.get_writer") as mock_get_writer:
        mock_writer = MagicMock()
        mock_get_writer.return_value = mock_writer
        run_tao_of_trading_scan(ScannerConfig(output_type="log"))
        mock_writer.write.assert_called_once()

def Should_FilterStock_When_StochKIsAboveThreshold(mock_get_scanner_data: MagicMock) -> None:
    """
    Verifies that stocks with Stoch.K > 40 are filtered out.
    Why: We need a pullback. High Stochastics imply price is not sufficiently pulled back.
    """
    stock_data = get_default_stock_data()
    stock_data["Stoch.K"] = 41.0
    mock_data = [None, [stock_data]]
    mock_get_scanner_data.return_value = mock_data

    with patch("tao_bounce_scanner.get_writer") as mock_get_writer:
        mock_writer = MagicMock()
        mock_get_writer.return_value = mock_writer
        run_tao_of_trading_scan(ScannerConfig(output_type="log"))
        mock_writer.write.assert_not_called()

def Should_NotFilterStock_When_StochKIsBelowThreshold(mock_get_scanner_data: MagicMock) -> None:
    """
    Verifies that stocks with Stoch.K <= 40 are retained.
    Why: Identifies stocks that are oversold/pulled back within the uptrend.
    """
    stock_data = get_default_stock_data()
    stock_data["Stoch.K"] = 40.0
    mock_data = [None, [stock_data]]
    mock_get_scanner_data.return_value = mock_data

    with patch("tao_bounce_scanner.get_writer") as mock_get_writer:
        mock_writer = MagicMock()
        mock_get_writer.return_value = mock_writer
        run_tao_of_trading_scan(ScannerConfig(output_type="log"))
        mock_writer.write.assert_called_once()

def Should_FilterStock_When_PriceIsNotInActionZone(mock_get_scanner_data: MagicMock) -> None:
    """
    Verifies that stocks are filtered if price is too far from EMA21 (> 1 ATR).
    Why: The 'Action Zone' ensures we enter near the mean (EMA21), managing risk.
    """
    stock_data = get_default_stock_data()
    # EMA21 is 670. ATR is 30. Action Zone is [640, 700].
    # Close 700 is barely in.
    # Set ATR to 29. 700 - 670 = 30. 30 > 29. Filtered.
    stock_data["ATR"] = 29.0
    mock_data = [None, [stock_data]]
    mock_get_scanner_data.return_value = mock_data

    with patch("tao_bounce_scanner.get_writer") as mock_get_writer:
        mock_writer = MagicMock()
        mock_get_writer.return_value = mock_writer
        run_tao_of_trading_scan(ScannerConfig(output_type="log"))
        mock_writer.write.assert_not_called()

def Should_NotFilterStock_When_PriceIsInActionZone(mock_get_scanner_data: MagicMock) -> None:
    """
    Verifies that stocks within 1 ATR of EMA21 are retained.
    Why: Confirms entry location is within acceptable risk parameters.
    """
    stock_data = get_default_stock_data()
    stock_data["ATR"] = 30.0
    mock_data = [None, [stock_data]]
    mock_get_scanner_data.return_value = mock_data

    with patch("tao_bounce_scanner.get_writer") as mock_get_writer:
        mock_writer = MagicMock()
        mock_get_writer.return_value = mock_writer
        run_tao_of_trading_scan(ScannerConfig(output_type="log"))
        mock_writer.write.assert_called_once()

# --- Tests for Bounce 2.0 (Earnings & RSI) ---

def Should_FilterStock_When_EarningsAreWithinBuffer(mock_get_scanner_data: MagicMock) -> None:
    """
    Verifies that stocks with earnings within 14 days are filtered.
    Why: Earnings releases cause high volatility (gap risk). We avoid holding through them.
    """
    stock_data = get_default_stock_data()
    # Set earnings date to 5 days from now
    stock_data["earnings_release_next_date"] = (datetime.now() + timedelta(days=5)).timestamp()
    
    mock_data = [None, [stock_data]]
    mock_get_scanner_data.return_value = mock_data

    with patch("tao_bounce_scanner.get_writer") as mock_get_writer:
        mock_writer = MagicMock()
        mock_get_writer.return_value = mock_writer
        run_tao_of_trading_scan(ScannerConfig(output_type="log"))
        mock_writer.write.assert_not_called()

def Should_NotFilterStock_When_EarningsAreSafe(mock_get_scanner_data: MagicMock) -> None:
    """
    Verifies that stocks with earnings > 14 days away are retained.
    Why: Ensures we can trade the setup without immediate earnings risk.
    """
    stock_data = get_default_stock_data()
    # Set earnings date to 20 days from now (safe)
    stock_data["earnings_release_next_date"] = (datetime.now() + timedelta(days=20)).timestamp()
    
    mock_data = [None, [stock_data]]
    mock_get_scanner_data.return_value = mock_data

    with patch("tao_bounce_scanner.get_writer") as mock_get_writer:
        mock_writer = MagicMock()
        mock_get_writer.return_value = mock_writer
        run_tao_of_trading_scan(ScannerConfig(output_type="log"))
        mock_writer.write.assert_called_once()

def Should_FilterStock_When_RSI2_HasNotTriggered(mock_get_scanner_data: MagicMock) -> None:
    """
    Verifies that stocks are filtered if RSI(2) hasn't crossed UP above 10.
    Case: Both yesterday and today are below 10.
    Why: We need the MOMENT of reversal (crossing 10), not just oversold condition.
    """
    stock_data = get_default_stock_data()
    # Case 1: Both below 10 (Oversold but not crossing up yet)
    stock_data["RSI2[1]"] = 5.0
    stock_data["RSI2"] = 8.0
    
    mock_data = [None, [stock_data]]
    mock_get_scanner_data.return_value = mock_data

    with patch("tao_bounce_scanner.get_writer") as mock_get_writer:
        mock_writer = MagicMock()
        mock_get_writer.return_value = mock_writer
        run_tao_of_trading_scan(ScannerConfig(output_type="log"))
        mock_writer.write.assert_not_called()

def Should_FilterStock_When_RSI2_AlreadyTriggered(mock_get_scanner_data: MagicMock) -> None:
    """
    Verifies that stocks are filtered if RSI(2) was already above 10 yesterday.
    Case: Both yesterday and today are above 10.
    Why: We missed the entry signal. Chasing is not allowed.
    """
    stock_data = get_default_stock_data()
    # Case 2: Both above 10 (Triggered yesterday or before)
    stock_data["RSI2[1]"] = 12.0
    stock_data["RSI2"] = 15.0
    
    mock_data = [None, [stock_data]]
    mock_get_scanner_data.return_value = mock_data

    with patch("tao_bounce_scanner.get_writer") as mock_get_writer:
        mock_writer = MagicMock()
        mock_get_writer.return_value = mock_writer
        run_tao_of_trading_scan(ScannerConfig(output_type="log"))
        mock_writer.write.assert_not_called()

def Should_NotFilterStock_When_RSI2_triggers(mock_get_scanner_data: MagicMock) -> None:
    """
    Verifies that stocks are retained exactly when RSI(2) crosses from <= 10 to > 10.
    Why: This is the precise 'Buy' signal for the Bounce 2.0 strategy.
    """
    stock_data = get_default_stock_data()
    # Valid Trigger: Prev <= 10, Curr > 10
    stock_data["RSI2[1]"] = 9.0
    stock_data["RSI2"] = 11.0
    
    mock_data = [None, [stock_data]]
    mock_get_scanner_data.return_value = mock_data

    with patch("tao_bounce_scanner.get_writer") as mock_get_writer:
        mock_writer = MagicMock()
        mock_get_writer.return_value = mock_writer
        run_tao_of_trading_scan(ScannerConfig(output_type="log"))
        mock_writer.write.assert_called_once()
