import pandas as pd
import yfinance as yf
import streamlit as st


@st.cache_data(show_spinner=False)
def load_stock_data(
    ticker: str | None = None,
    start: str = "2015-01-01",
    end: str | None = None,
    github_url: str | None = None,
    sheet_name: int | str | None = 0,
) -> pd.DataFrame:
    """
    Load price data either from yfinance (default) or from a GitHub-hosted file you uploaded.
    - github_url: raw link to CSV/XLSX on GitHub. If provided, it overrides yfinance.
    """
    if github_url:
        loader = pd.read_excel if github_url.lower().endswith(("xlsx", "xls")) else pd.read_csv
        df = loader(github_url, sheet_name=sheet_name)
        date_col = next((c for c in df.columns if str(c).lower() in ("date", "datetime", "time")), None)
        if date_col:
            df[date_col] = pd.to_datetime(df[date_col])
            df = df.sort_values(date_col).set_index(date_col)
        return df.dropna(how="all")
    if not ticker:
        return pd.DataFrame()
    df = yf.download(ticker, start=start, end=end, auto_adjust=True, progress=False)
    return df.dropna()


def calculate_indicators(df: pd.DataFrame, short: int = 20, long: int = 50, rsi_window: int = 14) -> pd.DataFrame:
    """
    Add SMA/EMA pairs and RSI to the DataFrame.
    """
    data = df.copy()
    data["SMA_Short"] = data["Close"].rolling(short, min_periods=short).mean()
    data["SMA_Long"] = data["Close"].rolling(long, min_periods=long).mean()
    data["EMA_Short"] = data["Close"].ewm(span=short, adjust=False).mean()
    data["EMA_Long"] = data["Close"].ewm(span=long, adjust=False).mean()

    delta = data["Close"].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(rsi_window, min_periods=rsi_window).mean()
    avg_loss = loss.rolling(rsi_window, min_periods=rsi_window).mean()
    rs = avg_gain / avg_loss
    data["RSI"] = 100 - (100 / (1 + rs))
    return data


def rating_signal(df: pd.DataFrame) -> str:
    """
    Simple signal:
    - Bullish: short SMA > long SMA and RSI < 70
    - Bearish: short SMA < long SMA and RSI > 30
    - Neutral: otherwise
    """
    latest = df.dropna().iloc[-1]
    if latest["SMA_Short"] > latest["SMA_Long"] and latest["RSI"] < 70:
        return "Bullish"
    if latest["SMA_Short"] < latest["SMA_Long"] and latest["RSI"] > 30:
        return "Bearish"
    return "Neutral"
