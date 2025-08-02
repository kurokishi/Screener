import yfinance as yf
import concurrent.futures
from functools import lru_cache
import time

# Cache with 10-minute expiration (600 seconds) to reduce API calls
@lru_cache(maxsize=128, typed=True)
def get_cached_ticker(ticker: str, expiration: int = 600) -> yf.Ticker:
    """Cache mechanism with expiration for Ticker objects"""
    current_time = time.time()
    if not hasattr(get_cached_ticker, "cache_times"):
        get_cached_ticker.cache_times = {}
    
    if (ticker in get_cached_ticker.cache_times and 
        current_time - get_cached_ticker.cache_times[ticker] < expiration):
        return yf.Ticker(ticker)
    
    # Refresh cache
    ticker_obj = yf.Ticker(ticker)
    get_cached_ticker.cache_times[ticker] = current_time
    return ticker_obj

def fetch_stock_info(ticker: str) -> dict:
    """Fetch comprehensive stock data with error handling and fallbacks"""
    try:
        yf_ticker = get_cached_ticker(ticker + ".JK")
        info = yf_ticker.info
        
        # Get price with multiple fallbacks
        price = (info.get("currentPrice") or 
                info.get("regularMarketPrice") or 
                info.get("previousClose") or 
                info.get("open") or 0)
        
        # Calculate Free Cash Flow if not available
        fcf = info.get("freeCashflow")
        if not fcf:
            op_cashflow = info.get("operatingCashflow", 0)
            capex = abs(info.get("capitalExpenditures", 0))
            fcf = op_cashflow - capex if op_cashflow and capex else None

        # Handle missing values and calculate metrics
        roe = info.get("returnOnEquity")
        roe = roe * 100 if roe else None
        
        eps_growth = info.get("earningsQuarterlyGrowth")
        eps_growth = eps_growth * 100 if eps_growth else None
        
        der = info.get("debtToEquity")
        der = der / 100 if der else None  # Convert to decimal
        
        # Get additional fundamental data
        dividend_yield = info.get("dividendYield", 0) * 100 if info.get("dividendYield") else 0
        current_ratio = info.get("currentRatio")
        quick_ratio = info.get("quickRatio")
        profit_margin = info.get("profitMargins", 0) * 100 if info.get("profitMargins") else None
        beta = info.get("beta")
        
        return {
            "ticker": ticker,
            "price": price,
            "PER": info.get("trailingPE"),
            "PBV": info.get("priceToBook"),
            "ROE": roe,
            "DER": der,
            "EPS_Growth": eps_growth,
            "FCF": fcf,
            "dividend_yield": dividend_yield,
            "current_ratio": current_ratio,
            "quick_ratio": quick_ratio,
            "profit_margin": profit_margin,
            "beta": beta,
            "market_cap": info.get("marketCap"),
            "volume": info.get("volume"),
            "currency": info.get("currency", "IDR"),
            "last_updated": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
    except Exception as e:
        print(f"Error fetching data for {ticker}: {str(e)}")
        return {
            "ticker": ticker,
            "error": str(e)
        }

def get_stock_data(tickers: list, max_workers: int = 8) -> dict:
    """
    Fetch data for multiple stocks concurrently with enhanced error handling
    
    Parameters:
    tickers (list): List of stock tickers (without .JK suffix)
    max_workers (int): Number of concurrent threads
    
    Returns:
    dict: {ticker: data_dict}
    """
    results = {}
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_ticker = {
            executor.submit(fetch_stock_info, ticker): ticker 
            for ticker in tickers
        }
        
        for future in concurrent.futures.as_completed(future_to_ticker):
            ticker = future_to_ticker[future]
            try:
                results[ticker] = future.result()
            except Exception as e:
                results[ticker] = {"ticker": ticker, "error": str(e)}
    
    return results
