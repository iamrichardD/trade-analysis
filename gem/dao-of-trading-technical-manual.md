# THE TAO OF TRADING: TECHNICAL OPERATING MANUAL

# CRITICAL RISK & MATH REFERENCE

**Expectancy Formula**
Used to determine the long-term viability of a trading system:
$$Expectancy = (Probability\ of\ Win \times Average\ Win) - (Probability\ of\ Loss \times Average\ Loss)$$

**Position Sizing (Account Scalability)**
* **Large Accounts:** 1% to 2% of Net Liquidating Value (NLV) risked per trade.
* **Small Accounts (< $50,000):** Up to 10% of account risked per trade (allocated as 5% initial + 5% at milestone).

**The 15% NLV Rule (Portfolio Stop-Loss)**
A mandatory "peak-to-trough" trailing stop on the total portfolio value.
* **Threshold:** 15% drop from the highest NLV point.
* **Action:** Close all positions immediately and remain in cash for 24+ hours.

**Option Delta ($\Delta$) Guidelines**
* **Naked Calls:** Target Delta $\approx 0.70$ (In-the-Money).
* **Naked Puts:** Target Delta $\approx 0.60$ (In-the-Money).
* **At-the-Money (ATM):** Delta $\approx 0.50$.

**Keltner Channel Calculations (Mean Reversion)**
Calculated using the 21-period EMA as the baseline:
* **Action Zone:** Price within $\pm 1$ Average True Range (ATR).
* **Conservative Target:** 2 ATRs from the 21 EMA.
* **Stretch Target:** 3 ATRs from the 21 EMA.

**Growth Target**
* **Weekly Compound Target:** 2.5% of account value.

---

# I. MARKET FRAMEWORK & PHILOSOPHICAL GROUNDING
**Metadata:** Topic: Counter-Conventional Finance | Author: Simon Ree | Category: Mindset

> [!WARNING]
> **FIDUCIARY ALERT:** Traditional "Buy and Hold" strategies and 10% annual return targets are designed for institutional scalability and fee generation, not rapid individual wealth acceleration.

## Executive Summary (Expert)
* **Objective:** Wealth acceleration through asymmetric payoff profiles.
* **Core Edge:** Trading patterns/emotions rather than fundamental "investing."
* **Risk Paradox:** Lower risk (high probability setups) leads to higher returns.

## Professional ELI5
Most "Wall Street" advice is built to manage billions of dollars safely while charging fees, not to help you grow a smaller account quickly. Trading is the business of identifying repeatable patterns in human behavior (fear and greed) and profiting from them.
* **The Math:** Instead of settling for 10% a year, we focus on trades where the potential reward is significantly higher than the amount we risk on the trade.

---

# II. THE TECHNICAL STACK (INDICATORS)
**Metadata:** Topic: Standardized Indicator Suite | Author: Simon Ree | Category: Strategy

The following technical stack must be configured on all scanning and charting platforms:

| Indicator | Type | Period/Setting | Function |
| :--- | :--- | :--- | :--- |
| **Short EMA** | Exponential | 8, 21, 34 | Immediate trend & Mean baseline |
| **Long EMA** | Exponential | 55, 89 | Medium-term trend support |
| **Core SMA** | Simple | 50, 100, 200 | Institutional "Line-in-the-Sand" |
| **RSI** | Momentum | 2 | Mean Reversion trigger |
| **Stochastics** | Momentum | 8, 3 | Pullback/Rally validation |
| **ADX** | Trend Strength | 13 | Filter: Must be $\ge 20$ for trend trades |

---

# III. STRATEGY: THE BOUNCE 2.0
**Metadata:** Topic: Mean Reversion & Trend Continuation | Author: Simon Ree | Category: Strategy

> [!WARNING]
> **NEGATIVE CONSTRAINT:** DO NOT enter a Bounce 2.0 setup if an earnings announcement is scheduled within the next 14 days.



## Executive Summary (Expert)
* **Filter 1 (Trend):** EMAs must be "Bullish Stacked" (8 > 21 > 34 > 55 > 89) or "Bearish Stacked."
* **Filter 2 (Strength):** ADX(13) must be $\ge 20$.
* **Filter 3 (Mean):** Price must be within the **Action Zone** ($\pm 1$ ATR of the 21 EMA).
* **Setup:** Slow Stochastics $\le 40$ (Bullish) or $\ge 60$ (Bearish).
* **Trigger (RSI-2):** Bullish entry when RSI(2) crosses back above 10; Bearish when crossing back below 90.

## Professional ELI5
Imagine an "invisible elastic band" connecting the stock price to its average (the 21 EMA). When the price pulls too far away, it eventually snaps back. This strategy waits for the stock to "snap back" to its average during a strong trend, and we "buy the dip" just as it starts moving back in the original direction.
* **The Math:** We use the **Keltner Channels** to measure how far that elastic band is stretched. We only enter when the price is close to the average (within 1 ATR) so we aren't "chasing" the move.

---

# IV. DERIVATIVE SELECTION & ARCHITECTURE
**Metadata:** Topic: Options & Vertical Spreads | Author: Simon Ree | Category: Strategy

> [!WARNING]
> **THETA DECAY:** An option loses two-thirds of its value during the last third of its life. Avoid holding long "Out-of-the-Money" (OTM) options into the final weeks of expiration.

## Executive Summary (Expert)
* **Naked Options:** Buy ITM (In-the-Money) with $\Delta \approx 0.70$ (Calls) or $\Delta \approx 0.60$ (Puts).
* **Vertical Spreads:** Use to eliminate Theta (time decay) and lower capital outlay.
* **Strategy:** Buy ATM/ITM option, sell OTM option of the same expiry.
* **Exit Rule:** Exit spread when value reaches 80-85% of max spread width (Delta 50 setups) or 95-100% (ITM setups).

## Professional ELI5
Options are like insurance policies or "coupons" that let you control a stock for a fraction of the price.
* **Leverage:** Instead of buying 100 shares of a $200 stock for $20,000, you might buy one option for $500.
* **The Math:** We prefer **In-the-Money** options because they act more like the actual stock. If the stock moves $1, your option moves $\approx$ $0.70 (that's the **Delta**).

---

# V. DEFENSIVE PROTOCOLS (RISK MANAGEMENT)
**Metadata:** Topic: Capital Preservation | Author: Simon Ree | Category: Risk

> [!WARNING]
> **SIZE RISK:** Never trade a position size that causes emotional distress. If you cannot look away from the screen, your position is too large.

## Executive Summary (Expert)
* **Hard Stop-Loss:** 50% loss on option premium paid.
* **Technical Stop:** Close position if the underlying price invalidates the trend (lower low in uptrend).
* **Correlation Filter:** Use "Ronin" stocks (independent movers) to ensure diversification across industries.
* **Execution:** Use **Limit Orders** only. Target the "Mid" price between Bid and Ask.

## Professional ELI5
Risk management is the "Secret Sauce." Your job isn't to be "right"; it's to keep your account balance growing.
* **Operating Expenses:** Think of a losing trade like the electricity bill for a business—it's just a cost of doing business.
* **The Math:** If you pay $4.00 for an option, your "Mental Stop-Loss" is $2.00. If the value drops to $2.00, you close the trade immediately—no excuses.

---

# VI. OPERATIONAL WORKFLOW
**Metadata:** Topic: Daily Trading Process | Author: Simon Ree | Category: Risk

1.  **Phase Assessment:** Check S&P 500 relative to 200 SMA and 8/21 EMA crosses.
2.  **Macro Review:** Check the weekly economic calendar for high-impact reports.
3.  **Position Audit:** Review open trades against Stop-Loss and Profit Target levels.
4.  **Scanning:** Run "Bounce 2.0" scans (Volume > 500k, Cap > $1B).
5.  **Shortlist Weeding:** Remove stocks with earnings within 2 weeks or messy price action.
6.  **Strategy Match:** Select Vertical Spread vs. Naked Option based on volatility and price.
7.  **Diary Entry:** Document the "Why" and the "Entry/Exit Agreement" before clicking buy.

Would you like me to generate a specific scan criteria list for a platform like TradingView or Thinkorswim based on these rules?
