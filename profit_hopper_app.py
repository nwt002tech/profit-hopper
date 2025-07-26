
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Profit Hopper", layout="wide")

st.title("💰 Profit Hopper")
st.markdown("Smart game recommendations based on your bankroll strategy.")

# Load data
url = "https://raw.githubusercontent.com/nwt002tech/profit-hopper/main/extended_game_list.csv"
games_df = pd.read_csv(url)

# Convert numeric fields safely
numeric_fields = ["RTP", "Volatility", "Min_Bet", "Bonus_Frequency", "Advantage_Play_Potential"]
for field in numeric_fields:
    if field in games_df.columns:
        games_df[field] = pd.to_numeric(games_df[field], errors="coerce").fillna(0)

# User inputs
total_bankroll = st.number_input("Enter your total bankroll ($)", min_value=1, value=100)
session_count = st.number_input("Number of sessions", min_value=1, value=5)
session_bankroll = round(total_bankroll / session_count, 2)
max_bet = round(session_bankroll * 0.25, 2)

st.markdown(f"**Session Bankroll:** ${session_bankroll} | **Max Bet Per Session:** ${max_bet}")

# Recommendation engine
def recommend_games(df, session_bankroll, max_bet):
    if "Bonus_Frequency" not in df.columns:
        df["Bonus_Frequency"] = 0

    df["Score"] = (
        df["RTP"] * 0.3 +
        (100 - df["Volatility"]) * 0.2 +
        df["Bonus_Frequency"] * 0.2 +
        df["Advantage_Play_Potential"] * 0.3
    )

    df = df[df["Min_Bet"] <= max_bet]
    df["Stop_Loss"] = df["Min_Bet"].apply(lambda x: round(max(x, session_bankroll * 0.6), 2))

    return df.sort_values("Score", ascending=False)

# Generate recommendations
try:
    recommended = recommend_games(games_df, session_bankroll, max_bet)
    st.subheader("🎯 Recommended Games")

    for _, row in recommended.iterrows():
        st.markdown(
            f"""**{row['Name']}**
🎰 Type: {row.get('Best_Casino_Type', 'N/A')}  
💵 Min Bet: ${row['Min_Bet']}  
🎯 RTP: {row['RTP']}%  
⚡ Volatility: {row['Volatility']}  
🎁 Bonus Frequency: {row.get('Bonus_Frequency', 'N/A')}  
🧠 Advantage Play Potential: {row.get('Advantage_Play_Potential', 'N/A')}  
🛑 Stop Loss: ${row.get('Stop_Loss', 'N/A')}
---
""")
except Exception as e:
    st.error(f"Failed to load recommendations: {e}")
