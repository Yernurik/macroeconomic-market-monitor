# Macroeconomic Market Monitor & Analytics Dashboard 

A quantitative research tool designed to fetch, process, and visualize global macroeconomic data (e.g., inflation, interest rates, central bank liquidity, and market sentiment metrics). This repository serves as an analytical dashboard to support macro-driven trading strategies and regime-shifting analysis.

## Key Features
*   **Automated Data Pipeline:** Multi-source pipeline extracting data from financial APIs (such as FRED, Alpha Vantage, or Yahoo Finance).
*   **Macro Indicator Suite:** Tracking and normalizing critical market drivers:
    *   **Monetary Policy & Liquidity:** Central bank interest rates, balance sheets, and yield curve spreads (e.g., 10Y-2Y).
    *   **Inflation & Growth:** Consumer Price Index (CPI), GDP growth rates, and manufacturing indexes.
    *   **Market Sentiment & Risk:** High-frequency risk indicators and volatility metrics.
*   **Data Visualization:** Interactive charting and dashboards to identify regime shifts and macroeconomic anomalies.

---

## Tech Stack

*   **Language:** Python 3.x
*   **Data Gathering:** `requests`, `pandas-datareader`
*   **Data Engineering:** `pandas`, `numpy` (for normalization, rolling z-scores, and statistical metrics)
*   **Visualization:** `matplotlib`, `seaborn` or `plotly`

---

## Getting Started

### Prerequisites
Install the required libraries using pip:
```bash
pip install pandas numpy requests matplotlib seaborn python-dotenv# macroeconomic-market-monitor
An analytical quantitative tool to fetch, process, and visualize global macroeconomic data to support macro-driven trading strategies.
