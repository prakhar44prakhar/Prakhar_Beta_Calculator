import streamlit as st
import yfinance as yf
import pandas as pd
from scipy import stats
from datetime import datetime, timedelta

# 1. Global Index Mapping Dictionary
# Maps Yahoo Finance suffixes to their primary benchmark indices
INDEX_MAP = {
    ".BO": "^BSESN",   # India (BSE Sensex)
    ".NS": "^NSEI",   # India (NSE Nifty 50)
    ".SI": "^STI",    # Singapore (Straits Times Index)
    ".HK": "^HSI",    # Hong Kong (Hang Seng)
    ".L":  "^FTSE",   # UK (FTSE 100)
    ".T":  "^N225",   # Japan (Nikkei 225)
    ".DE": "^GDAXI",  # Germany (DAX)
    ".AX": "^AXJO",   # Australia (ASX 200)
    ".TO": "^GSPTSE", # Canada (TSX Composite)
}

st.set_page_config(page_title="Global Beta Slope Engine", layout="wide")
st.title("📉 Global Beta Slope Calculator")

# 2. Input Logic
ticker_input = st.sidebar.text_input("Enter Ticker (e.g., RELIANCE.BO, AAPL, D05.SI)", "RELIANCE.BO").upper()

# Auto-detect Benchmark
selected_benchmark = "^GSPC" # Default to S&P 500 for US or unknown
for suffix, index in INDEX_MAP.items():
    if ticker_input.endswith(suffix):
        selected_benchmark = index
        break

benchmark = st.sidebar.text_input("Benchmark Index", selected_benchmark)
period = st.sidebar.selectbox("Analysis Period", ["1y", "2y", "5y"], index=1)

if st.sidebar.button("Calculate Beta Slope"):
    try:
        # Download Data
        # auto_adjust=False is required to keep 'Adj Close'
        data = yf.download([ticker_input, benchmark], period=period, auto_adjust=False)['Adj Close']
        
        if data.empty or ticker_input not in data.columns:
            st.error("Data not found. Please check your ticker suffix.")
        else:
            # 3. Percentage Change Calculation
            returns = data.pct_change().dropna()
            
            # 4. Slope Calculation (Linear Regression)
            # y = Stock Returns, x = Market Returns
            x = returns[benchmark].values
            y = returns[ticker_input].values
            
            # linregress returns: slope, intercept, r_value, p_value, std_err
            slope, intercept, r_val, p_val, std_err = stats.linregress(x, y)
            
            # 5. UI Display
            st.divider()
            col1, col2, col3 = st.columns(3)
            
            col1.metric("Beta (Slope)", f"{slope:.2f}")
            col2.metric("R-Squared (Fit)", f"{r_val**2:.2f}")
            col3.metric("Benchmark Used", benchmark)
            
            # Scatter Plot with Regression Line
            st.subheader("Returns Regression: Stock vs Market")
            import matplotlib.pyplot as plt
            import seaborn as sns
            
            fig, ax = plt.subplots()
            sns.regplot(x=x, y=y, ax=ax, scatter_kws={'alpha':0.3}, line_kws={'color':'red'})
            ax.set_xlabel(f"{benchmark} Daily Returns")
            ax.set_ylabel(f"{ticker_input} Daily Returns")
            st.pyplot(fig)
            
            st.info(f"**Interpretation:** A slope of {slope:.2f} means for every 1% the {benchmark} moves, {ticker_input} is expected to move {slope:.2f}%.")

    except Exception as e:
        st.error(f"Execution Error: {e}")
