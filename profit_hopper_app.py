
import streamlit as st
import pandas as pd

# Load game list from GitHub
url = "https://raw.githubusercontent.com/nwt002tech/profit-hopper/main/extended_game_list.csv"
games_df = pd.read_csv(url)

# Ensure numeric fields are parsed properly
numeric_fields = [
    "Volatility", "RTP", "Bonus_Frequency", "Advantage_Play_Potential",
    "Min_Bet", "Max_Bet", "Stop_Loss"
]
for field in numeric_fields:
    if field in games_df.columns:
        games_df[field] = pd.to_numeric(games_df[field], errors="coerce")

# App layout
st.set_page_config(page_title="Profit Hopper", layout="wide")
st.title("🎯 Profit Hopper")
st.markdown("Smart game recommendations based on your bankroll and strategy goals.")

# User input
total_bankroll = st.number_input("💰 Total Bankroll", min_value=10, value=100)
num_sessions = st.slider("🎯 Number of Sessions", 1, 20, 5)
session_bankroll = total_bankroll / num_sessions
max_bet = round(session_bankroll * 0.25, 2)

# Game recommendation logic
def recommend_games(df, session_bankroll, max_bet):
    df = df.copy()
    df["Stop_Loss"] = (session_bankroll * 0.6).round(2)
    df["Score"] = (
        df["RTP"] * 0.4 +
        df["Volatility"] * -0.3 +
        df["Bonus_Frequency"] * 0.2 +
        df["Advantage_Play_Potential"] * 0.1
    )
    filtered = df[
        (df["Min_Bet"] <= max_bet) & 
        (df["Stop_Loss"] >= df["Min_Bet"])
    ].sort_values("Score", ascending=False)
    return filtered.reset_index(drop=True)

# Load recommendations
try:
    recommended = recommend_games(games_df, session_bankroll, max_bet)
    st.success(f"Showing {len(recommended)} recommended games:")
    for i, row in recommended.iterrows():
        st.markdown(
            f"""
**{row['Name']}**
🎰 Type: {row['Best_Casino_Type']}
💥 Volatility: {row['Volatility']} | 🎯 RTP: {row['RTP']}%
🎲 Bonus Frequency: {row['Bonus_Frequency']} | 🧠 AP Potential: {row['Advantage_Play_Potential']}
🛑 **Stop Loss: ${row['Stop_Loss']}**
""".strip(),
            unsafe_allow_html=True,
        )
except Exception as e:
    st.error(f"Failed to load recommendations: {e}")
