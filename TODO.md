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
