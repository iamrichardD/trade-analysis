import sys
import pandas as pd
from tradingview_screener import Query, Column as col
from datetime import datetime
from storage import get_writer, ConfigurationError
import logging
import sys

def run_tao_of_trading_scan(config: dict):
    """
    Executes a scan for US equities meeting Simon Ree's Bounce 2.0 criteria.
    Returns a CSV formatted for LLM Knowledge Base ingestion.
    """

    # 1. Define the Query & Basic Filters (Liquid US Equities)
    query = (Query().set_markets('america')
            .select('name', 'close', 'EMA8', 'EMA21', 'EMA34', 'EMA55', 'EMA89', 'SMA200', 'ATR', 'ADX', 'Stoch.K', 'relative_volume_10d_calc')
            .where(col('type').isin(['stock']))
            .where(col('subtype').isin(['common']))
            .where(col('market_cap_basic') > 1_000_000_000)  # Market Cap > $1B
            .where(col('average_volume_30d_calc') > 500_000) # Vol > 500k
            .where(col('exchange').isin(['NYSE', 'NASDAQ'])))

    # 2. Execute Scan and Select Relevant Columns
    # Note: All filters are applied post-fetch for precision
    data = query.get_scanner_data()[1]

    # Convert to DataFrame
    df = pd.DataFrame(data)

    if df.empty:
        logging.info("No stocks currently meet the Bounce 2.0 criteria.")
        return

    # 3. Apply Technical Stack (Trend & Strength) - Post-process
    df = df[df['ADX'] >= 20]
    df = df[df['close'] > df['SMA200']]

    # 4. Apply EMA Stacking Logic (8 > 21 > 34 > 55 > 89) - Post-process
    df = df[df['EMA8'] > df['EMA21']]
    df = df[df['EMA21'] > df['EMA34']]
    df = df[df['EMA34'] > df['EMA55']]
    df = df[df['EMA55'] > df['EMA89']]

    # 5. Apply Pullback Logic (Stochastics <= 40) - Post-process
    df = df[df['Stoch.K'] <= 40]

    # 6. Apply Action Zone Filter - Post-process
    # Price must be within 1 ATR of the 21 EMA
    df['dist_from_mean'] = abs(df['close'] - df['EMA21'])
    df = df[df['dist_from_mean'] <= df['ATR']]

    # 7. Final Formatting
    output_columns = [
        'name', 'close', 'SMA200', 'EMA8', 'EMA21', 'EMA34', 'EMA55', 'EMA89', 'ATR', 'ADX',
        'Stoch.K', 'relative_volume_10d_calc'
    ]
    final_df = df[output_columns].copy()

    try:
        writer = get_writer(config)
        if not final_df.empty:
            writer.write(final_df)
        else:
            logging.info("No stocks found after filtering to write to output.")
    except ConfigurationError as e:
        logging.error(e)

if __name__ == "__main__":
    import sys
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    # Example usage with log output
    log_config = {"output_type": "log"}
    run_tao_of_trading_scan(log_config)
