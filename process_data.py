import pandas as pd
import os

def process_stock(symbol="TCS.NS"):
    file_path = os.path.join("data", f"{symbol}.csv")
    df = pd.read_csv(file_path)

    # Convert Date
    df["Date"] = pd.to_datetime(df["Date"])

    # Handle missing values
    df.ffill(inplace=True)

    # Daily Return
    df["Daily Return"] = (df["Close"] - df["Open"]) / df["Open"]

    # 7-day moving average
    df["MA7"] = df["Close"].rolling(window=7).mean()

    # Volatility (standard deviation of last 7 days)
    df["Volatility"] = df["Close"].rolling(window=7).std()

    # Sentiment Index (simple logic)
    df["Sentiment"] = (df["Daily Return"] * 100) - df["Volatility"]
    
    # 52-week high/low
    df["52W High"] = df["Close"].rolling(window=252).max()
    df["52W Low"] = df["Close"].rolling(window=252).min()

    # Save cleaned file
    df.to_csv(file_path, index=False)

    print(f"Processed {symbol}")

if __name__ == "__main__":
    process_stock("TCS.NS")
    process_stock("INFY.NS")
    process_stock("HDFCBANK.NS")
    process_stock("LT.NS")
    process_stock("WIPRO.NS")