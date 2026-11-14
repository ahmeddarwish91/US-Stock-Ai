import streamlit as st
import yfinance as yf

st.set_page_config(page_title="US Stock AI")

st.title("US Stock AI")
st.write("American Stock Analyzer")

symbol = st.text_input("Stock Symbol", "AAPL")

if st.button("Analyze Stock"):
    try:
        data = yf.download(
            symbol,
            period="3mo",
            auto_adjust=True,
            progress=False
        )

        if data.empty:
            st.error("No data found")
        else:
            st.success("Data loaded successfully")
            st.line_chart(data["Close"])

    except Exception as e:
        st.error(str(e))
