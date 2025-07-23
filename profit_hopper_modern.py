
import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Profit Hopper", layout="centered")

# Initialize session state
if "tracker" not in st.session_state:
    st.session_state.tracker = []

# --- Header ---
st.markdown("## 🎰 Profit Hopper")
st.caption("Casino Bankroll Discipline & Tracker")

# --- Sidebar Setup ---
with st.sidebar:
    st.header("🎯 Setup")
    bankroll = st.number_input("💵 Starting Bankroll ($)", min_value=10, value=100, step=10)
    sessions = st.number_input("🎮 Machines/Sessions to Divide", min_value=1, value=5)
    risk = st.selectbox("📊 Risk Level", ["Low", "Medium", "High"])
    profit_goal_percent = st.slider("🏁 Profit Goal (%)", 5, 100, 20)

# --- Strategy Logic ---
session_unit = bankroll / sessions
risk_factor = {"Low": 40, "Medium": 30, "High": 20}
max_bet = session_unit / risk_factor[risk]
profit_goal = bankroll * (1 + profit_goal_percent / 100)

# --- Summary Sections ---
with st.container():
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("**📈 Bankroll Summary**")
        st.write(f"Start: ${bankroll:.2f}")
        st.write(f"Goal: ${profit_goal:.2f}")
    with col2:
        st.markdown("**📊 Session Strategy**")
        st.write(f"Per Session: ${session_unit:.2f}")
        st.write(f"Max Bet: ${max_bet:.2f}")
    with col3:
        st.markdown("**💼 Bankroll Status**")
        df = pd.DataFrame(st.session_state.tracker)
        total_in = df["Amount In"].sum() if not df.empty else 0
        total_out = df["Amount Out"].sum() if not df.empty else 0
        net = total_out - total_in
        st.write(f"In: ${total_in:.2f}")
        st.write(f"Out: ${total_out:.2f}")
        st.write(f"Net: ${net:.2f}")

st.markdown("---")

# --- Tabs ---
tab1, tab2 = st.tabs(["📋 Session Tracker", "📊 Session Log"])

# --- Tracker Input ---
with tab1:
    st.subheader("Log a Machine/Session")
    with st.form("session_form", clear_on_submit=True):
        game = st.text_input("Game / Machine Name")
        amount_in = st.number_input("Amount Inserted ($)", min_value=0.0, step=1.0)
        amount_out = st.number_input("Cashout Amount ($)", min_value=0.0, step=1.0)
        bonus_hit = st.radio("Bonus Hit?", ["Yes", "No"], horizontal=True)
        rule_followed = st.radio("Followed Rule?", ["Yes", "No"], horizontal=True)
        notes = st.text_area("Session Notes")
        submitted = st.form_submit_button("➕ Add Entry")

        if submitted:
            win_loss = amount_out - amount_in
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            st.session_state.tracker.append({
                "Date/Time": timestamp,
                "Game": game,
                "Amount In": amount_in,
                "Amount Out": amount_out,
                "Win/Loss": win_loss,
                "Bonus Hit": bonus_hit,
                "Rule Followed": rule_followed,
                "Notes": notes
            })
            st.success("Session added!")

# --- Tracker Output ---
with tab2:
    st.subheader("🧾 Session Log")
    if st.session_state.tracker:
        df = pd.DataFrame(st.session_state.tracker)
        df.index += 1
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No sessions logged yet.")
