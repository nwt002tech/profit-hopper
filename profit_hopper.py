
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Profit Hopper", layout="centered")

st.title("🎰 Profit Hopper - Casino Bankroll Manager")

# Sidebar setup
with st.sidebar:
    st.header("🎯 Session Setup")
    bankroll = st.number_input("Enter your total bankroll ($):", min_value=10, max_value=10000, value=100, step=10)
    sessions = st.number_input("How many machines/sessions to divide into?", min_value=1, max_value=20, value=5, step=1)
    risk = st.selectbox("Select your risk level:", ["Low", "Medium", "High"])
    profit_goal_percent = st.slider("Profit Goal (%):", 5, 100, 20)

# Calculations
session_unit = bankroll / sessions
max_bet = session_unit / 40
profit_goal = bankroll * (1 + profit_goal_percent / 100)

st.subheader("📊 Strategy Overview")
col1, col2 = st.columns(2)
col1.metric("Session Unit ($)", f"${session_unit:.2f}")
col2.metric("Max Bet per Spin ($)", f"${max_bet:.2f}")
st.success(f"💰 Target Cashout: ${profit_goal:.2f}")

# Initialize session state for tracking
if "tracker" not in st.session_state:
    st.session_state.tracker = []

st.markdown("---")
st.subheader("🎮 Track Your Machine")

with st.form("session_form"):
    game = st.text_input("Game / Machine Name")
    amount_in = st.number_input("Amount Inserted ($)", min_value=0.0, step=1.0)
    amount_out = st.number_input("Cashout Amount ($)", min_value=0.0, step=1.0)
    bonus_hit = st.radio("Bonus Hit?", ["Yes", "No"], horizontal=True)
    rule_followed = st.radio("Followed Spin/Loss Rule?", ["Yes", "No"], horizontal=True)
    notes = st.text_area("Session Notes", placeholder="Any observations or emotional triggers...")

    submitted = st.form_submit_button("Add Session Entry")

    if submitted:
        win_loss = amount_out - amount_in
        st.session_state.tracker.append({
            "Game": game,
            "Amount In": amount_in,
            "Amount Out": amount_out,
            "Win/Loss": win_loss,
            "Bonus Hit": bonus_hit,
            "Rule Followed": rule_followed,
            "Notes": notes
        })
        st.success("Session logged!")

# Display session tracker
if st.session_state.tracker:
    st.markdown("### 🧾 Session Log")
    df = pd.DataFrame(st.session_state.tracker)
    df.index += 1
    st.dataframe(df, use_container_width=True)

    total_in = df["Amount In"].sum()
    total_out = df["Amount Out"].sum()
    total_net = total_out - total_in

    st.markdown("### 📈 Summary")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total In", f"${total_in:.2f}")
    col2.metric("Total Out", f"${total_out:.2f}")
    col3.metric("Net Profit", f"${total_net:.2f}")

    if total_out >= profit_goal:
        st.balloons()
        st.success("🎉 You reached your profit goal! Time to walk away a winner.")
    elif total_net < 0:
        st.warning("You're currently down. Stick to the plan and don't chase losses.")
