
import streamlit as st
import pandas as pd

# Load extended game list from GitHub
games_url = "https://raw.githubusercontent.com/nwt002tech/profit-hopper/main/extended_game_list.csv"
games_df = pd.read_csv(games_url)

# Convert critical columns to numeric safely
numeric_fields = ['Volatility', 'Bonus_Frequency', 'Advantage_Play_Potential', 'Min_Bet']
for field in numeric_fields:
    games_df[field] = pd.to_numeric(games_df[field], errors='coerce').fillna(0)

# Inputs
st.title("🎯 Profit Hopper: Bankroll Growth Strategy")
total_bankroll = st.number_input("Total Bankroll ($)", value=100.0, step=1.0)
total_sessions = st.number_input("Number of Sessions", value=5, step=1)
session_bankroll = round(total_bankroll / total_sessions, 2)
max_bet = round(session_bankroll / 4, 2)

st.markdown(f"### 💰 Bankroll Summary")
st.markdown(f"**Session Bankroll:** ${session_bankroll:.2f} | **Max Bet:** ${max_bet:.2f}")

# Recommendation function
def recommend_games(df, session_bankroll, max_bet):
    df = df.copy()
    df["Score"] = (
        df["Bonus_Frequency"] * 0.4 +
        df["Advantage_Play_Potential"] * 0.2 -
        df["Volatility"] * 0.3
    )
    df["Stop_Loss"] = df["Min_Bet"].clip(lower=1.0)
    filtered = df[
        (df["Min_Bet"] <= max_bet) & 
        (df["Stop_Loss"] <= session_bankroll)
    ].sort_values(by="Score", ascending=False)
    return filtered

# Display Recommendations
recommended = recommend_games(games_df, session_bankroll, max_bet)

st.markdown("### 🧠 Recommended Games")
for _, row in recommended.iterrows():
    st.markdown(f"""
**🎮 {row['Name']}**
🧪 Volatility: {row['Volatility']}
🎁 Bonus Frequency: {row['Bonus_Frequency']}
📈 Advantage Potential: {row['Advantage_Play_Potential']}
💵 Min Bet: ${row['Min_Bet']}
🛑 Stop-Loss: ${row['Stop_Loss']}
📌 Tip: {row['Tips']}
---
""")
