import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

# 1. Page Setup
st.set_page_config(page_title="AlphaBeta Pro", page_icon="📊", layout="wide")

st.title("📊 Professional Beta Calculator")
st.markdown("Calculate the volatility of any stock relative to a market benchmark.")

# 2. Sidebar Inputs
st.sidebar.header("Calculation Settings")
ticker = st.sidebar.text_input("Stock Ticker (e.g., RELIANCE.NS, AAPL)", "RELIANCE.NS").upper()
benchmark = st.sidebar.selectbox("Market Benchmark", ["^GSPC", "^NSEI", "^BSESN", "^IXIC"], index=0)

# Date Selection - Defaulting to last 3 years to ensure we skip holidays/weekends
col1, col2 = st.sidebar.columns(2)
start_date = col1.date_input("Start Date", datetime.now() - timedelta(days=365*3))
end_date = col2.date_input("End Date", datetime.now())

# 3. Execution
if st.sidebar.button("Run Analysis"):
    with st.spinner('Fetching data from Yahoo Finance...'):
        try:
            # IMPORTANT: auto_adjust=False fixes the KeyError: 'Adj Close' bug
            data = yf.download([ticker, benchmark], start=start_date, end=end_date, auto_adjust=False)
            
            # Check if the dataframe has the required columns
            if 'Adj Close' in data.columns:
                prices = data['Adj Close']
                
                # Check if the specific ticker exists in the downloaded data
                if ticker not in prices.columns:
                    st.error(f"⚠️ Ticker '{ticker}' not found. Did you forget '.NS' for Indian stocks?")
                else:
                    # Drop missing values (this skips Jan 1st and weekends automatically)
                    returns = prices.pct_change().dropna()
                    
                    if returns.empty:
                        st.warning("📭 No trading data found for this date range. Markets might have been closed.")
                    else:
                        # Beta Calculation: Covariance / Variance
                        covariance = returns.cov().iloc[0, 1]
                        market_variance = returns[benchmark].var()
                        beta = covariance / market_variance
                        
                        # 4. Display Results
                        st.divider()
                        m1, m2, m3 = st.columns(3)
                        m1.metric(label="Calculated Beta", value=f"{beta:.2f}")
                        m2.metric(label="Benchmark", value="S&P 500" if benchmark=="^GSPC" else "NIFTY 50")
                        m3.metric(label="Trading Days Analyzed", value=len(returns))
                        
                        # 5. Charts
                        st.subheader(f"Price Performance: {ticker} vs {benchmark}")
                        # Normalize to 100 to compare different price scales
                        normalized_df = (prices / prices.iloc[0]) * 100
                        st.
