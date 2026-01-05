import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

# 1. Page Configuration
st.set_page_config(page_title="Beta Calc Pro", layout="wide")
st.title("📊 Professional Beta Calculator")

# 2. Sidebar for Inputs
st.sidebar.header("Settings")
ticker = st.sidebar.text_input("Stock Ticker (e.g., RELIANCE.NS)", "RELIANCE.NS").upper()
benchmark = st.sidebar.selectbox("Benchmark", ["^GSPC", "^NSEI", "^IXIC"], index=0)

# Setting date defaults to avoid holiday errors
col1, col2 = st.sidebar.columns(2)
start_date = col1.date_input("Start Date", datetime.now() - timedelta(days=365*2))
end_date = col2.date_input("End Date", datetime.now())

# 3. Calculation Logic
if st.sidebar.button("Run Analysis"):
    try:
        # auto_adjust=False is CRITICAL to avoid the KeyError: 'Adj Close'
        data = yf.download([ticker, benchmark], start=start_date, end=end_date, auto_adjust=False)
        
        if 'Adj Close' in data.columns:
            prices = data['Adj Close']
            
            # Drop missing values automatically (handles holidays/weekends)
            returns = prices.pct_change().dropna()
            
            if ticker not in returns.columns:
                st.error(f"Ticker {ticker} not found. Did you include .NS?")
            else:
                # Beta Calculation
                cov = returns.cov().iloc[0, 1]
                var = returns[benchmark].var()
                beta = cov / var
                
                # 4. Display Results
                st.divider()
                st.metric(label=f"Beta Score for {ticker}", value=f"{beta:.2f}")
                
                st.subheader("Price Trend (Normalized)")
                # Normalize to 100 for easy comparison
                norm_df = (prices / prices.iloc[0]) * 100
                st.line_chart(norm_df)
                st.success("Analysis Complete")
        else:
            st.error("Could not find 'Adj Close' data. Try a different date range.")
            
    except Exception as e:
        st.error(f"An error occurred: {e}")

# 5. Footer
st.divider()
st.caption("Data sourced from Yahoo Finance. Dates with no trading are automatically skipped.")
