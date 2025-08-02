import requests
import yfinance as yf

def get_stock_data(ticker):
    try:
        yf_ticker = yf.Ticker(ticker + ".JK")
        info = yf_ticker.info

        price = info.get("currentPrice") or info.get("regularMarketPrice")
        roe = info.get("returnOnEquity", 0) * 100
        per = info.get("trailingPE", 0)
        pbv = info.get("priceToBook", 0)
        eps_growth = info.get("earningsQuarterlyGrowth", 0) * 100
        debt_to_equity = info.get("debtToEquity", 0)
        fcf = info.get("freeCashflow", 0)

        return {
            "price": price,
            "PER": per,
            "PBV": pbv,
            "ROE": roe,
            "DER": debt_to_equity / 100 if debt_to_equity else 1,
            "EPS_Growth": eps_growth,
            "fcf": fcf if fcf else 1e8,
        }
    except Exception as e:
        print("Error fetching data:", e)
        return None
