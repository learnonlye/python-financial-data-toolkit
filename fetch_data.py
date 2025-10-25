import ccxt
import pandas as pd
import time
import argparse
from datetime import datetime

def fetch_historical_data(symbol, timeframe, start_date_str=None, limit_per_req=1000, exchange_id='binance'):
    """
    Fetches historical OHLCV data for a given symbol and timeframe from a specified exchange.

    Args:
        symbol (str): The trading pair symbol (e.g., 'BTC/USDT').
        timeframe (str): The timeframe for the candles (e.g., '1m', '1h', '1d').
        start_date_str (str, optional): The start date in 'YYYY-MM-DD' format. 
                                        If None, fetches the most recent data. Defaults to None.
        limit_per_req (int, optional): Number of candles to fetch per API request. Defaults to 1000.
        exchange_id (str, optional): The ID of the exchange (e.g., 'binance', 'kraken'). Defaults to 'binance'.

    Returns:
        pandas.DataFrame: DataFrame containing OHLCV data, or None if fetching fails.
    """
    try:
        # Initialize the exchange using ccxt
        exchange_class = getattr(ccxt, exchange_id)
        exchange = exchange_class({'enableRateLimit': True}) # Enable ccxt's built-in rate limiter
        print(f"Using exchange: {exchange.name}")

        # Convert start date string to milliseconds timestamp if provided
        since = None
        if start_date_str:
            try:
                # Assuming YYYY-MM-DD format, convert to UTC midnight timestamp
                start_dt = datetime.strptime(start_date_str, '%Y-%m-%d')
                since = int(start_dt.timestamp() * 1000)
                print(f"Starting data fetch from: {start_dt.strftime('%Y-%m-%d')}")
            except ValueError:
                print("Invalid date format. Please use YYYY-MM-DD. Fetching recent data instead.")

        all_ohlcv = []
        print(f"Fetching historical {timeframe} data for {symbol}...")

        # Loop to fetch data in batches if fetching historical data
        fetch_limit = limit_per_req if since else limit_per_req # Fetch only 'limit' if no start date

        while True:
            try:
                # Use 'since' if fetching historical, otherwise fetch most recent 'limit' candles
                params = {'limit': fetch_limit}
                current_fetch_since = since if since else None # Avoid sending since=None explicitly if fetching recent

                print(f"Requesting {fetch_limit} candles{' since ' + str(pd.to_datetime(current_fetch_since, unit='ms')) if current_fetch_since else ' (most recent)'}...")
                
                ohlcv = exchange.fetch_ohlcv(symbol, timeframe, since=current_fetch_since, limit=fetch_limit, params=params)

                if not ohlcv:
                    print("No more data returned or empty response.")
                    break

                print(f"Received {len(ohlcv)} candles.")
                all_ohlcv.extend(ohlcv)

                # If we're fetching historical data, update the 'since' timestamp
                if since:
                    last_timestamp_ms = ohlcv[-1][0]
                    # Calculate next timestamp: last candle's time + timeframe duration
                    next_since = last_timestamp_ms + exchange.parse_timeframe(timeframe) * 1000 
                    
                    # Check if we have moved forward in time, if not, break to prevent infinite loop
                    if next_since <= since:
                        print("Timestamp did not advance, stopping fetch.")
                        break 
                    since = next_since

                    # Optional: Break if fetched data reaches current time (or close enough)
                    # if since > exchange.milliseconds():
                    #    print("Reached current time.")
                    #    break
                        
                else:
                    # If fetching recent data (no start date), only one fetch is needed
                    break

                # Respect the exchange's suggested delay between requests
                # ccxt handles basic rate limiting, this adds a small extra buffer
                time.sleep(exchange.rateLimit / 1000)

            except ccxt.RateLimitExceeded as e:
                print(f"Rate limit exceeded: {e}. Waiting for 60 seconds...")
                time.sleep(60)
            except ccxt.NetworkError as e:
                print(f"Network error: {e}. Waiting for 10 seconds...")
                time.sleep(10)
            except ccxt.ExchangeError as e:
                print(f"Exchange error: {e}. Stopping fetch.")
                break
            except Exception as e:
                print(f"An unexpected error occurred: {e}. Stopping fetch.")
                break # Stop fetching on other errors
        
        if not all_ohlcv:
            print("No data was fetched.")
            return None

        # Convert list of lists to DataFrame
        df = pd.DataFrame(all_ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        # Convert timestamp to datetime objects (UTC by default from ccxt)
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        # Remove potential duplicate timestamps if any overlap occurred during fetching
        df = df.drop_duplicates(subset='timestamp')
        # Set timestamp as the index
        df.set_index('timestamp', inplace=True)
        # Sort by timestamp just in case
        df.sort_index(inplace=True) 

        print(f"Successfully fetched {len(df)} unique candles.")
        return df

    except AttributeError:
        print(f"Error: Exchange '{exchange_id}' not found in ccxt.")
        return None
    except Exception as e:
        print(f"An error occurred during initialization: {e}")
        return None

if __name__ == "__main__":
    # --- Set up command-line argument parsing ---
    parser = argparse.ArgumentParser(description='Fetch historical OHLCV data for crypto assets.')
    parser.add_argument('symbol', type=str, help="Trading pair symbol (e.g., 'BTC/USDT')")
    parser.add_argument('-tf', '--timeframe', type=str, default='1h', 
                        help="Timeframe (e.g., '1m', '5m', '1h', '1d'). Default: '1h'")
    parser.add_argument('-s', '--startdate', type=str, default=None, 
                        help="Start date in YYYY-MM-DD format (fetches historical data). Default: None (fetches recent data)")
    parser.add_argument('-l', '--limit', type=int, default=100, 
                        help="Number of recent candles to fetch if --startdate is not used. Default: 100")
    parser.add_argument('-e', '--exchange', type=str, default='binance', 
                        help="Exchange ID (e.g., 'binance', 'kraken'). Default: 'binance'")
    parser.add_argument('-o', '--output', type=str, default=None,
                        help="Optional: Path to save the fetched data as a CSV file.")

    args = parser.parse_args()

    # --- Fetch Data ---
    # Determine limit based on whether start date is provided
    fetch_limit = 1000 if args.startdate else args.limit # Use larger limit for historical fetches
    
    historical_data = fetch_historical_data(
        symbol=args.symbol, 
        timeframe=args.timeframe, 
        start_date_str=args.startdate, 
        limit_per_req=fetch_limit, # Use 1000 for batch fetching if start date is given
        exchange_id=args.exchange
    )

    # --- Display and Save Results ---
    if historical_data is not None and not historical_data.empty:
        print("\n--- Data Summary ---")
        print(f"Symbol: {args.symbol}")
        print(f"Timeframe: {args.timeframe}")
        print(f"Data points fetched: {len(historical_data)}")
        print(f"Start Time: {historical_data.index.min()}")
        print(f"End Time: {historical_data.index.max()}")
        
        print("\nLast 5 data points:")
        print(historical_data.tail())

        # Save to CSV if output path is provided
        if args.output:
            try:
                historical_data.to_csv(args.output)
                print(f"\nData successfully saved to: {args.output}")
            except Exception as e:
                print(f"\nError saving data to CSV: {e}")
    else:
        print("\nFailed to fetch or process data.")
