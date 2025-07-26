# ✅ Base Version: 2025-07-26
import streamlit as st
import pandas as pd

# Load game list
@st.cache_data
def load_game_data():
    return pd.read_csv("extended_game_list.csv")

def recommend_games(df, session_bankroll, max_bet):
    df = df.copy()
    df["Score"] = (
        df["RTP"] * 0.3 +
        df["Volatility"] * -0.4 +
        df["Bonus_Frequency"] * 0.2 +
        df["Advantage_Play_Potential"] * 0.2
    )
    df["Stop_Loss"] = session_bankroll * 0.6
    df["Stop_Loss"] = df["Stop_Loss"].clip(lower=df["Min_Bet"]).round(2)
    recommended = df[df["Min_Bet"] <= max_bet].sort_values(by="Score", ascending=False)
    return recommended

st.set_page_config(page_title="Profit Hopper", layout="wide")

st.title("Profit Hopper: Bankroll Strategy Optimizer")

# Input section
col1, col2 = st.columns(2)
with col1:
    total_bankroll = st.number_input("Total Bankroll ($)", min_value=1, value=100)
    session_count = st.number_input("Number of Sessions", min_value=1, value=5)
with col2:
    session_bankroll = total_bankroll / session_count
    max_bet = round(session_bankroll * 0.25, 2)
    st.metric("Session Bankroll", f"${session_bankroll:.2f}")
    st.metric("Max Bet per Game", f"${max_bet:.2f}")

# Load games
games_df = load_game_data()
recommended = recommend_games(games_df, session_bankroll, max_bet)

# Show recommendations
st.subheader("Recommended Games to Play")
for idx, row in recommended.iterrows():
    st.markdown(f"""
**{row['Name']}**  
Type: {row['Best_Casino_Type']}  
Min Bet: ${row['Min_Bet']}  
Volatility: {row['Volatility']}  
RTP: {row['RTP']}%  
Bonus Freq: {row['Bonus_Frequency']}  
Stop-Loss: ${row['Stop_Loss']}  
Advantage Play: {row['Advantage_Play_Potential']}  
Tips: {row['Tips']}
---
""")

# End of file
