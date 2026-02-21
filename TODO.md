# TODO

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
- [ ] **Move Filters Server-side**: Progressively move local filters to the TradingView `Query().where(...)` to reduce data transfer and over-filtering risks:
    - [x] Move Trend & Strength (ADX >= 20, Close > SMA200).
    - [x] Move EMA Stacking (8 > 21 > 34 > 55 > 89).
    - [x] Move Pullback (Stochastic K <= 40).
    - [x] Move RSI(2) condition (RSI(2) > 10).
    - [ ] Move Earnings condition (Exclude if next 14 days) - Researching range-based server-side filter possibilities.
    - [ ] Move Action Zone (Price within 1 ATR of EMA21 - Requires cross-column math, currently local only).

### Technical Manual Alignment & Refinement
- [x] **Refine Indicator Periods**: Update query columns and logic to match the manual's specific periods:
    - [x] Use `ADX(13)` instead of default (14).
    - [x] Use `Stochastics(8, 3)` instead of default.
- [x] **Expand Trend Filters**: Add additional institutional "Lines-in-the-Sand" to the query:
    - [x] Add `Close > SMA50`.
    - [x] Add `Close > SMA100`.
- [x] **Volume/Momentum Quality**: Add additional liquidity and momentum filters to the query:
    - [x] Add `Relative Volume > 1.0` (Ensuring active participation).
    - [x] Add `Change % > 0` (Confirming daily bullish bias).
- [x] **Scale Scanning Capacity**: Increase query `limit` from 150 to 500 to capture a wider universe of stacked trends before applying the highly restrictive RSI(2) and Action Zone filters.
