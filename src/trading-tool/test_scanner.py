import pandas as pd
import pytest
from typing import Dict, Any, Generator
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
from tao_bounce_scanner import run_tao_of_trading_scan, ScannerConfig, RSI_BULLISH_CROSS_LEVEL, EARNINGS_BUFFER_DAYS

@pytest.fixture
def mock_get_scanner_data() -> Generator[MagicMock, None, None]:
    with patch("tradingview_screener.Query.get_scanner_data") as mock_get_data:
        yield mock_get_data

def get_default_stock_data() -> Dict[str, Any]:
    # Set default earnings date to far future
    safe_earnings_date = (datetime.now() + timedelta(days=100)).timestamp()
    
    return {
        "name": "GOOD_STOCK",
        "close": 700,
        "SMA200": 600,
        "ADX": 25,
        "EMA8": 680,
        "EMA21": 670,
        "EMA34": 660,
        "EMA55": 650,
        "EMA89": 640,
        "Stoch.K": 30,
        "ATR": 30,
        "relative_volume_10d_calc": 1.5,
        "RSI2": 15,         # Bullish Trigger: Curr > 10
        "RSI2[1]": 5,       # Bullish Trigger: Prev <= 10
        "earnings_release_next_date": safe_earnings_date
    }

# ... (Existing tests: Should_FilterStock_When_ADXIsBelowThreshold, etc.) ...
# I will keep them but I need to make sure they still pass with new fields.
# Since I updated `get_default_stock_data`, they should have the new fields and pass if logic is correct.
# Wait, I am replacing the whole file content or specific part?
# The user wants me to ADD tests.
# I will rewrite the file to include all tests including new ones.

def Should_FilterStock_When_ADXIsBelowThreshold(mock_get_scanner_data: MagicMock) -> None:
    stock_data = get_default_stock_data()
    stock_data["ADX"] = 19
    mock_data = [None, [stock_data]]
    mock_get_scanner_data.return_value = mock_data

    with patch("tao_bounce_scanner.get_writer") as mock_get_writer:
        mock_writer = MagicMock()
        mock_get_writer.return_value = mock_writer
        run_tao_of_trading_scan(ScannerConfig(output_type="log"))
        mock_writer.write.assert_not_called()

def Should_NotFilterStock_When_ADXIsAboveThreshold(mock_get_scanner_data: MagicMock) -> None:
    stock_data = get_default_stock_data()
    stock_data["ADX"] = 20
    mock_data = [None, [stock_data]]
    mock_get_scanner_data.return_value = mock_data

    with patch("tao_bounce_scanner.get_writer") as mock_get_writer:
        mock_writer = MagicMock()
        mock_get_writer.return_value = mock_writer
        run_tao_of_trading_scan(ScannerConfig(output_type="log"))
        mock_writer.write.assert_called_once()

def Should_FilterStock_When_CloseIsBelowSMA200(mock_get_scanner_data: MagicMock) -> None:
    stock_data = get_default_stock_data()
    stock_data["SMA200"] = 750
    mock_data = [None, [stock_data]]
    mock_get_scanner_data.return_value = mock_data

    with patch("tao_bounce_scanner.get_writer") as mock_get_writer:
        mock_writer = MagicMock()
        mock_get_writer.return_value = mock_writer
        run_tao_of_trading_scan(ScannerConfig(output_type="log"))
        mock_writer.write.assert_not_called()

def Should_NotFilterStock_When_CloseIsAboveSMA200(mock_get_scanner_data: MagicMock) -> None:
    stock_data = get_default_stock_data()
    mock_data = [None, [stock_data]]
    mock_get_scanner_data.return_value = mock_data

    with patch("tao_bounce_scanner.get_writer") as mock_get_writer:
        mock_writer = MagicMock()
        mock_get_writer.return_value = mock_writer
        run_tao_of_trading_scan(ScannerConfig(output_type="log"))
        mock_writer.write.assert_called_once()

def Should_FilterStock_When_EMAsAreNotBullishlyStacked(mock_get_scanner_data: MagicMock) -> None:
    stock_data = get_default_stock_data()
    stock_data["EMA8"] = 660
    mock_data = [None, [stock_data]]
    mock_get_scanner_data.return_value = mock_data

    with patch("tao_bounce_scanner.get_writer") as mock_get_writer:
        mock_writer = MagicMock()
        mock_get_writer.return_value = mock_writer
        run_tao_of_trading_scan(ScannerConfig(output_type="log"))
        mock_writer.write.assert_not_called()

def Should_NotFilterStock_When_EMAsAreBullishlyStacked(mock_get_scanner_data: MagicMock) -> None:
    stock_data = get_default_stock_data()
    mock_data = [None, [stock_data]]
    mock_get_scanner_data.return_value = mock_data

    with patch("tao_bounce_scanner.get_writer") as mock_get_writer:
        mock_writer = MagicMock()
        mock_get_writer.return_value = mock_writer
        run_tao_of_trading_scan(ScannerConfig(output_type="log"))
        mock_writer.write.assert_called_once()

def Should_FilterStock_When_StochKIsAboveThreshold(mock_get_scanner_data: MagicMock) -> None:
    stock_data = get_default_stock_data()
    stock_data["Stoch.K"] = 41
    mock_data = [None, [stock_data]]
    mock_get_scanner_data.return_value = mock_data

    with patch("tao_bounce_scanner.get_writer") as mock_get_writer:
        mock_writer = MagicMock()
        mock_get_writer.return_value = mock_writer
        run_tao_of_trading_scan(ScannerConfig(output_type="log"))
        mock_writer.write.assert_not_called()

def Should_NotFilterStock_When_StochKIsBelowThreshold(mock_get_scanner_data: MagicMock) -> None:
    stock_data = get_default_stock_data()
    stock_data["Stoch.K"] = 40
    mock_data = [None, [stock_data]]
    mock_get_scanner_data.return_value = mock_data

    with patch("tao_bounce_scanner.get_writer") as mock_get_writer:
        mock_writer = MagicMock()
        mock_get_writer.return_value = mock_writer
        run_tao_of_trading_scan(ScannerConfig(output_type="log"))
        mock_writer.write.assert_called_once()

def Should_FilterStock_When_PriceIsNotInActionZone(mock_get_scanner_data: MagicMock) -> None:
    stock_data = get_default_stock_data()
    stock_data["ATR"] = 29
    mock_data = [None, [stock_data]]
    mock_get_scanner_data.return_value = mock_data

    with patch("tao_bounce_scanner.get_writer") as mock_get_writer:
        mock_writer = MagicMock()
        mock_get_writer.return_value = mock_writer
        run_tao_of_trading_scan(ScannerConfig(output_type="log"))
        mock_writer.write.assert_not_called()

def Should_NotFilterStock_When_PriceIsInActionZone(mock_get_scanner_data: MagicMock) -> None:
    stock_data = get_default_stock_data()
    stock_data["ATR"] = 30
    mock_data = [None, [stock_data]]
    mock_get_scanner_data.return_value = mock_data

    with patch("tao_bounce_scanner.get_writer") as mock_get_writer:
        mock_writer = MagicMock()
        mock_get_writer.return_value = mock_writer
        run_tao_of_trading_scan(ScannerConfig(output_type="log"))
        mock_writer.write.assert_called_once()

# --- New Tests for Bounce 2.0 (Earnings & RSI) ---

def Should_FilterStock_When_EarningsAreWithinBuffer(mock_get_scanner_data: MagicMock) -> None:
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
    stock_data = get_default_stock_data()
    # Case 1: Both below 10 (Oversold but not crossing up yet)
    stock_data["RSI2[1]"] = 5
    stock_data["RSI2"] = 8 
    
    mock_data = [None, [stock_data]]
    mock_get_scanner_data.return_value = mock_data

    with patch("tao_bounce_scanner.get_writer") as mock_get_writer:
        mock_writer = MagicMock()
        mock_get_writer.return_value = mock_writer
        run_tao_of_trading_scan(ScannerConfig(output_type="log"))
        mock_writer.write.assert_not_called()

def Should_FilterStock_When_RSI2_AlreadyTriggered(mock_get_scanner_data: MagicMock) -> None:
    stock_data = get_default_stock_data()
    # Case 2: Both above 10 (Triggered yesterday or before)
    stock_data["RSI2[1]"] = 12
    stock_data["RSI2"] = 15
    
    mock_data = [None, [stock_data]]
    mock_get_scanner_data.return_value = mock_data

    with patch("tao_bounce_scanner.get_writer") as mock_get_writer:
        mock_writer = MagicMock()
        mock_get_writer.return_value = mock_writer
        run_tao_of_trading_scan(ScannerConfig(output_type="log"))
        mock_writer.write.assert_not_called()

def Should_NotFilterStock_When_RSI2_triggers(mock_get_scanner_data: MagicMock) -> None:
    stock_data = get_default_stock_data()
    # Valid Trigger: Prev <= 10, Curr > 10
    stock_data["RSI2[1]"] = 9
    stock_data["RSI2"] = 11
    
    mock_data = [None, [stock_data]]
    mock_get_scanner_data.return_value = mock_data

    with patch("tao_bounce_scanner.get_writer") as mock_get_writer:
        mock_writer = MagicMock()
        mock_get_writer.return_value = mock_writer
        run_tao_of_trading_scan(ScannerConfig(output_type="log"))
        mock_writer.write.assert_called_once()
