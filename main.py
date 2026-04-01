from fastapi import FastAPI
import pandas as pd
import os
import math

app = FastAPI()

DATA_FOLDER = "data"

def load_data(symbol):
    file_path = os.path.join(DATA_FOLDER, f"{symbol}.csv")
    return pd.read_csv(file_path)

@app.get("/")
def home():
    return {"message": "Stock API Running"}

# 1. Companies
@app.get("/companies")
def get_companies():
    files = os.listdir(DATA_FOLDER)
    symbols = [f.replace(".csv", "") for f in files]
    return {"companies": symbols}

# 2. Last 30 days
@app.get("/data/{symbol}")
def get_data(symbol: str):
    df = load_data(symbol)
    df["Date"] = pd.to_datetime(df["Date"])

    # Select useful columns
    df = df[[
        "Date",
        "Open",
        "Close",
        "Daily Return",
        "MA7",
        "Volatility",
        "Sentiment"
    ]]

    last_30 = df.sort_values("Date").tail(30)

    return last_30.to_dict(orient="records")

# 3. Summary

@app.get("/summary/{symbol}")
def summary(symbol: str):
    df = load_data(symbol)

    def safe_value(val):
        if val is None or (isinstance(val, float) and math.isnan(val)):
            return None  # JSON safe
        return float(val)

    return {
        "52W High": safe_value(df["52W High"].max() if "52W High" in df.columns else None),
        "52W Low": safe_value(df["52W Low"].min() if "52W Low" in df.columns else None),
        "Average Close": safe_value(df["Close"].mean() if "Close" in df.columns else None),
        "Latest Volatility": safe_value(
            df["Volatility"].dropna().iloc[-1] if "Volatility" in df.columns and not df["Volatility"].dropna().empty else None
        ),
        "Latest Sentiment": safe_value(
        df["Sentiment"].dropna().iloc[-1] if "Sentiment" in df.columns and not df["Sentiment"].dropna().empty else None
        )
    }

# 4. Compare
@app.get("/compare")
def compare(symbol1: str, symbol2: str):
    df1 = load_data(symbol1)
    df2 = load_data(symbol2)

    return {
        symbol1: {
            "Latest Price": float(df1["Close"].iloc[-1]),
            "Volatility": float(df1["Volatility"].iloc[-1])
        },
        symbol2: {
            "Latest Price": float(df2["Close"].iloc[-1]),
            "Volatility": float(df2["Volatility"].iloc[-1])
        }
    }

@app.get("/correlation")
def correlation(symbol1: str, symbol2: str):
    df1 = load_data(symbol1)
    df2 = load_data(symbol2)

    # Align both datasets by Date
    df1["Date"] = pd.to_datetime(df1["Date"])
    df2["Date"] = pd.to_datetime(df2["Date"])

    merged = pd.merge(df1, df2, on="Date", suffixes=("_1", "_2"))

    corr = merged["Close_1"].corr(merged["Close_2"])

    return {
        "symbol1": symbol1,
        "symbol2": symbol2,
        "correlation": float(corr) if pd.notna(corr) else None
    }

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)