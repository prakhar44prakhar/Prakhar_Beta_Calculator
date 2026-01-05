import streamlit as st
import yfinance as yf

st.set_page_config(page_title="Free Beta Calc", layout="centered")

st.title("📈 Free Beta Calculator")
st.write("Calculate the Beta of any stock against the S&P 500.")

ticker = st.text_input("Enter Ticker (e.g., TSLA, MSFT):", "AAPL")

if st.button("Calculate"):
    try:
        # Get data for the stock and the market index (^GSPC is S&P 500)
        data = yf.download([ticker, "^GSPC"], period="3y")['Close']
        returns = data.pct_change().dropna()
        
        # Beta Formula: Covariance / Variance
        cov = returns.cov().iloc[0, 1]
        var = returns["^GSPC"].var()
        beta = cov / var
        
        st.metric(label=f"Beta for {ticker}", value=round(beta, 2))
        st.line_chart(data[ticker])
    except:
        st.error("Could not find ticker. Please try a valid symbol.")