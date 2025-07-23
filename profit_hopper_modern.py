
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Profit Hopper", layout="centered")

# --- Persistent session state initialization ---
if "tracker" not in st.session_state:
    st.session_state.tracker = []

# --- Header ---
st.markdown("## 🎰 Profit Hopper")
st.caption("Track your bankroll, stay disciplined, and hit your profit goals.")

# --- Sidebar: Bankroll and Strategy Setup ---
with st.sidebar:
    st.header("🎯 Setup")
    bankroll = st.number_input("💵 Starting Bankroll ($)", min_value=10, max_value=10000, value=100, step=10)
    sessions = st.number_input("🎮 Number of Machines/Sessions", min_value=1, max_value=20, value=5)
    risk = st.selectbox("📊 Risk Level", ["Low", "Medium", "High"])
    profit_goal_percent = st.slider("🏁 Profit Goal (%)", 5, 100, 20)

# --- Strategy Calculations ---
session_unit = bankroll / sessions
risk_factor = {"Low": 40, "Medium": 30, "High": 20}
max_bet = session_unit / risk_factor[risk]
profit_goal = bankroll * (1 + profit_goal_percent / 100)

# --- Bankroll Summary: Condensed into one line ---
st.markdown(
    f"📈 **Bankroll Summary**: "
    f"💵 ${bankroll:.2f} | "
    f"🎮 ${session_unit:.2f}/session | "
    f"🎯 Max Bet ${max_bet:.2f} | "
    f"🏁 Goal: ${profit_goal:.2f}"
)

st.markdown("---")

# --- Tabs for navigation ---
tab1, tab2 = st.tabs(["📋 Session Tracker", "📊 Summary"])

with tab1:
    st.subheader("🎮 Log a Machine/Session")
    with st.form("session_form"):
        game = st.text_input("Game / Machine Name")
        amount_in = st.number_input("Amount Inserted ($)", min_value=0.0, step=1.0)
        amount_out = st.number_input("Cashout Amount ($)", min_value=0.0, step=1.0)
        bonus_hit = st.radio("Bonus Hit?", ["Yes", "No"], horizontal=True)
        rule_followed = st.radio("Followed Spin/Loss Rule?", ["Yes", "No"], horizontal=True)
        notes = st.text_area("Session Notes", placeholder="Observations or emotions...")

        submitted = st.form_submit_button("➕ Add Session")
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
            st.success("✅ Session added!")

with tab2:
    st.subheader("🧾 Session Log")
    if st.session_state.tracker:
        df = pd.DataFrame(st.session_state.tracker)
        df.index += 1
        st.dataframe(df, use_container_width=True)

        total_in = df["Amount In"].sum()
        total_out = df["Amount Out"].sum()
        total_net = total_out - total_in

        st.markdown("### 💼 Results Summary")
        cols = st.columns(3)
        cols[0].metric("Total In", f"${total_in:.2f}")
        cols[1].metric("Total Out", f"${total_out:.2f}")
        cols[2].metric("Net Profit", f"${total_net:.2f}")

        if total_out >= profit_goal:
            st.balloons()
            st.success("🎉 Profit goal reached! Walk away a winner.")
        elif total_net < 0:
            st.warning("You're currently down. Stick to the plan and manage emotions.")
    else:
        st.info("No sessions logged yet. Use the tracker to get started.")
