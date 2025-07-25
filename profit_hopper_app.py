
import streamlit as st
import pandas as pd
from datetime import datetime

# Initialize session state
if "session_log" not in st.session_state:
    st.session_state.session_log = []

# Title and layout setup
st.set_page_config(page_title="Profit Hopper", layout="wide")

# User inputs
st.sidebar.header("Settings")
total_bankroll = st.sidebar.number_input("Total Bankroll", min_value=10, value=100)
total_sessions = st.sidebar.number_input("Number of Sessions", min_value=1, value=5)

session_bankroll = round(total_bankroll / total_sessions, 2)
max_bet = round(session_bankroll * 0.25, 2)

# Compact summaries
st.markdown("### 💰 Bankroll Status")
st.markdown(f"**Total Bankroll:** ${total_bankroll:.2f} | **Sessions:** {total_sessions}")

st.markdown("### 🎯 Game Plan Summary")
st.markdown(f"**Bankroll/Session:** ${session_bankroll:.2f} | **Max Bet/Session:** ${max_bet:.2f}")

# Tabs for sections
tab1, tab2, tab3 = st.tabs(["📋 Game Plan", "🧾 Tracker", "📈 Summary"])

with tab1:
    st.subheader("Recommended Games")
    st.info("Game recommendations will appear here (dynamic feature to be added).")

with tab2:
    st.subheader("Session Tracker")
    with st.form("log_session"):
        date = datetime.now().strftime("%Y-%m-%d %I:%M %p")
        game = st.text_input("Game Played")
        amount_in = st.number_input("Amount In", min_value=0.0, value=0.0)
        amount_out = st.number_input("Amount Out", min_value=0.0, value=0.0)
        submitted = st.form_submit_button("Add Entry")
        if submitted and game:
            st.session_state.session_log.append({
                "Time": date,
                "Game": game,
                "In": amount_in,
                "Out": amount_out,
                "Net": round(amount_out - amount_in, 2)
            })

with tab3:
    st.subheader("Session Log Summary")
    if st.session_state.session_log:
        df = pd.DataFrame(st.session_state.session_log)
        st.dataframe(df)
        total_in = df["In"].sum()
        total_out = df["Out"].sum()
        net = total_out - total_in
        st.markdown(f"**Total In:** ${total_in:.2f} | **Total Out:** ${total_out:.2f} | **Net:** ${net:.2f}")
    else:
        st.info("No session data logged yet.")
