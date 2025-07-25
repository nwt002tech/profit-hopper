import streamlit as st
import pandas as pd

# Load external game list from GitHub
game_list_url = "https://raw.githubusercontent.com/nwt002tech/profit-hopper/main/extended_game_list.csv"
df = pd.read_csv(game_list_url)

# Session inputs
total_bankroll = st.sidebar.number_input("Total Bankroll", min_value=10, value=100)
total_sessions = st.sidebar.number_input("Number of Sessions", min_value=1, value=5)
session_bankroll = total_bankroll / total_sessions
max_bet = session_bankroll * 0.25

st.markdown("### 💰 Bankroll Status")
st.markdown(f"**Total Bankroll:** ${total_bankroll:.2f} | **Sessions:** {total_sessions}")
st.markdown("### 🎯 Game Plan Summary")
st.markdown(f"**Bankroll/Session:** ${session_bankroll:.2f} | **Max Bet/Session:** ${max_bet:.2f}")

# Calculate score for each game based on multiple factors
df["Score"] = (
    df["RTP"] * 1.5 +
    df["Bonus_Frequency"] * 1.0 +
    df["Volatility"] * -0.4 +
    df["Advantage_Play_Potential"] * 1.2
)

# Filter games based on min bet and bankroll
df["Min_Bet_OK"] = df["Min_Bet"] <= max_bet
filtered = df[df["Min_Bet_OK"]]
filtered = filtered.sort_values(by="Score", ascending=False)

# Calculate Stop-Loss
filtered["Stop_Loss"] = (session_bankroll * 0.6).clip(lower=filtered["Min_Bet"]).round(2)

st.markdown("### 🧠 Recommended Games")
for idx, row in filtered.iterrows():
    st.markdown(f"""**{row['Name']}**
🎰 Min Bet: ${row['Min_Bet']} | 🛑 Stop-Loss: ${row['Stop_Loss']}
📝 {row['Tips']}""")