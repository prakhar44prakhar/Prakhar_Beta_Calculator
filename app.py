import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from scipy import stats

# 1. Dictionary for Smart Global Lookup
INDEX_MAP = {
    ".BO": "^BSESN",   # India - BSE Sensex
    ".NS": "^NSEI",   # India - NSE Nifty 50
    ".SI": "^STI",    # Singapore - STI
    ".HK": "^HSI",    # Hong Kong - Hang Seng
}

st.title("📊 Excel-Style Beta Slope Calculator")

ticker_input = st.sidebar.text_input("Ticker (e.g., RELIANCE.BO, AAPL)", "RELIANCE.BO").upper()

# Auto-detect Benchmark
default_index = "^GSPC"
for suffix, idx in INDEX_MAP.items():
    if ticker_input.endswith(suffix):
        default_index = idx
        break

benchmark = st.sidebar.text_input("Benchmark Index", default_index)

if st.sidebar.button("Calculate"):
    try:
        # Fetch data (3 years for a stable slope)
        raw_data = yf.download([ticker_input, benchmark], period="3y", auto_adjust=False)['Adj Close']
        
        # --- THE EXCEL-STYLE FIX ---
        # 1. Calculate fractional change (like Excel daily returns)
        returns = raw_data.pct_change()
        
        # 2. Use dropna() to remove the first row AND any mismatched holiday/missing data rows
        # This ensures x and y are always paired and finite
        clean_returns = returns.dropna()
        
        # Separate the columns for the slope formula
        y = clean_returns[ticker_input] # The Stock
        x = clean_returns[benchmark]    # The Index
        
        # 3. Use the scipy slope formula (same as Excel SLOPE function)
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
        
        # UI Metrics
        st.divider()
        m1, m2 = st.columns(2)
        m1.metric("Calculated Beta (Slope)", f"{slope:.2f}")
        m2.metric("Data Points (n)", len(clean_returns))
        
        # Charting the % Change (Volatility)
        st.subheader("Daily % Change Comparison")
        st.line_chart(clean_returns)
        
    except Exception as e:
        st.error(f"Analysis failed: {e}")
