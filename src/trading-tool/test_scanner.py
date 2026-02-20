import pandas as pd
import pytest
from typing import Dict, Any, Generator
from unittest.mock import patch, MagicMock
from tao_bounce_scanner import run_tao_of_trading_scan, ScannerConfig

@pytest.fixture
def mock_get_scanner_data() -> Generator[MagicMock, None, None]:
    with patch("tradingview_screener.Query.get_scanner_data") as mock_get_data:
        yield mock_get_data

def get_default_stock_data() -> Dict[str, Any]:
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
        "relative_volume_10d_calc": 1.5
    }

def Should_FilterStock_When_ADXIsBelowThreshold(mock_get_scanner_data: MagicMock) -> None:
    stock_data = get_default_stock_data()
    stock_data["ADX"] = 19
    mock_data = [None, [stock_data]]
    mock_get_scanner_data.return_value = mock_data

    with patch("tao_bounce_scanner.get_writer") as mock_get_writer:
        mock_writer = MagicMock()
        mock_get_writer.return_value = mock_writer

        config = ScannerConfig(output_type="log")
        run_tao_of_trading_scan(config)

        mock_writer.write.assert_not_called()

def Should_NotFilterStock_When_ADXIsAboveThreshold(mock_get_scanner_data: MagicMock) -> None:
    stock_data = get_default_stock_data()
    stock_data["ADX"] = 20 # ADX is exactly 20
    mock_data = [None, [stock_data]]
    mock_get_scanner_data.return_value = mock_data

    with patch("tao_bounce_scanner.get_writer") as mock_get_writer:
        mock_writer = MagicMock()
        mock_get_writer.return_value = mock_writer

        config = ScannerConfig(output_type="log")
        run_tao_of_trading_scan(config)

        mock_writer.write.assert_called_once()
        df = mock_writer.write.call_args[0][0]
        assert len(df) == 1
        assert df.iloc[0]["name"] == "GOOD_STOCK"

def Should_FilterStock_When_CloseIsBelowSMA200(mock_get_scanner_data: MagicMock) -> None:
    stock_data = get_default_stock_data()
    stock_data["SMA200"] = 750
    mock_data = [None, [stock_data]]
    mock_get_scanner_data.return_value = mock_data

    with patch("tao_bounce_scanner.get_writer") as mock_get_writer:
        mock_writer = MagicMock()
        mock_get_writer.return_value = mock_writer

        config = ScannerConfig(output_type="log")
        run_tao_of_trading_scan(config)

        mock_writer.write.assert_not_called()

def Should_NotFilterStock_When_CloseIsAboveSMA200(mock_get_scanner_data: MagicMock) -> None:
    stock_data = get_default_stock_data()
    stock_data["close"] = 700
    stock_data["SMA200"] = 600 # Close is above SMA200
    mock_data = [None, [stock_data]]
    mock_get_scanner_data.return_value = mock_data

    with patch("tao_bounce_scanner.get_writer") as mock_get_writer:
        mock_writer = MagicMock()
        mock_get_writer.return_value = mock_writer

        config = ScannerConfig(output_type="log")
        run_tao_of_trading_scan(config)

        mock_writer.write.assert_called_once()
        df = mock_writer.write.call_args[0][0]
        assert len(df) == 1
        assert df.iloc[0]["name"] == "GOOD_STOCK"

def Should_FilterStock_When_EMAsAreNotBullishlyStacked(mock_get_scanner_data: MagicMock) -> None:
    stock_data = get_default_stock_data()
    stock_data["EMA8"] = 660
    mock_data = [None, [stock_data]]
    mock_get_scanner_data.return_value = mock_data

    with patch("tao_bounce_scanner.get_writer") as mock_get_writer:
        mock_writer = MagicMock()
        mock_get_writer.return_value = mock_writer

        config = ScannerConfig(output_type="log")
        run_tao_of_trading_scan(config)

        mock_writer.write.assert_not_called()

def Should_NotFilterStock_When_EMAsAreBullishlyStacked(mock_get_scanner_data: MagicMock) -> None:
    stock_data = get_default_stock_data()
    # EMAs are bullishly stacked by default
    mock_data = [None, [stock_data]]
    mock_get_scanner_data.return_value = mock_data

    with patch("tao_bounce_scanner.get_writer") as mock_get_writer:
        mock_writer = MagicMock()
        mock_get_writer.return_value = mock_writer

        config = ScannerConfig(output_type="log")
        run_tao_of_trading_scan(config)

        mock_writer.write.assert_called_once()
        df = mock_writer.write.call_args[0][0]
        assert len(df) == 1
        assert df.iloc[0]["name"] == "GOOD_STOCK"

def Should_FilterStock_When_StochKIsAboveThreshold(mock_get_scanner_data: MagicMock) -> None:
    stock_data = get_default_stock_data()
    stock_data["Stoch.K"] = 41
    mock_data = [None, [stock_data]]
    mock_get_scanner_data.return_value = mock_data

    with patch("tao_bounce_scanner.get_writer") as mock_get_writer:
        mock_writer = MagicMock()
        mock_get_writer.return_value = mock_writer

        config = ScannerConfig(output_type="log")
        run_tao_of_trading_scan(config)

        mock_writer.write.assert_not_called()

def Should_NotFilterStock_When_StochKIsBelowThreshold(mock_get_scanner_data: MagicMock) -> None:
    stock_data = get_default_stock_data()
    stock_data["Stoch.K"] = 40 # Stoch.K is exactly 40
    mock_data = [None, [stock_data]]
    mock_get_scanner_data.return_value = mock_data

    with patch("tao_bounce_scanner.get_writer") as mock_get_writer:
        mock_writer = MagicMock()
        mock_get_writer.return_value = mock_writer

        config = ScannerConfig(output_type="log")
        run_tao_of_trading_scan(config)

        mock_writer.write.assert_called_once()
        df = mock_writer.write.call_args[0][0]
        assert len(df) == 1
        assert df.iloc[0]["name"] == "GOOD_STOCK"

def Should_FilterStock_When_PriceIsNotInActionZone(mock_get_scanner_data: MagicMock) -> None:
    stock_data = get_default_stock_data()
    stock_data["ATR"] = 29
    mock_data = [None, [stock_data]]
    mock_get_scanner_data.return_value = mock_data

    with patch("tao_bounce_scanner.get_writer") as mock_get_writer:
        mock_writer = MagicMock()
        mock_get_writer.return_value = mock_writer

        config = ScannerConfig(output_type="log")
        run_tao_of_trading_scan(config)

        mock_writer.write.assert_not_called()

def Should_NotFilterStock_When_PriceIsInActionZone(mock_get_scanner_data: MagicMock) -> None:
    stock_data = get_default_stock_data()
    stock_data["ATR"] = 30 # dist_from_mean is 30, so this is exactly in the action zone
    mock_data = [None, [stock_data]]
    mock_get_scanner_data.return_value = mock_data

    with patch("tao_bounce_scanner.get_writer") as mock_get_writer:
        mock_writer = MagicMock()
        mock_get_writer.return_value = mock_writer

        config = ScannerConfig(output_type="log")
        run_tao_of_trading_scan(config)

        mock_writer.write.assert_called_once()
        df = mock_writer.write.call_args[0][0]
        assert len(df) == 1
        assert df.iloc[0]["name"] == "GOOD_STOCK"
