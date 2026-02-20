import pandas as pd
from unittest.mock import patch, MagicMock
from tao_bounce_scanner import TaoBounceScanner
from storage import ScannerConfig
import logging
import sys

# Setup logging
logging.basicConfig(level=logging.INFO, stream=sys.stdout)

def test_diagnostic_scan():
    config = ScannerConfig(output_type="log")
    scanner = TaoBounceScanner(config)
    
    # Mock data with 5 stocks
    # 2 pass trend
    # 2 pass EMA (1 of the above)
    # All 5 have Stoch.K > 40 (should pass now because filter is disabled)
    mock_data = [
        {"name": "STOCK1", "ADX": 25, "close": 110, "SMA200": 100, "EMA8": 50, "EMA21": 40, "EMA34": 30, "EMA55": 20, "EMA89": 10, "Stoch.K": 80, "ATR": 10}, # Passes Trend, EMA, Pullback (disabled)
        {"name": "STOCK2", "ADX": 15, "close": 110, "SMA200": 100, "EMA8": 50, "EMA21": 40, "EMA34": 30, "EMA55": 20, "EMA89": 10, "Stoch.K": 80, "ATR": 10}, # Fails Trend
        {"name": "STOCK3", "ADX": 25, "close": 90, "SMA200": 100, "EMA8": 50, "EMA21": 40, "EMA34": 30, "EMA55": 20, "EMA89": 10, "Stoch.K": 80, "ATR": 10}, # Fails Trend (Close < SMA)
        {"name": "STOCK4", "ADX": 25, "close": 110, "SMA200": 100, "EMA8": 30, "EMA21": 40, "EMA34": 30, "EMA55": 20, "EMA89": 10, "Stoch.K": 80, "ATR": 10}, # Passes Trend, Fails EMA
        {"name": "STOCK5", "ADX": 25, "close": 110, "SMA200": 100, "EMA8": 50, "EMA21": 40, "EMA34": 30, "EMA55": 20, "EMA89": 10, "Stoch.K": 80, "ATR": 10}, # Passes Trend, EMA, Pullback (disabled)
    ]
    
    with patch.object(TaoBounceScanner, "_fetch_data", return_value=pd.DataFrame(mock_data)):
        # We also need to mock _filter_earnings and _filter_rsi_trigger as they might filter out our test data if columns are missing
        with patch.object(TaoBounceScanner, "_filter_earnings", side_effect=lambda x: x):
            with patch.object(TaoBounceScanner, "_filter_rsi_trigger", side_effect=lambda x: x):
                with patch.object(TaoBounceScanner, "_filter_action_zone", side_effect=lambda x: x):
                    scanner.run_scan()

if __name__ == "__main__":
    test_diagnostic_scan()
