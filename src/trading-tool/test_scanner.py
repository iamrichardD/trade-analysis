import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
from typing import Dict, Any, Generator, List, Optional
from datetime import datetime, timedelta
from tao_bounce_scanner import run_tao_of_trading_scan, TaoBounceScanner, ADX_COL, STOCH_K_COL
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
    Returns a dictionary representing a stock that meets ALL Bullish Bounce 2.0 criteria.
    Why: specific tests can modify just one attribute to verify individual filter logic.
    """
    # Set default earnings date to far future (safe)
    safe_earnings_date = (datetime.now() + timedelta(days=100)).timestamp()
    
    return {
        "name": "GOOD_STOCK_LONG",
        "close": 700.0,
        "SMA50": 650.0,
        "SMA100": 620.0,
        "SMA200": 600.0,
        ADX_COL: 25.0,
        "EMA8": 680.0,
        "EMA21": 670.0,
        "EMA34": 660.0,
        "EMA55": 650.0,
        "EMA89": 640.0,
        STOCH_K_COL: 30.0,
        "ATR": 30.0,
        "relative_volume_10d_calc": 1.5,
        "change": 1.2,
        "RSI2": 15.0,         # Bullish Trigger: Curr > 10
        "RSI2[1]": 5.0,       # Bullish Trigger: Prev <= 10
        "earnings_release_next_date": safe_earnings_date
    }

def get_bearish_stock_data() -> Dict[str, Any]:
    """
    Returns a dictionary representing a stock that meets ALL Bearish Bounce 2.0 criteria.
    Why: specific tests can modify just one attribute to verify individual short filter logic.
    """
    # Set default earnings date to far future (safe)
    safe_earnings_date = (datetime.now() + timedelta(days=100)).timestamp()
    
    return {
        "name": "GOOD_STOCK_SHORT",
        "close": 500.0,
        "SMA50": 550.0,
        "SMA100": 580.0,
        "SMA200": 600.0,
        ADX_COL: 25.0,
        "EMA8": 520.0,
        "EMA21": 530.0,
        "EMA34": 540.0,
        "EMA55": 550.0,
        "EMA89": 560.0,
        STOCH_K_COL: 70.0,    # Pullback for short is >= 60
        "ATR": 30.0,
        "relative_volume_10d_calc": 1.5,
        "change": -1.2,
        "RSI2": 85.0,         # Bearish Trigger: Curr < 90
        "RSI2[1]": 95.0,      # Bearish Trigger: Prev >= 90
        "earnings_release_next_date": safe_earnings_date
    }

def Should_FilterStock_When_ADXIsBelowThreshold(mock_get_scanner_data: MagicMock) -> None:
    """
    Verifies that stocks with ADX < 20 are filtered out.
    Why: ADX < 20 indicates a weak trend. Bounce 2.0 requires a strong trend.
    """
    stock_data = get_default_stock_data()
    stock_data[ADX_COL] = 19.0
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
    stock_data[ADX_COL] = 20.0
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
    stock_data[STOCH_K_COL] = 41.0
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
    stock_data[STOCH_K_COL] = 40.0
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

# --- Tests for Individual Filter Methods (Diagnostic Support) ---

def test_filter_trend_strength() -> None:
    """
    Tests _filter_trend_strength in isolation.
    Why: Ensures the trend filter correctly identifies candidates above SMA200, SMA100, SMA50 with ADX[13] >= 20.
    """
    scanner = TaoBounceScanner(ScannerConfig(output_type="log"))
    df = pd.DataFrame([
        {"name": "PASS", "close": 110, "SMA200": 100, "SMA100": 90, "SMA50": 80, ADX_COL: 25},
        {"name": "FAIL_SMA200", "close": 90, "SMA200": 100, "SMA100": 80, "SMA50": 70, ADX_COL: 25},
        {"name": "FAIL_SMA100", "close": 95, "SMA200": 90, "SMA100": 100, "SMA50": 80, ADX_COL: 25},
        {"name": "FAIL_ADX", "close": 110, "SMA200": 100, "SMA100": 90, "SMA50": 80, ADX_COL: 15},
    ])
    result = scanner._filter_trend_strength(df)
    assert len(result) == 1
    assert result.iloc[0]["name"] == "PASS"

def test_filter_ema_stacking() -> None:
    """
    Tests _filter_ema_stacking in isolation.
    Why: Verifies that only 'perfectly' stacked EMAs pass the filter.
    """
    scanner = TaoBounceScanner(ScannerConfig(output_type="log"))
    df = pd.DataFrame([
        {"name": "PASS", "EMA8": 50, "EMA21": 40, "EMA34": 30, "EMA55": 20, "EMA89": 10},
        {"name": "FAIL_ORDER", "EMA8": 50, "EMA21": 30, "EMA34": 40, "EMA55": 20, "EMA89": 10},
    ])
    result = scanner._filter_ema_stacking(df)
    assert len(result) == 1
    assert result.iloc[0]["name"] == "PASS"

def test_filter_pullback() -> None:
    """
    Tests _filter_pullback in isolation.
    Why: Ensures stocks with Stoch.K[8]|3 <= 40 are correctly identified as pullbacks.
    """
    scanner = TaoBounceScanner(ScannerConfig(output_type="log"))
    df = pd.DataFrame([
        {"name": "PASS", STOCH_K_COL: 35},
        {"name": "FAIL", STOCH_K_COL: 45},
    ])
    result = scanner._filter_pullback(df)
    assert len(result) == 1
    assert result.iloc[0]["name"] == "PASS"

def test_filter_action_zone() -> None:
    """
    Tests _filter_action_zone in isolation.
    Why: Verifies that price must be within 1 ATR of the EMA21.
    """
    scanner = TaoBounceScanner(ScannerConfig(output_type="log"))
    df = pd.DataFrame([
        {"name": "PASS", "close": 105, "EMA21": 100, "ATR": 10}, # Dist 5 <= 10
        {"name": "FAIL", "close": 115, "EMA21": 100, "ATR": 10}, # Dist 15 > 10
    ])
    result = scanner._filter_action_zone(df)
    assert len(result) == 1
    assert result.iloc[0]["name"] == "PASS"

def test_filter_earnings() -> None:
    """
    Tests _filter_earnings in isolation.
    Why: Confirms that stocks with imminent earnings are filtered out.
    """
    scanner = TaoBounceScanner(ScannerConfig(output_type="log"))
    now = datetime.now()
    safe_date = (now + timedelta(days=20)).timestamp()
    risky_date = (now + timedelta(days=5)).timestamp()
    
    df = pd.DataFrame([
        {"name": "PASS", "earnings_release_next_date": safe_date},
        {"name": "FAIL", "earnings_release_next_date": risky_date},
        {"name": "PASS_NONE", "earnings_release_next_date": None},
    ])
    result = scanner._filter_earnings(df)
    assert len(result) == 2
    assert "PASS" in result["name"].values
    assert "PASS_NONE" in result["name"].values

def test_should_calculate_targets_for_long_setup(mock_get_scanner_data: MagicMock) -> None:
    """
    Verifies that target_conservative (EMA21 + 2*ATR) and target_stretch (EMA21 + 3*ATR) 
    are correctly calculated for long setups.
    """
    stock_data = get_default_stock_data()
    # EMA21=670, ATR=30. targets: 670+60=730, 670+90=760
    mock_data = [None, [stock_data]]
    mock_get_scanner_data.return_value = mock_data

    with patch("tao_bounce_scanner.get_writer") as mock_get_writer:
        mock_writer = MagicMock()
        mock_get_writer.return_value = mock_writer
        run_tao_of_trading_scan(ScannerConfig(output_type="log", direction="long"))
        
        args, _ = mock_writer.write.call_args
        df = args[0]
        assert df.iloc[0]['target_conservative'] == 730.0
        assert df.iloc[0]['target_stretch'] == 760.0
        assert df.iloc[0]['signal_direction'] == "LONG"

def test_should_calculate_targets_for_short_setup(mock_get_scanner_data: MagicMock) -> None:
    """
    Verifies that targets are correctly calculated for short setups (EMA21 - N*ATR).
    """
    stock_data = get_bearish_stock_data()
    # EMA21=530, ATR=30. targets: 530-60=470, 530-90=440
    mock_data = [None, [stock_data]]
    mock_get_scanner_data.return_value = mock_data

    with patch("tao_bounce_scanner.get_writer") as mock_get_writer:
        mock_writer = MagicMock()
        mock_get_writer.return_value = mock_writer
        run_tao_of_trading_scan(ScannerConfig(output_type="log", direction="short"))
        
        args, _ = mock_writer.write.call_args
        df = args[0]
        assert df.iloc[0]['target_conservative'] == 470.0
        assert df.iloc[0]['target_stretch'] == 440.0
        assert df.iloc[0]['signal_direction'] == "SHORT"

def test_filter_trend_strength_short() -> None:
    """
    Tests _filter_trend_strength for short direction.
    """
    scanner = TaoBounceScanner(ScannerConfig(output_type="log", direction="short"))
    df = pd.DataFrame([
        {"name": "PASS", "close": 90, "SMA200": 100, "SMA100": 110, "SMA50": 120, ADX_COL: 25},
        {"name": "FAIL_SMA200", "close": 110, "SMA200": 100, "SMA100": 120, "SMA50": 130, ADX_COL: 25},
    ])
    result = scanner._filter_trend_strength(df)
    assert len(result) == 1
    assert result.iloc[0]["name"] == "PASS"

def test_filter_rsi_trigger_short() -> None:
    """
    Tests _filter_rsi_trigger for short direction (crossed BELOW 90).
    """
    scanner = TaoBounceScanner(ScannerConfig(output_type="log", direction="short"))
    df = pd.DataFrame([
        {"name": "PASS", "RSI2[1]": 95, "RSI2": 85},   # Crossed down
        {"name": "FAIL_HIGH", "RSI2[1]": 95, "RSI2": 92}, # Still high
        {"name": "FAIL_LOW", "RSI2[1]": 85, "RSI2": 80}, # Already low
    ])
    result = scanner._filter_rsi_trigger(df)
    assert len(result) == 1
    assert result.iloc[0]["name"] == "PASS"

def test_should_include_all_filters_in_query() -> None:
    """
    Verifies that _build_query includes all required server-side filters.
    Why: Ensures that we are maximizing the use of server-side filtering to reduce data transfer.
    """
    scanner = TaoBounceScanner(ScannerConfig(output_type="log"))
    query = scanner._build_query()
    
    # Check that where clauses are present
    # Query stores filters in q.query['filter']
    filters = query.query['filter']
    
    # We expect several filters: type, subtype, market_cap, avg_volume, exchange, change, rel_vol, 
    # ADX, SMA50, SMA100, SMA200, EMA8>21, EMA21>34, EMA34>55, EMA55>89, Stoch.K, RSI2, RSI2[1], earnings
    # Total filters should be 19
    assert len(filters) == 19

    # Check for specific filters (by column name)
    col_names_left = [f['left'] for f in filters]
    col_names_right = [f['right'] for f in filters if isinstance(f['right'], str)]
    all_cols = col_names_left + col_names_right

    assert 'type' in all_cols
    assert 'subtype' in all_cols
    assert 'market_cap_basic' in all_cols
    assert 'average_volume_30d_calc' in all_cols
    assert 'exchange' in all_cols
    assert 'change' in all_cols
    assert 'relative_volume_10d_calc' in all_cols
    assert ADX_COL in all_cols
    assert 'SMA50' in all_cols
    assert 'SMA100' in all_cols
    assert 'SMA200' in all_cols
    assert 'EMA8' in all_cols
    assert 'EMA21' in all_cols
    assert 'EMA34' in all_cols
    assert 'EMA55' in all_cols
    assert STOCH_K_COL in all_cols
    assert 'RSI2' in all_cols
    assert 'RSI2[1]' in all_cols
    assert 'earnings_release_next_date' in all_cols

    # Verify RSI trigger logic in query
    rsi_filter = next(f for f in filters if f['left'] == 'RSI2')
    assert rsi_filter['operation'] == 'greater'
    assert rsi_filter['right'] == 10

    rsi_prev_filter = next(f for f in filters if f['left'] == 'RSI2[1]')
    assert rsi_prev_filter['operation'] == 'eless'
    assert rsi_prev_filter['right'] == 10

    # Verify earnings filter in query
    earnings_filter = next(f for f in filters if f['left'] == 'earnings_release_next_date')
    assert earnings_filter['operation'] == 'not_in_range'

def test_should_include_all_short_filters_in_query() -> None:
    """
    Verifies that _build_query includes all required server-side filters for SHORT direction.
    """
    scanner = TaoBounceScanner(ScannerConfig(output_type="log", direction="short"))
    query = scanner._build_query()
    filters = query.query['filter']
    
    assert len(filters) == 19

    # Verify RSI trigger logic for short (opposite of long)
    rsi_filter = next(f for f in filters if f['left'] == 'RSI2')
    assert rsi_filter['operation'] == 'less'
    assert rsi_filter['right'] == 90

    rsi_prev_filter = next(f for f in filters if f['left'] == 'RSI2[1]')
    assert rsi_prev_filter['operation'] == 'egreater'
    assert rsi_prev_filter['right'] == 90

    # Verify EMA stacking logic for short (opposite of long)
    ema8_filter = next(f for f in filters if f['left'] == 'EMA8')
    assert ema8_filter['operation'] == 'less'
    assert ema8_filter['right'] == 'EMA21'

def test_should_parse_cli_arguments_correctly():
    """
    Verifies that the parser correctly handles CLI arguments.
    Why: Ensures that users can control the scanner via command line as intended.
    """
    from tao_bounce_scanner import parse_args
    import sys
    
    test_args = [
        "tao_bounce_scanner.py", 
        "--direction", "short", 
        "--output_type", "file", 
        "--path", "/tmp/scans"
    ]
    
    with patch.object(sys, 'argv', test_args):
        args = parse_args()
        assert args.direction == "short"
        assert args.output_type == "file"
        assert args.path == "/tmp/scans"

def test_should_use_default_cli_arguments():
    """
    Verifies the default values of CLI arguments.
    Why: Confirms that the scanner behaves as expected when no flags are provided.
    """
    from tao_bounce_scanner import parse_args
    import sys
    
    test_args = ["tao_bounce_scanner.py"]
    
    with patch.object(sys, 'argv', test_args):
        args = parse_args()
        assert args.direction == "long"
        assert args.output_type == "log"
        assert args.aws_region == "us-east-1"
