
import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(
    page_title="US Stock AI",
    page_icon="📈",
    layout="wide"
)

st.title("📈 US Stock AI")
st.write("American Stock Technical Analyzer")
st.caption("Educational analysis - Not financial advice")

symbol = st.text_input(
    "Stock Symbol",
    value="AAPL"
).strip().upper()

period = st.selectbox(
    "Analysis Period",
    ["3mo", "6mo", "1y", "2y"],
    index=2
)

if st.button("Analyze Stock", type="primary"):
    if not symbol:
        st.warning("Please enter a stock symbol.")
        st.stop()

    try:
        with st.spinner("Downloading stock data..."):
            data = yf.download(
                symbol,
                period=period,
                interval="1d",
                auto_adjust=True,
                progress=False,
                threads=False
            )

        if data.empty:
            st.error("No data found for this symbol.")
            st.stop()

        close = data["Close"].squeeze()
        close = pd.to_numeric(
            close, errors="coerce"
        ).dropna()

        if len(close) < 50:
            st.warning("Not enough historical data.")
            st.stop()

        # Moving averages
        ma20 = close.rolling(20).mean()
        ma50 = close.rolling(50).mean()

        # RSI calculation
        delta = close.diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)

        avg_gain = gain.ewm(
            alpha=1/14,
            adjust=False,
            min_periods=14
        ).mean()

        avg_loss = loss.ewm(
            alpha=1/14,
            adjust=False,
            min_periods=14
        ).mean()

        rs = avg_gain / avg_loss.replace(0, float("nan"))
        rsi = 100 - (100 / (1 + rs))
        rsi = rsi.mask(
            (avg_loss == 0) & (avg_gain > 0), 100
        )
        rsi = rsi.mask(
            (avg_loss == 0) & (avg_gain == 0), 50
        )

        # MACD calculation
        ema12 = close.ewm(
            span=12, adjust=False
        ).mean()
        ema26 = close.ewm(
            span=26, adjust=False
        ).mean()

        macd = ema12 - ema26
        signal = macd.ewm(
            span=9, adjust=False
        ).mean()

        last_price = float(close.iloc[-1])
        last_rsi = float(rsi.iloc[-1])
        last_ma50 = float(ma50.iloc[-1])
        last_macd = float(macd.iloc[-1])
        last_signal = float(signal.iloc[-1])

        st.success("Stock data loaded successfully!")

        st.caption(
            f"Latest trading date: "
            f"{close.index[-1].strftime('%Y-%m-%d')}"
        )

        st.metric(
            "Latest Closing Price",
            f"${last_price:,.2f}"
        )

        st.metric(
            "RSI (14)",
            f"{last_rsi:.2f}"
        )

        # Price chart
        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=close.index,
            y=close.to_numpy(),
            mode="lines",
            name="Closing Price",
            line=dict(color="#2563eb", width=3)
        ))

        fig.add_trace(go.Scatter(
            x=ma20.index,
            y=ma20.to_numpy(),
            mode="lines",
            name="MA 20"
        ))

        fig.add_trace(go.Scatter(
            x=ma50.index,
            y=ma50.to_numpy(),
            mode="lines",
            name="MA 50"
        ))

        fig.update_layout(
            title=f"{symbol} Price Chart",
            xaxis_title="Date",
            yaxis_title="Price (USD)",
            height=450,
            hovermode="x unified",
            margin=dict(l=10, r=10, t=50, b=30)
        )

        st.plotly_chart(fig, width="stretch")

        # RSI chart
        rsi_fig = go.Figure()

        rsi_fig.add_trace(go.Scatter(
            x=rsi.index,
            y=rsi.to_numpy(),
            mode="lines",
            name="RSI"
        ))

        rsi_fig.add_hline(
            y=70, line_dash="dash",
            line_color="red"
        )
        rsi_fig.add_hline(
            y=30, line_dash="dash",
            line_color="green"
        )

        rsi_fig.update_layout(
            title="RSI Indicator",
            yaxis_range=[0, 100],
            height=300
        )

        st.plotly_chart(rsi_fig, width="stretch")

        # Technical assessment
        st.subheader("Technical Assessment")

        if last_price > last_ma50:
            st.success("Price is above the 50-day average.")
        else:
            st.warning("Price is below the 50-day average.")

        if last_rsi > 70:
            st.warning("RSI: Potentially overbought.")
        elif last_rsi < 30:
            st.info("RSI: Potentially oversold.")
        else:
            st.info("RSI: Neutral range.")

        if last_macd > last_signal:
            st.success("MACD: Positive momentum.")
        else:
            st.warning("MACD: Negative momentum.")

        st.caption(
            "Indicators are not guaranteed buy/sell signals. "
            "Prices may be delayed or adjusted."
        )

    except Exception as e:
        st.error(f"Analysis error: {e}")
