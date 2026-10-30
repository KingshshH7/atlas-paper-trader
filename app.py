import random
from datetime import datetime, timezone

import streamlit as st

st.set_page_config(page_title="ATLAS AI — Paper Trader", page_icon="🤖", layout="centered")

MARKETS = {
    "Bitcoin (BTC)": {"start": 65000.0, "vol": 0.012},
    "EUR/USD": {"start": 1.0850, "vol": 0.0025},
    "Apple (AAPL)": {"start": 225.0, "vol": 0.008},
}
STARTING_CASH = 10_000.0
POSITION_FRACTION = 0.10
STOP_LOSS = 0.02
TAKE_PROFIT = 0.04
MAX_DRAWDOWN = 0.03

def initialise():
    if "cash" not in st.session_state:
        st.session_state.cash = STARTING_CASH
        st.session_state.prices = {name: [cfg["start"]] * 25 for name, cfg in MARKETS.items()}
        st.session_state.positions = {}
        st.session_state.trades = []
        st.session_state.steps = 0
        st.session_state.start_equity = STARTING_CASH
        st.session_state.paused = False

def equity_value():
    holdings = sum(pos["units"] * st.session_state.prices[name][-1]
                   for name, pos in st.session_state.positions.items())
    return st.session_state.cash + holdings

def close_position(name, reason):
    pos = st.session_state.positions.pop(name)
    price = st.session_state.prices[name][-1]
    proceeds = pos["units"] * price
    pnl = (price - pos["entry"]) * pos["units"]
    st.session_state.cash += proceeds
    st.session_state.trades.insert(0, {
        "Time": datetime.now(timezone.utc).strftime("%H:%M:%S UTC"),
        "Market": name, "Action": "SELL", "Price": price,
        "P/L": pnl, "Reason": reason
    })

def advance_market():
    for name, cfg in MARKETS.items():
        old = st.session_state.prices[name][-1]
        change = random.gauss(0, cfg["vol"])
        new = max(old * (1 + change), 0.00001)
        st.session_state.prices[name].append(new)
        st.session_state.prices[name] = st.session_state.prices[name][-60:]

        if name in st.session_state.positions:
            pos = st.session_state.positions[name]
            move = new / pos["entry"] - 1
            if move <= -STOP_LOSS:
                close_position(name, "Stop-loss")
                continue
            if move >= TAKE_PROFIT:
                close_position(name, "Take-profit")
                continue

        history = st.session_state.prices[name]
        if len(history) >= 20 and name not in st.session_state.positions:
            fast = sum(history[-5:]) / 5
            slow = sum(history[-20:]) / 20
            if fast > slow and st.session_state.cash > 0:
                if equity_value() >= STARTING_CASH * (1 - MAX_DRAWDOWN):
                    budget = min(st.session_state.cash, equity_value() * POSITION_FRACTION)
                    units = budget / new
                    st.session_state.cash -= budget
                    st.session_state.positions[name] = {"entry": new, "units": units}
                    st.session_state.trades.insert(0, {
                        "Time": datetime.now(timezone.utc).strftime("%H:%M:%S UTC"),
                        "Market": name, "Action": "BUY", "Price": new,
                        "P/L": 0.0, "Reason": "5/20 moving-average trend"
                    })
        elif len(history) >= 20 and name in st.session_state.positions:
            fast = sum(history[-5:]) / 5
            slow = sum(history[-20:]) / 20
            if fast < slow:
                close_position(name, "Trend reversal")

initialise()

st.title("🤖 ATLAS AI")
st.caption("Version 0.1 • Educational paper-trading simulator")
st.warning("PAPER MODE ONLY — prices are randomly simulated, not live market prices. No broker is connected and no real orders can be placed.")

with st.sidebar:
    st.header("Safety controls")
    st.write("Trading mode: **SIMULATION ONLY**")
    st.write(f"Position size: **{POSITION_FRACTION:.0%}** of equity per entry")
    st.write(f"Stop-loss: **{STOP_LOSS:.0%}**")
    st.write(f"Take-profit: **{TAKE_PROFIT:.0%}**")
    st.write(f"Maximum drawdown guard: **{MAX_DRAWDOWN:.0%}**")
    st.divider()
    if st.button("Reset paper account", use_container_width=True):
        for key in ("cash", "prices", "positions", "trades", "steps", "start_equity", "paused"):
            st.session_state.pop(key, None)
        st.rerun()

equity = equity_value()
open_pnl = sum((st.session_state.prices[n][-1] - p["entry"]) * p["units"]
               for n, p in st.session_state.positions.items())
closed_pnl = sum(t["P/L"] for t in st.session_state.trades)
c1, c2 = st.columns(2)
c1.metric("Paper account equity", f"${equity:,.2f}", f"{equity - STARTING_CASH:+,.2f}")
c2.metric("Available cash", f"${st.session_state.cash:,.2f}")
c3, c4 = st.columns(2)
c3.metric("Open positions", str(len(st.session_state.positions)))
c4.metric("Open P/L", f"${open_pnl:+,.2f}")

st.subheader("Market monitor")
for name, cfg in MARKETS.items():
    history = st.session_state.prices[name]
    current = history[-1]
    previous = history[-2]
    change_pct = (current / previous - 1) * 100
    fast = sum(history[-5:]) / 5
    slow = sum(history[-20:]) / 20
    signal = "Bullish trend" if fast > slow else "Bearish / wait"
    st.markdown(f"**{name}** — `{current:,.5f}` · {change_pct:+.2f}% · {signal}")
    st.line_chart({"Simulated price": history}, height=130)

st.subheader("Paper trading controls")
st.write(f"Simulation steps completed: **{st.session_state.steps}**")
if st.button("▶ Run next simulation step", type="primary", use_container_width=True):
    if equity < STARTING_CASH * (1 - MAX_DRAWDOWN):
        st.error("Drawdown guard triggered. Reset the paper account before continuing.")
    else:
        advance_market()
        st.session_state.steps += 1
        st.rerun()

if st.session_state.positions:
    st.subheader("Open positions")
    for name, pos in st.session_state.positions.items():
        last = st.session_state.prices[name][-1]
        pnl = (last - pos["entry"]) * pos["units"]
        st.write(f"**{name}** · entry {pos['entry']:,.5f} · current {last:,.5f} · P/L ${pnl:+,.2f}")

st.subheader("Trade history")
if st.session_state.trades:
    st.dataframe(st.session_state.trades[:30], use_container_width=True, hide_index=True)
else:
    st.info("No trades yet. Run a few simulation steps to let the strategy observe the market.")

st.caption("Strategy v0.1: a simple 5-period / 20-period moving-average trend rule with simulated fills. It is not an AI prediction model and does not demonstrate profitability. State is held in this browser session and may reset when the app restarts.")
