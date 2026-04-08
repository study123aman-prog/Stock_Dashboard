from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import os
import math

app = FastAPI(title="Stock Market API", version="1.0")

# CORS must be added RIGHT AFTER app is created
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_FOLDER = "data"

def load_data(symbol):
    file_path = os.path.join(DATA_FOLDER, f"{symbol}.csv")
    if not os.path.exists(file_path):
        return None
    return pd.read_csv(file_path)

def safe_value(val):
    if val is None or (isinstance(val, float) and math.isnan(val)):
        return None
    return round(float(val), 2)

@app.get("/")
def home():
    return {"message": "Stock API Running ✅"}

@app.get("/companies")
def get_companies():
    files = os.listdir(DATA_FOLDER)
    symbols = [f.replace(".csv", "") for f in files if f.endswith(".csv")]
    return {"companies": symbols}

@app.get("/data/{symbol}")
def get_data(symbol: str):
    df = load_data(symbol)
    if df is None:
        return {"error": f"No data found for {symbol}"}
    df["Date"] = pd.to_datetime(df["Date"])
    df = df[["Date", "Open", "Close", "Daily Return", "MA7", "Volatility", "Sentiment"]]
    last_30 = df.sort_values("Date").tail(30)
    return last_30.to_dict(orient="records")

@app.get("/summary/{symbol}")
def summary(symbol: str):
    df = load_data(symbol)
    if df is None:
        return {"error": f"No data found for {symbol}"}
    return {
        "52W High": safe_value(df["52W High"].max() if "52W High" in df.columns else None),
        "52W Low":  safe_value(df["52W Low"].min()  if "52W Low"  in df.columns else None),
        "Average Close":      safe_value(df["Close"].mean()),
        "Latest Volatility":  safe_value(df["Volatility"].dropna().iloc[-1] if not df["Volatility"].dropna().empty else None),
        "Latest Sentiment":   safe_value(df["Sentiment"].dropna().iloc[-1]  if not df["Sentiment"].dropna().empty  else None),
    }

@app.get("/compare")
def compare(symbol1: str, symbol2: str):
    df1, df2 = load_data(symbol1), load_data(symbol2)
    if df1 is None or df2 is None:
        return {"error": "One or both symbols not found"}
    return {
        symbol1: {"Latest Price": safe_value(df1["Close"].iloc[-1]), "Volatility": safe_value(df1["Volatility"].dropna().iloc[-1])},
        symbol2: {"Latest Price": safe_value(df2["Close"].iloc[-1]), "Volatility": safe_value(df2["Volatility"].dropna().iloc[-1])},
    }

@app.get("/correlation")
def correlation(symbol1: str, symbol2: str):
    df1, df2 = load_data(symbol1), load_data(symbol2)
    if df1 is None or df2 is None:
        return {"error": "One or both symbols not found"}
    df1["Date"] = pd.to_datetime(df1["Date"])
    df2["Date"] = pd.to_datetime(df2["Date"])
    merged = pd.merge(df1, df2, on="Date", suffixes=("_1", "_2"))
    corr = merged["Close_1"].corr(merged["Close_2"])
    return {"symbol1": symbol1, "symbol2": symbol2, "correlation": safe_value(corr)}