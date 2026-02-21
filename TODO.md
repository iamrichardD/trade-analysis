# TODO

> [!IMPORTANT]
> **MAINTENANCE PROTOCOL:** This file is APPEND-ONLY for new tasks. Do NOT overwrite or delete previous tasks. Mark completed items with `[x]`. New features or bugs found must be added as new items at the bottom of the relevant section or in a new session block.

- [x] Study Python code and identify improvement opportunities.
- [x] Document improvement opportunities in `TODO.md`.
- [x] Implement improvements identified.

## Identified Improvement Opportunities

### Refactoring & SOLID
- [x] **Refactor `tao_bounce_scanner.py`**: Break down the monolithic `run_tao_of_trading_scan` function. Separate:
    - Query definition and fetching.
    - Data filtering based on strategy rules.
    - Reporting and writing output.
- [x] **Configuration System**: Replace raw dictionaries with a dedicated `ScannerConfig` class or similar for better validation and type safety.

### Trading Logic (Bounce 2.0)
- [x] **Implement RSI(2) Trigger**: Add the final bullish/bearish entry trigger based on RSI(2) (crossing back above 10/below 90).
- [x] **Negative Constraint - Earnings Check**: Implement a check to exclude stocks with an earnings announcement within the next 14 days. This is a critical risk rule from `GEMINI.md`.
- [x] **Support Bearish Setup**: Add logic for Bearish Bounce 2.0 (Bearish Stacked EMAs, Stoch.K >= 60, RSI2 crossing below 90).
- [x] **Target Calculations**: Add `target_conservative` (2 ATR) and `target_stretch` (3 ATR) to the output for better actionability.

### Quality & Standards
- [x] **Strong Typing**: Add comprehensive type hints (Mypy compliant) to all functions, variables, and parameters in:
    - `tao_bounce_scanner.py`
    - `storage.py`
    - `test_scanner.py`
    - `test_storage.py`
- [x] **Code Cleanup**: Remove duplicate `sys` import in `tao_bounce_scanner.py`.
- [x] **Documentation**: Improve docstrings for all functions to follow a consistent standard and explain the "Why".
- [x] **Test Refactoring**: Add type hints to tests and ensure all tests follow a consistent naming convention.
- [x] **Constants Management**: Extract hardcoded thresholds (ADX=20, Stoch.K=40, etc.) into a configuration or constants module.
- [x] **Diagnostic/Over-filtering Support**:
    - [x] Refactor `_apply_filters` into modular private methods.
    - [x] Add diagnostic logging to report candidate counts after each filter step.
    - [x] Add unit tests for each individual filter method in `test_scanner.py`.
- [x] **Data Integrity**: Ensure any column data used in local calculations (e.g., ATR, EMA21 for Action Zone) are explicitly included in the final `DataWriter` output for auditability.

### Query Optimization & Scaling
- [x] **Address Default Result Limit (50)**: Increase the `limit` in the TradingView query to ensure a larger starting candidate pool. (Increased to 500).
- [x] **Move Filters Server-side**: Progressively move local filters to the TradingView `Query().where(...)` to reduce data transfer and over-filtering risks:
    - [x] Move Trend & Strength (ADX >= 20, Close > SMA200).
    - [x] Move EMA Stacking (8 > 21 > 34 > 55 > 89).
    - [x] Move Pullback (Stochastic K <= 40).
    - [x] Move RSI(2) condition (RSI(2) > 10).
    - [x] Move RSI(2) trigger (RSI2[1] <= 10).
    - [x] Move Earnings condition: Use `.where(col('earnings_release_next_date').not_between(now, future_14))` to filter server-side.
    - [x] **Constraint - Action Zone**: Confirmed as "local only" due to library lack of cross-column arithmetic support.

### Technical Manual Alignment & Refinement
- [x] **INVESTIGATE: Custom Indicator Periods**: Discovery: `EMA` supports custom periods, but `ADX` and `Stochastics` return `None` for non-standard periods in the current API version.
    - *Decision:* Stick with default `ADX(14)` and `Stochastics(14,3,3)` as functional proxies until a calculation-capable API endpoint is identified.
- [x] **Refine Indicator Periods**: Update query columns and logic to match the manual's specific periods (Currently using proxies - see investigation task).
- [x] **Expand Trend Filters**: Add additional institutional "Lines-in-the-Sand" to the query:
    - [x] Add `Close > SMA50`.
    - [x] Add `Close > SMA100`.
- [x] **Volume/Momentum Quality**: Add additional liquidity and momentum filters to the query:
    - [x] Add `Relative Volume > 1.0` (Ensuring active participation).
    - [x] Add `Change % > 0` (Confirming daily bullish bias).
- [x] **Scale Scanning Capacity**: Increase query `limit` from 150 to 500 to capture a wider universe of stacked trends before applying the highly restrictive RSI(2) and Action Zone filters.
- [x] **Actionable Targets**: Calculate and include Conservative (2 ATR) and Stretch (3 ATR) targets in the reporting layer output.

### AWS SNS Email Notifications (Infrastructure & Code)
- [x] **Infrastructure (Terraform)**:
    - [x] Create `aws_sns_topic` for scanner alerts (e.g., `tao-scanner-alerts`).
    - [x] Create `aws_sns_topic_subscription` resources for configurable email list.
    - [x] Create `aws_iam_user` for the scanner machine account.
    - [x] Create `aws_iam_policy` with `sns:Publish` permissions restricted specifically to the topic ARN (DevSecOps Least Privilege).
    - [x] Create `aws_iam_access_key` for machine account authentication and instructions for secure retrieval.
- [x] **Software Architecture (SNS Integration)**:
    - [x] Add `boto3` and `types-boto3` to `requirements.txt`.
    - [x] Update `ScannerConfig` in `storage.py` with `sns_topic_arn`, `aws_region`, and `email` output type.
    - [x] Implement `SNSWriter(DataWriter)` in `storage.py` to format (DataFrame to Markdown) and publish results via SNS.
    - [x] Update `get_writer` factory in `storage.py` to support the `email` output type.
- [x] **DevSecOps & Validation**:
    - [x] Update `Containerfile` and `Containerfile.test` to include `boto3` in the runtime and test environments.
    - [x] Create `test_sns_writer.py` using `moto` to verify notification logic without making live AWS calls.
    - [x] Document secure credential injection workflow via Podman secrets or environment files.
- [x] **Documentation**:
    - [x] Provide step-by-step instructions for subscription confirmation and Terraform deployment.
