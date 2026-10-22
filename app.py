import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from trading_strategy import (
    calculate_moving_averages,
    get_stock_data,
    identify_golden_cross,
    implement_strategy,
    summarize_results,
)


@st.cache_data
def load_strategy_data():
    data = get_stock_data("MSFT")
    data = calculate_moving_averages(data)
    data = identify_golden_cross(data)
    trades = implement_strategy(data)
    summary = summarize_results(trades)
    return data, trades, summary


def format_float(value, decimals=2):
    if pd.isna(value):
        return "N/A"
    return f"{value:.{decimals}f}"


def render_price_chart(data, trades):
    data_plot = data.reset_index().rename(columns={"index": "Date"})

    buy_points = data_plot[data_plot["GoldenCross"] == True].copy()
    buy_points = buy_points[["Date", "Close"]].rename(columns={"Close": "Price"})

    sell_points = trades[["SellDate", "SellPrice"]].dropna().copy()
    sell_points = sell_points.rename(columns={"SellDate": "Date", "SellPrice": "Price"})

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=data_plot["Date"],
            y=data_plot["Close"],
            mode="lines",
            name="Stock Price",
            line={"color": "#1f77b4", "width": 2},
        )
    )
    fig.add_trace(
        go.Scatter(
            x=data_plot["Date"],
            y=data_plot["MA50"],
            mode="lines",
            name="Short-term MA (50)",
            line={"color": "#ff7f0e", "width": 2},
        )
    )
    fig.add_trace(
        go.Scatter(
            x=data_plot["Date"],
            y=data_plot["MA200"],
            mode="lines",
            name="Long-term MA (200)",
            line={"color": "#2ca02c", "width": 2},
        )
    )
    fig.add_trace(
        go.Scatter(
            x=buy_points["Date"],
            y=buy_points["Price"],
            mode="markers",
            name="Buy Signal",
            marker={"color": "#28a745", "size": 10, "symbol": "circle"},
        )
    )
    fig.add_trace(
        go.Scatter(
            x=sell_points["Date"],
            y=sell_points["Price"],
            mode="markers",
            name="Sell Signal",
            marker={"color": "#dc3545", "size": 10, "symbol": "circle"},
        )
    )

    fig.update_layout(
        title="MSFT Price and Moving Averages",
        xaxis_title="Date",
        yaxis_title="Price",
        template="plotly_white",
        legend={"orientation": "h", "yanchor": "bottom", "y": 1.02, "xanchor": "left", "x": 0},
        hovermode="x unified",
    )

    st.plotly_chart(fig, use_container_width=True)


def render_statistics(summary):
    st.subheader("Overall Trade Statistics")
    cols = st.columns(4)
    cols[0].metric("Total Trades", summary["TotalTrades"])
    cols[1].metric("Winning Trades", summary["WinningTrades"])
    cols[2].metric("Losing Trades", summary["LosingTrades"])
    cols[3].metric("Win Rate", f"{summary['WinRate']:.2f}%")

    cols2 = st.columns(4)
    cols2[0].metric("Average Profit", f"{summary['AverageProfitPct']:.2f}%")
    cols2[1].metric("Average Holding Days", f"{summary['AverageHoldingDays']:.2f}")
    cols2[2].metric("Target Reached", summary["TargetReached"])
    cols2[3].metric("Max Holding Period", summary["MaxHoldingPeriod"])


def render_detailed_trades(trades):
    st.subheader("Detailed Trade Record")
    display_df = trades.copy()
    if not display_df.empty:
        display_df["BuyDate"] = display_df["BuyDate"].dt.strftime("%Y-%m-%d")
        display_df["SellDate"] = display_df["SellDate"].dt.strftime("%Y-%m-%d")
        display_df["BuyPrice"] = display_df["BuyPrice"].map(lambda x: format_float(x, 2))
        display_df["SellPrice"] = display_df["SellPrice"].map(lambda x: format_float(x, 2))
        display_df["ProfitPct"] = display_df["ProfitPct"].map(lambda x: format_float(x, 2) + "%")
    st.dataframe(display_df, use_container_width=True, hide_index=True)


def main():
    st.set_page_config(page_title="Trading Strategy Dashboard", layout="wide")
    st.title("MSFT Trading Strategy Dashboard")

    data, trades, summary = load_strategy_data()

    page = st.sidebar.radio(
        "Navigation",
        ["Price Chart", "Trade Statistics", "Detailed Trades"],
        index=0,
    )

    if page == "Price Chart":
        render_price_chart(data, trades)
    elif page == "Trade Statistics":
        render_statistics(summary)
    else:
        render_detailed_trades(trades)


if __name__ == "__main__":
    main()
