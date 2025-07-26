
import streamlit as st
import pandas as pd

# Set up page
st.set_page_config(page_title="Profit Hopper", layout="centered")

@st.cache_data
def load_game_data():
    url = "https://raw.githubusercontent.com/nwt002tech/profit-hopper/main/extended_game_list.csv"
    return pd.read_csv(url)

def recommend_games(df, session_bankroll, max_bet):
    numeric_fields = [
        "Volatility", "Bonus_Frequency", "Advantage_Play_Potential",
        "Expected_RTP", "Min_Bet", "Max_Bet"
    ]
    for field in numeric_fields:
        df[field] = pd.to_numeric(df[field], errors="coerce")

    df = df.dropna(subset=numeric_fields)
    df["Score"] = (
        df["Expected_RTP"] * 0.4 +
        df["Bonus_Frequency"] * 0.2 +
        df["Advantage_Play_Potential"] * 0.2 +
        df["Volatility"] * -0.2
    )

    df = df[df["Min_Bet"] <= max_bet]
    stop_loss_value = round(session_bankroll * 0.6, 2)
    df["Stop_Loss"] = df["Min_Bet"].apply(lambda x: round(max(stop_loss_value, x), 2))
    return df.sort_values(by="Score", ascending=False).reset_index(drop=True)

# App UI
st.title("🎯 Profit Hopper")

bankroll = st.number_input("Total Bankroll", min_value=10, value=100, step=10)
sessions = st.number_input("Planned Sessions", min_value=1, value=5, step=1)
session_bankroll = bankroll / sessions
max_bet = round(session_bankroll * 0.25, 2)

st.markdown(f"**Bankroll per Session:** ${session_bankroll:.2f} | **Max Bet:** ${max_bet:.2f}")

games_df = load_game_data()

try:
    recommended = recommend_games(games_df, session_bankroll, max_bet)
    st.subheader("🎰 Recommended Games")
    for _, row in recommended.iterrows():
        st.markdown(f"""
**{row['Name']}**
🎮 Type: {row['Best_Casino_Type']}  
💰 Min Bet: ${row['Min_Bet']} | Max Bet: ${row['Max_Bet']}  
🧠 RTP: {row['Expected_RTP']} | 🎯 Volatility: {row['Volatility']}  
🎁 Bonus Freq: {row['Bonus_Frequency']} | 🕵️‍♂️ AP: {row['Advantage_Play_Potential']}  
🛑 Stop Loss: ${row['Stop_Loss']}
---
""")
except Exception as e:
    st.error(f"Failed to load recommendations: {e}")
