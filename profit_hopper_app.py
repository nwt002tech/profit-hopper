
import streamlit as st
import pandas as pd
import requests

st.set_page_config(layout="centered", page_title="Profit Hopper", page_icon="🎰")

@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/nwt002tech/profit-hopper/main/extended_game_list.csv"
    return pd.read_csv(url)

def recommend_games(df, session_bankroll, max_bet):
    numeric_fields = ["RTP", "Volatility", "Bonus_Frequency", "Advantage_Play_Potential"]
    for field in numeric_fields:
        df[field] = pd.to_numeric(df[field], errors="coerce")
    df["Score"] = (
        df["RTP"] * 0.4 +
        df["Bonus_Frequency"] * 0.2 +
        df["Advantage_Play_Potential"] * 0.2 +
        df["Volatility"] * -0.2
    )
    df["Stop_Loss"] = df["Min_Bet"].apply(lambda x: round(max(session_bankroll * 0.6, x), 2))
    return df.sort_values(by="Score", ascending=False)

df = load_data()
st.title("🎯 Profit Hopper")
st.markdown("## 💰 Session Setup")

total_bankroll = st.number_input("Total Bankroll", min_value=10, value=100)
num_sessions = st.slider("Number of Sessions", min_value=1, max_value=10, value=5)
session_bankroll = round(total_bankroll / num_sessions, 2)
max_bet = round(session_bankroll * 0.25, 2)

st.markdown(f"### 📊 Bankroll Per Session: **${session_bankroll}**, Max Bet: **${max_bet}**")

st.markdown("## 🎰 Recommended Games")
recommended = recommend_games(df, session_bankroll, max_bet)

for _, row in recommended.iterrows():
    st.markdown(f"""
    ### 🎮 {row['Name']}
    - 🧩 **Type**: {row['Best_Casino_Type']}
    - 🪙 **Min Bet**: ${row['Min_Bet']}
    - 💥 **Volatility**: {row['Volatility']}
    - 🎯 **RTP**: {row['RTP']}%
    - 🎁 **Bonus Freq**: {row['Bonus_Frequency']}
    - ✅ **AP Potential**: {row['Advantage_Play_Potential']}
    - 🚫 **Stop-Loss**: ${row['Stop_Loss']}
    """)
