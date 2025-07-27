
import streamlit as st
import pandas as pd
import requests


def format_advantage_play(value):
    if value >= 0.8:
        return "🧠 Very High Advantage"
    elif value >= 0.6:
        return "👍 High Advantage"
    elif value >= 0.4:
        return "⚠️ Moderate Advantage"
    elif value >= 0.2:
        return "🔍 Low Advantage"
    else:
        return "🚫 Minimal Advantage"

def format_volatility(value):
    if value <= 2:
        return "🌱 Low Volatility"
    elif value <= 4:
        return "🎯 Medium Volatility"
    else:
        return "🔥 High Volatility"

def format_bonus_frequency(value):
    if value >= 0.4:
        return "🎁 Very Frequent Bonuses"
    elif value >= 0.25:
        return "🎁 Moderate Bonuses"
    elif value >= 0.1:
        return "🎁 Rare Bonuses"
    else:
        return "🎁 Very Rare Bonuses"

st.set_page_config(page_title="Profit Hopper", layout="wide")

@st.cache_data
def load_game_data():
    url = "https://raw.githubusercontent.com/nwt002tech/profit-hopper/main/extended_game_list.csv"
    return pd.read_csv(url)

def recommend_games(df, session_bankroll, max_bet):
    df = df.copy()
    numeric_fields = ["Min_Bet", "Volatility", "Bonus_Frequency", "RTP", "Advantage_Play_Potential"]
    for field in numeric_fields:
        if field in df.columns:
            df[field] = pd.to_numeric(df[field], errors="coerce")
    df.dropna(subset=["Min_Bet"], inplace=True)
    df["Stop_Loss"] = round(session_bankroll * 0.6, 2)
    df["Score"] = (
        df["Advantage_Play_Potential"] * 0.4 +
        df["Bonus_Frequency"] * 0.3 +
        df["RTP"] * 0.2 +
        (1 / (df["Volatility"] + 1)) * 0.1
    )
    df = df[df["Min_Bet"] <= max_bet]
    return df.sort_values(by="Score", ascending=False).reset_index(drop=True)

st.title("💰 Profit Hopper")

total_bankroll = st.number_input("Enter Total Bankroll ($)", value=100.0, step=10.0)
num_sessions = st.slider("Number of Sessions", 1, 20, 5)
session_bankroll = total_bankroll / num_sessions
max_bet = round(session_bankroll * 0.25, 2)

st.markdown(f"### 📊 Session Settings")
st.markdown(f"- 💵 **Session Bankroll**: ${session_bankroll:.2f}")
st.markdown(f"- 🎯 **Max Bet/Game**: ${max_bet:.2f}")
st.markdown("---")

try:
    games_df = load_game_data()
    recommended = recommend_games(games_df, session_bankroll, max_bet)

    st.subheader("🎯 Top Game Recommendations")
    for _, row in recommended.iterrows():
        with st.container():
            
st.markdown(f"""
**{{row['Name']}}**

🎰 Type: {{row["Type"]}}
💸 Min Bet: ${{row["Min_Bet"]}}
🚫 StopLoss: ${{row["Stop_Loss"]}}

🧠 {{format_advantage_play(row["Advantage_Play_Potential"])}}
🎲 {{format_volatility(row["Volatility"])}}
🎁 {{format_bonus_frequency(row["Bonus_Frequency"])}}
🔢 RTP: {{row["RTP"]}}%
💡 Tips: {{row["Tips"]}}
""")

except Exception as e:
    st.error(f"Failed to load recommendations: {e}")