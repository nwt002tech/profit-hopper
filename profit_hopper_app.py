
import streamlit as st
import pandas as pd

# Load game data
games_df = pd.read_csv("extended_game_list.csv")

# Example session parameters (replace with dynamic values as needed)
total_bankroll = 100
total_sessions = 5
session_bankroll = total_bankroll / total_sessions
max_bet = session_bankroll / 4

# Bankroll Summary
st.markdown("### 💰 Bankroll Status")
st.markdown(f"**Total Bankroll:** ${total_bankroll:.2f} | **Sessions:** {total_sessions}")

# Game Plan Summary
st.markdown("### 🎯 Game Plan Summary")
st.markdown(f"**Bankroll/Session:** ${session_bankroll:.2f} | **Max Bet/Session:** ${max_bet:.2f}")

# Recommendation Logic
def recommend_games(df, session_bankroll, max_bet):
    df = df.copy()
    df["Score"] = (
        df["Bonus_Frequency"] * 0.3 +
        df["Volatility"] * -0.4 +
        df["Advantage_Play_Potential"] * 0.2 +
        df["Hit_Frequency"] * 0.1 +
        df["RTP"] * 0.3
    )
    df["Stop_Loss"] = df[["Min_Bet", "Score"]].apply(
        lambda row: max(row["Min_Bet"], round(session_bankroll * 0.6, 2)), axis=1
    )
    df["Score"] = df["Score"].round(2)
    df = df[df["Min_Bet"] <= max_bet]
    return df.sort_values(by="Score", ascending=False)

# Display Recommended Games
st.markdown("### 🧠 Recommended Games")
recommended = recommend_games(games_df, session_bankroll, max_bet)
for _, row in recommended.iterrows():
    st.markdown(f"""
**{row['Name']}**
🎰 Type: {row['Best_Casino_Type']}
💡 Tips: {row['Tips']}
📉 Volatility: {row['Volatility']} | 🎯 RTP: {row['RTP']}%
🔥 Bonus Frequency: {row['Bonus_Frequency']} | 🎯 Hit Frequency: {row['Hit_Frequency']}
💰 Min Bet: ${row['Min_Bet']} | 🛑 Stop Loss: ${row['Stop_Loss']}
---
""")
