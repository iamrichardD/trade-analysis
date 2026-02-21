import sys
import pandas as pd
from tradingview_screener import Query, Column as col
from datetime import datetime, timedelta
import logging
from typing import List, Optional, Any, Dict, Union
from storage import get_writer, ConfigurationError, ScannerConfig, DataWriter

# Constants for Bounce 2.0 Strategy
# Why: Centralized configuration allows for easy tuning of strategy parameters without digging into code.
MIN_MARKET_CAP: int = 1_000_000_000
MIN_AVG_VOLUME: int = 500_000
MIN_ADX: int = 20
STOCH_PULLBACK_THRESHOLD_BULLISH: int = 40
STOCH_PULLBACK_THRESHOLD_BEARISH: int = 60
RSI_BULLISH_CROSS_LEVEL: int = 10
RSI_BEARISH_CROSS_LEVEL: int = 90
EARNINGS_BUFFER_DAYS: int = 14
EMA_FAST: int = 8
EMA_MEDIUM: int = 21
EMA_SLOW: int = 34
EMA_EXTENDED_1: int = 55
EMA_EXTENDED_2: int = 89
SMA_TREND: int = 200
SMA_INSTITUTIONAL_50: int = 50
SMA_INSTITUTIONAL_100: int = 100

# Indicator Period Mappings (TradingView Column Names)
ADX_COL: str = "ADX"
STOCH_K_COL: str = "Stoch.K"

class TaoBounceScanner:
    """
    Scanner for US equities meeting Simon Ree's Bounce 2.0 criteria.
    Encapsulates logic for data fetching, filtering, and reporting.
    """

    def __init__(self, config: Union[ScannerConfig, Dict[str, Any]]):
        self.config = config
        self.writer: DataWriter = get_writer(config)

    def _get_direction(self) -> str:
        """Helper to get direction from config, defaulting to 'long'."""
        if isinstance(self.config, dict):
            return self.config.get("direction", "long")
        return self.config.direction

    def _build_query(self) -> Query:
        """
        Defines the initial query for liquid US common stocks meeting Bounce 2.0 criteria.
        Why: We only want to trade liquid stocks with orderly trends (EMA stacked)
        that are in a pullback and starting to show momentum.
        """
        now = datetime.now()
        future_14 = now + timedelta(days=EARNINGS_BUFFER_DAYS)
        direction = self._get_direction()

        filters = [
            col('type').isin(['stock']),
            col('subtype').isin(['common']),
            col('market_cap_basic') > MIN_MARKET_CAP,
            col('average_volume_30d_calc') > MIN_AVG_VOLUME,
            col('exchange').isin(['NYSE', 'NASDAQ']),
            col('relative_volume_10d_calc') > 1.0,
            col(ADX_COL) >= MIN_ADX,
            col('earnings_release_next_date').not_between(now.timestamp(), future_14.timestamp())
        ]

        if direction == "long":
            filters.extend([
                col('change') > 0,
                col('close') > col(f'SMA{SMA_INSTITUTIONAL_50}'),
                col('close') > col(f'SMA{SMA_INSTITUTIONAL_100}'),
                col('close') > col(f'SMA{SMA_TREND}'),
                col(f'EMA{EMA_FAST}') > col(f'EMA{EMA_MEDIUM}'),
                col(f'EMA{EMA_MEDIUM}') > col(f'EMA{EMA_SLOW}'),
                col(f'EMA{EMA_SLOW}') > col(f'EMA{EMA_EXTENDED_1}'),
                col(f'EMA{EMA_EXTENDED_1}') > col(f'EMA{EMA_EXTENDED_2}'),
                col(STOCH_K_COL) <= STOCH_PULLBACK_THRESHOLD_BULLISH,
                col('RSI2') > RSI_BULLISH_CROSS_LEVEL,
                col('RSI2[1]') <= RSI_BULLISH_CROSS_LEVEL
            ])
        else: # short
            filters.extend([
                col('change') < 0,
                col('close') < col(f'SMA{SMA_INSTITUTIONAL_50}'),
                col('close') < col(f'SMA{SMA_INSTITUTIONAL_100}'),
                col('close') < col(f'SMA{SMA_TREND}'),
                col(f'EMA{EMA_FAST}') < col(f'EMA{EMA_MEDIUM}'),
                col(f'EMA{EMA_MEDIUM}') < col(f'EMA{EMA_SLOW}'),
                col(f'EMA{EMA_SLOW}') < col(f'EMA{EMA_EXTENDED_1}'),
                col(f'EMA{EMA_EXTENDED_1}') < col(f'EMA{EMA_EXTENDED_2}'),
                col(STOCH_K_COL) >= STOCH_PULLBACK_THRESHOLD_BEARISH,
                col('RSI2') < RSI_BEARISH_CROSS_LEVEL,
                col('RSI2[1]') >= RSI_BEARISH_CROSS_LEVEL
            ])

        return (Query().set_markets('america')
                .select('name', 'close', 'EMA8', 'EMA21', 'EMA34', 'EMA55', 'EMA89', 
                        'SMA50', 'SMA100', 'SMA200', 
                        'ATR', ADX_COL, STOCH_K_COL, 'relative_volume_10d_calc', 'change',
                        'RSI2', 'RSI2[1]', 'earnings_release_next_date')
                .where(*filters)
                .limit(500))

    def _fetch_data(self) -> pd.DataFrame:
        """
        Executes the query and returns the results as a DataFrame.
        Why: Abstracts the external API call, making the main logic testable/mockable.
        """
        query = self._build_query()
        _, data = query.get_scanner_data()
        df = pd.DataFrame(data)
        
        # Ensure custom period columns are numeric
        # Why: TradingView API may return non-standard columns as objects/strings.
        for col_name in [ADX_COL, STOCH_K_COL]:
            if col_name in df.columns:
                df[col_name] = pd.to_numeric(df[col_name], errors='coerce')
        
        return df

    def _apply_filters(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Applies the Bounce 2.0 technical filters to the DataFrame sequentially.
        Why: This is the core strategy logic. We track the count at each step to help
        diagnose over-filtering.
        """
        if df.empty:
            return df

        initial_count = len(df)
        logging.info(f"Starting filter pipeline with {initial_count} candidates.")

        # 1. Trend & Strength (Already filtered in Query, validated locally)
        df = self._filter_trend_strength(df)
        logging.info(f"Step 1 (Trend & Strength): {len(df)} remaining")
        if df.empty: return df

        # 2. EMA Stacking Logic (Already filtered in Query, validated locally)
        df = self._filter_ema_stacking(df)
        logging.info(f"Step 2 (EMA Stacking): {len(df)} remaining")
        if df.empty: return df

        # 3. Pullback Logic (Already filtered in Query, validated locally)
        df = self._filter_pullback(df)
        logging.info(f"Step 3 (Pullback): {len(df)} remaining")
        if df.empty: return df

        # 4. Action Zone Filter
        df = self._filter_action_zone(df)
        logging.info(f"Step 4 (Action Zone): {len(df)} remaining")
        if df.empty: return df

        # 5. Earnings Check
        df = self._filter_earnings(df)
        logging.info(f"Step 5 (Earnings Check): {len(df)} remaining")
        if df.empty: return df

        # 6. RSI(2) Trigger (Partially filtered in Query, cross validated locally)
        df = self._filter_rsi_trigger(df)
        logging.info(f"Step 6 (RSI Trigger): {len(df)} remaining")

        return df

    def _filter_trend_strength(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Filters for stocks in a strong trend (ADX > 20) and above/below the relevant SMAs.
        """
        direction = self._get_direction()
        mask = (df[ADX_COL] >= MIN_ADX)
        
        if direction == "long":
            mask &= (df['close'] > df[f'SMA{SMA_TREND}']) & \
                    (df['close'] > df[f'SMA{SMA_INSTITUTIONAL_50}']) & \
                    (df['close'] > df[f'SMA{SMA_INSTITUTIONAL_100}'])
        else:
            mask &= (df['close'] < df[f'SMA{SMA_TREND}']) & \
                    (df['close'] < df[f'SMA{SMA_INSTITUTIONAL_50}']) & \
                    (df['close'] < df[f'SMA{SMA_INSTITUTIONAL_100}'])
                    
        return df[mask]

    def _filter_ema_stacking(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Filters for 'Perfect' EMA stacking (8 > 21 > 34 > 55 > 89 for long).
        """
        direction = self._get_direction()
        if direction == "long":
            mask = (df[f'EMA{EMA_FAST}'] > df[f'EMA{EMA_MEDIUM}']) & \
                   (df[f'EMA{EMA_MEDIUM}'] > df[f'EMA{EMA_SLOW}']) & \
                   (df[f'EMA{EMA_SLOW}'] > df[f'EMA{EMA_EXTENDED_1}']) & \
                   (df[f'EMA{EMA_EXTENDED_1}'] > df[f'EMA{EMA_EXTENDED_2}'])
        else:
            mask = (df[f'EMA{EMA_FAST}'] < df[f'EMA{EMA_MEDIUM}']) & \
                   (df[f'EMA{EMA_MEDIUM}'] < df[f'EMA{EMA_SLOW}']) & \
                   (df[f'EMA{EMA_SLOW}'] < df[f'EMA{EMA_EXTENDED_1}']) & \
                   (df[f'EMA{EMA_EXTENDED_1}'] < df[f'EMA{EMA_EXTENDED_2}'])
        return df[mask]

    def _filter_pullback(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Filters for stocks that have pulled back (Stochastics threshold).
        """
        direction = self._get_direction()
        if direction == "long":
            return df[df[STOCH_K_COL] <= STOCH_PULLBACK_THRESHOLD_BULLISH]
        else:
            return df[df[STOCH_K_COL] >= STOCH_PULLBACK_THRESHOLD_BEARISH]

    def _filter_action_zone(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Filters for stocks where price is within 1 ATR of the EMA21 'Action Zone'.
        """
        df = df.copy() # Avoid SettingWithCopyWarning
        df['dist_from_mean'] = abs(df['close'] - df[f'EMA{EMA_MEDIUM}'])
        return df[df['dist_from_mean'] <= df['ATR']].drop(columns=['dist_from_mean'])

    def _filter_earnings(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Filters out stocks with earnings announcements within the next 14 days.
        """
        if 'earnings_release_next_date' not in df.columns:
            return df

        now = datetime.now()
        buffer_date = now + timedelta(days=EARNINGS_BUFFER_DAYS)
        
        # Ensure it's numeric
        df = df.copy()
        df['earnings_ts'] = pd.to_numeric(df['earnings_release_next_date'], errors='coerce')
        
        now_ts = now.timestamp()
        buffer_ts = buffer_date.timestamp()
        
        mask_earnings_safe = (df['earnings_ts'].isna()) | \
                             (df['earnings_ts'] < now_ts) | \
                             (df['earnings_ts'] > buffer_ts)
        
        return df[mask_earnings_safe].drop(columns=['earnings_ts'])

    def _filter_rsi_trigger(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Filters for the RSI(2) trigger (crossed above 10 for long, below 90 for short).
        """
        if 'RSI2' not in df.columns or 'RSI2[1]' not in df.columns:
            return df
            
        direction = self._get_direction()
        if direction == "long":
            mask = (df['RSI2[1]'] <= RSI_BULLISH_CROSS_LEVEL) & (df['RSI2'] > RSI_BULLISH_CROSS_LEVEL)
        else:
            mask = (df['RSI2[1]'] >= RSI_BEARISH_CROSS_LEVEL) & (df['RSI2'] < RSI_BEARISH_CROSS_LEVEL)
        return df[mask]

    def run_scan(self) -> None:
        """
        Executes the full scanning process.
        Why: Orchestrates the fetch-filter-write pipeline.
        """
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

            # Final Selection & Metadata enhancement
            direction = self._get_direction()
            final_df = filtered_df.copy()
            final_df['signal_direction'] = direction.upper()
            
            # Calculate Targets per Technical Manual
            # Conservative: 2 ATR from EMA21, Stretch: 3 ATR from EMA21
            if direction == "long":
                final_df['target_conservative'] = final_df[f'EMA{EMA_MEDIUM}'] + (2 * final_df['ATR'])
                final_df['target_stretch'] = final_df[f'EMA{EMA_MEDIUM}'] + (3 * final_df['ATR'])
            else:
                final_df['target_conservative'] = final_df[f'EMA{EMA_MEDIUM}'] - (2 * final_df['ATR'])
                final_df['target_stretch'] = final_df[f'EMA{EMA_MEDIUM}'] - (3 * final_df['ATR'])

            output_columns = [
                'name', 'signal_direction', 'close', 
                'target_conservative', 'target_stretch',
                f'SMA{SMA_INSTITUTIONAL_50}', f'SMA{SMA_INSTITUTIONAL_100}', f'SMA{SMA_TREND}', 
                f'EMA{EMA_FAST}', f'EMA{EMA_MEDIUM}', f'EMA{EMA_SLOW}', 
                f'EMA{EMA_EXTENDED_1}', f'EMA{EMA_EXTENDED_2}', 
                'ATR', ADX_COL, STOCH_K_COL, 'relative_volume_10d_calc', 'change',
                'RSI2', 'RSI2[1]', 'earnings_release_next_date'
            ]
            
            # Ensure columns exist before selecting
            cols_to_select = [c for c in output_columns if c in final_df.columns]
            final_df = final_df[cols_to_select]
            
            self.writer.write(final_df)

        except Exception as e:
            logging.error(f"Error during scan: {e}")

def run_tao_of_trading_scan(config: Union[ScannerConfig, Dict[str, Any]]) -> None:
    """
    Wrapper for backward compatibility.
    Why: Allows existing external scripts to call the scanner without knowing about the class structure.
    """
    scanner = TaoBounceScanner(config)
    scanner.run_scan()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    log_config = ScannerConfig(output_type="log")
    run_tao_of_trading_scan(log_config)
