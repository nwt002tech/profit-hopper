
import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Profit Hopper", layout="wide")
st.title("💰 Profit Hopper")

# --- Bankroll Inputs ---
st.sidebar.header("🎯 Bankroll Settings")
total_bankroll = st.sidebar.number_input("Total Starting Bankroll ($)", min_value=10, value=100, step=10)
sessions = st.sidebar.slider("Number of Sessions", min_value=1, max_value=10, value=5)
session_bankroll = total_bankroll / sessions
max_bet = round(session_bankroll * 0.25, 2)

# --- Summary Section ---
st.markdown(
    f"**Total Bankroll:** ${total_bankroll:.2f}  
"
    f"**Sessions:** {sessions}  
"
    f"**Bankroll/Session:** ${session_bankroll:.2f} | **Max Bet/Session:** ${max_bet:.2f}"
)

# --- Load Game Data ---
@st.cache_data
def load_game_data():
    data = {
        "Name": ["Cleopatra", "Miss Kitty", "Jacks or Better", "Buffalo Gold", "Caveman Keno"],
        "Type": ["Slot", "Slot", "Video Poker", "Slot", "Video Keno"],
        "Volatility": [3, 2, 1, 4, 1],
        "Bonus_Hit_Freq": [0.25, 0.30, 0.10, 0.20, 0.15],
        "Min_Bet": [0.2, 0.5, 0.25, 0.4, 0.25],
        "Notes": [
            "Watch for bonus symbols",
            "Look for stacked wilds",
            "Play full-pay versions only",
            "High volatility with big bonus potential",
            "Use patterns and bonus eggs"
        ]
    }
    return pd.DataFrame(data)

games_df = load_game_data()

# --- Recommendation Logic ---
def recommend_games(df, session_bankroll, max_bet):
    df = df.copy()
    df["Min_Bet_OK"] = df["Min_Bet"] <= max_bet
    filtered = df[df["Min_Bet_OK"]]
    if filtered.empty:
        return pd.DataFrame()
    filtered["Score"] = (
        (1 / (1 + filtered["Volatility"])) +
        filtered["Bonus_Hit_Freq"]
    )
    filtered["Stop_Loss"] = (session_bankroll * 0.6).round(2).clip(lower=filtered["Min_Bet"])
    return filtered.sort_values(by="Score", ascending=False).head(sessions)

recommended_games = recommend_games(games_df, session_bankroll, max_bet)

# --- Display Recommendations ---
st.subheader("Recommended Games to Play")
if recommended_games.empty:
    st.warning("No suitable games found for this bankroll and session settings.")
else:
    for idx, row in recommended_games.iterrows():
        st.markdown(
            f"**{row['Name']}**  
"
            f"Type: {row['Type']}  
"
            f"Min Bet: ${row['Min_Bet']:.2f} | Stop-Loss: ${row['Stop_Loss']:.2f}  
"
            f"{row['Notes']}"
        )
