# Python Financial Data Toolkit 🐍📊

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A collection of Python scripts designed for fetching, cleaning, and analyzing financial data from various sources, with an initial focus on cryptocurrency and stock market APIs.

---

## 🎯 Project Goals

* **Data Acquisition:** Provide robust and easy-to-use scripts for fetching historical and real-time financial data (OHLCV, trades, etc.).
* **Modularity:** Create reusable functions and classes for common data processing tasks.
* **Extensibility:** Allow easy integration with different data sources (exchanges, financial APIs) and analysis libraries.
* **Reliability:** Implement proper error handling, rate limiting considerations, and data validation.

---

## ✨ Features (Current)

* **Historical OHLCV Fetcher (`fetch_data.py`):**
    * Fetches historical Open, High, Low, Close, Volume (OHLCV) data for cryptocurrencies.
    * Uses the powerful `ccxt` library to support hundreds of exchanges (defaults to Binance).
    * Handles fetching in batches for large historical data requests.
    * Includes basic rate limit awareness (`enableRateLimit`).
    * Supports various timeframes (e.g., `1m`, `5m`, `1h`, `1d`).
    * Allows fetching data from a specific start date or just the most recent candles.
    * Command-line interface for easy execution.
    * Option to save fetched data to a CSV file.

---

## 🛠️ Setup

1.  **Clone the Repository:**
    ```bash
    git clone [https://github.com/learnonlye/python-financial-data-toolkit.git](https://github.com/learnonlye/python-financial-data-toolkit.git)
    cd python-financial-data-toolkit
    ```

2.  **Create a Virtual Environment (Recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

---

## ▶️ Usage Example (`fetch_data.py`)

The `fetch_data.py` script can be run from your terminal.

**Command Structure:**

```bash
python fetch_data.py <SYMBOL> [options]
