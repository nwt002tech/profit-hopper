
import streamlit as st
import pandas as pd

# Load game list from local CSV file in the repo
df = pd.read_csv("extended_game_list.csv")

# Sample bankroll/session setup
total_bankroll = 100.00
total_sessions = 5
session_bankroll = total_bankroll / total_sessions
max_bet = session_bankroll * 0.25

# Bankroll and Game Plan Summary
st.markdown("### 💰 Bankroll Status")
st.markdown(f"**Total Bankroll:** ${total_bankroll:.2f}")

st.markdown("### 🎯 Game Plan Summary")
st.markdown(f"**Bankroll/Session:** ${session_bankroll:.2f} | **Max Bet/Session:** ${max_bet:.2f}")

# Filter recommended games based on session parameters
filtered = df[df["Min_Bet"] <= max_bet]
filtered = filtered.sort_values(by="RTP", ascending=False)

# Display recommendations
st.markdown("### 🧠 Recommended Games")
for idx, row in filtered.iterrows():
    st.markdown(f"""**{row['Name']}**
🎰 Min Bet: ${row['Min_Bet']:.2f} | 🛑 Stop-Loss: ${max(session_bankroll * 0.6, row['Min_Bet']):.2f}
📝 {row['Tips']}""")
