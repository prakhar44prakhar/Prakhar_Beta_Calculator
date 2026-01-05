import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

# 1. Page Configuration
st.set_page_config(page_title="AlphaBeta Pro", page_icon="📊", layout="wide")

# 2. Sidebar for Inputs (Keeps the main page clean)
st.sidebar.header("Settings")
ticker = st.sidebar.text_input("Stock Ticker", "AAPL").upper()
market = st.sidebar.selectbox("Benchmark", ["^GSPC", "^IXIC", "^DJI"], index=0)

# Date Selection
col1, col2 = st.sidebar.columns(2)
start_date = col1.date_input("Start Date", datetime.now() - timedelta(days=365*3))
end_date = col2.date_input("End Date", datetime.now())

# 3. Fetch Company Info
stock_obj = yf.Ticker(ticker)
try:
    info = stock_obj.info
    st.title(f"{info.get('longName', ticker)} Beta Analysis")
    st.caption(f"{info.get('sector', '')} | {info.get('industry', '')} | {info.get('address1', '')}")
except:
    st.title(f"{ticker} Beta Analysis")

# 4. Calculation Logic
if st.sidebar.button("Run Analysis"):
    with st.spinner('Analyzing market correlations...'):
        # Fetch data
        data = yf.download([ticker, market], start=start_date, end=end_date)["Adj Close"]
        
        if len(data.columns) >= 2:
            returns = data.pct_change().dropna()
            
            # Beta Calculation
            cov = returns.cov().iloc[0, 1]
            var = returns[market].var()
            beta = cov / var
            
            # Display Metrics in Columns
            m1, m2, m3 = st.columns(3)
            m1.metric("Beta Score", f"{beta:.2f}")
            m2.metric("Market", "S&P 500" if market=="^GSPC" else market)
            m3.metric("Data Points", len(returns))
            
            # Visuals
            st.subheader("Price Movement Comparison")
            # Normalize data to 100 for comparison
            norm_data = (data / data.iloc[0]) * 100
            st.line_chart(norm_data)
            
            # Description
            st.info(f"**Interpretation:** A beta of {beta:.2f} indicates that for every 1% move in the {market}, {ticker} is expected to move {beta:.2f}%.")
        else:
            st.error("Error: Ticker not found or insufficient data for this date range.")

# 5. Footer (Helps with Search Engine Optimization)
st.markdown("---")
st.write(f"© 2026 YourName Financial Tools | Beta Calculator for {ticker}")
