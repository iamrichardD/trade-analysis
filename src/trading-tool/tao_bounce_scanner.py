import sys
import pandas as pd
from tradingview_screener import Query, Column as col
from datetime import datetime
import logging
from typing import List, Optional, Any, Dict, Union
from storage import get_writer, ConfigurationError, ScannerConfig, DataWriter

# Constants for Bounce 2.0 Strategy
MIN_MARKET_CAP: int = 1_000_000_000
MIN_AVG_VOLUME: int = 500_000
MIN_ADX: int = 20
STOCH_PULLBACK_THRESHOLD: int = 40
EMA_FAST: int = 8
EMA_MEDIUM: int = 21
EMA_SLOW: int = 34
EMA_EXTENDED_1: int = 55
EMA_EXTENDED_2: int = 89
SMA_TREND: int = 200

class TaoBounceScanner:
    """
    Scanner for US equities meeting Simon Ree's Bounce 2.0 criteria.
    Encapsulates logic for data fetching, filtering, and reporting.
    """

    def __init__(self, config: Union[ScannerConfig, Dict[str, Any]]):
        self.config = config
        self.writer: DataWriter = get_writer(config)

    def _build_query(self) -> Query:
        """Defines the initial query for liquid US common stocks."""
        return (Query().set_markets('america')
                .select('name', 'close', 'EMA8', 'EMA21', 'EMA34', 'EMA55', 'EMA89', 'SMA200', 'ATR', 'ADX', 'Stoch.K', 'relative_volume_10d_calc')
                .where(col('type').isin(['stock']))
                .where(col('subtype').isin(['common']))
                .where(col('market_cap_basic') > MIN_MARKET_CAP)
                .where(col('average_volume_30d_calc') > MIN_AVG_VOLUME)
                .where(col('exchange').isin(['NYSE', 'NASDAQ'])))

    def _fetch_data(self) -> pd.DataFrame:
        """Executes the query and returns the results as a DataFrame."""
        query = self._build_query()
        _, data = query.get_scanner_data()
        return pd.DataFrame(data)

    def _apply_filters(self, df: pd.DataFrame) -> pd.DataFrame:
        """Applies the Bounce 2.0 technical filters to the DataFrame."""
        if df.empty:
            return df

        # 1. Trend & Strength
        df = df[df['ADX'] >= MIN_ADX]
        df = df[df['close'] > df[f'SMA{SMA_TREND}']]

        # 2. EMA Stacking Logic (8 > 21 > 34 > 55 > 89)
        df = df[df[f'EMA{EMA_FAST}'] > df[f'EMA{EMA_MEDIUM}']]
        df = df[df[f'EMA{EMA_MEDIUM}'] > df[f'EMA{EMA_SLOW}']]
        df = df[df[f'EMA{EMA_SLOW}'] > df[f'EMA{EMA_EXTENDED_1}']]
        df = df[df[f'EMA{EMA_EXTENDED_1}'] > df[f'EMA{EMA_EXTENDED_2}']]

        # 3. Pullback Logic (Stochastics <= 40)
        df = df[df['Stoch.K'] <= STOCH_PULLBACK_THRESHOLD]

        # 4. Action Zone Filter: Price within 1 ATR of the EMA21
        df['dist_from_mean'] = abs(df['close'] - df[f'EMA{EMA_MEDIUM}'])
        df = df[df['dist_from_mean'] <= df['ATR']]

        return df

    def run_scan(self) -> None:
        """Executes the full scanning process."""
        logging.info("Starting Bounce 2.0 scan...")
        
        try:
            df = self._fetch_data()
            if df.empty:
                logging.info("Initial query returned no results.")
                return

            filtered_df = self._apply_filters(df)
            
            if filtered_df.empty:
                logging.info("No stocks currently meet the Bounce 2.0 criteria after filtering.")
                return

            # Final Selection for reporting
            output_columns = [
                'name', 'close', f'SMA{SMA_TREND}', f'EMA{EMA_FAST}', f'EMA{EMA_MEDIUM}', 
                f'EMA{EMA_SLOW}', f'EMA{EMA_EXTENDED_1}', f'EMA{EMA_EXTENDED_2}', 
                'ATR', 'ADX', 'Stoch.K', 'relative_volume_10d_calc'
            ]
            final_df = filtered_df[output_columns].copy()
            self.writer.write(final_df)

        except Exception as e:
            logging.error(f"Error during scan: {e}")

def run_tao_of_trading_scan(config: Union[ScannerConfig, Dict[str, Any]]) -> None:
    """Wrapper for backward compatibility."""
    scanner = TaoBounceScanner(config)
    scanner.run_scan()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    log_config = ScannerConfig(output_type="log")
    run_tao_of_trading_scan(log_config)
