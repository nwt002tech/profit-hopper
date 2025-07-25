
import streamlit as st
import pandas as pd

CSV_URL = "https://raw.githubusercontent.com/nwt002tech/profit-hopper/c821448aa7f9866b6d300bc1f31bba60db5b4144/extended_game_list.csv"

@st.cache_data
def load_game_data():
    return pd.read_csv(CSV_URL)

games_df = load_game_data()

st.title("🎰 Profit Hopper")

# Sample bankroll settings
total_bankroll = 100.0
total_sessions = 5
session_bankroll = total_bankroll / total_sessions
max_bet = round(session_bankroll * 0.25, 2)

# Bankroll Summary
st.markdown("### 💰 Bankroll Status")
st.markdown(f"**Total Bankroll:** ${total_bankroll:.2f} | **Money In:** $0.00 | **Money Out:** $0.00 | **Net:** $0.00")

# Game Plan Summary
st.markdown("### 🎯 Game Plan Summary")
st.markdown(f"**Sessions:** {total_sessions} | **Bankroll/Session:** ${session_bankroll:.2f} | **Max Bet/Session:** ${max_bet:.2f}")

# Game List from GitHub
st.markdown("### 🎮 Recommended Games")
st.dataframe(games_df)
