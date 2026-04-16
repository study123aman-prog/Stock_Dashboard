import yfinance as yf
import pandas as pd
import os

def fetch_stock(symbol="TCS.NS"):
    df = yf.download(symbol, period="6mo")


    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.droplevel(1)

    df.reset_index(inplace=True)


    file_path = os.path.join("data", f"{symbol}.csv")
    df.to_csv(file_path, index=False)

    print(f"Saved data for {symbol}")

if __name__ == "__main__":
    fetch_stock("TCS.NS")
    fetch_stock("INFY.NS")
    fetch_stock("HDFCBANK.NS")
    fetch_stock("LT.NS")
    fetch_stock("WIPRO.NS")
