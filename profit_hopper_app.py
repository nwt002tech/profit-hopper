
import streamlit as st
import pandas as pd
import numpy as np

# --- Load Data ---
@st.cache_data
def load_game_data():
    url = "https://raw.githubusercontent.com/nwt002tech/profit-hopper/main/extended_game_list.csv"
    return pd.read_csv(url)

games_df = load_game_data()

# --- Session Settings ---
st.title("🎯 Profit Hopper - Smart Bankroll Strategy")
total_bankroll = st.number_input("Total Bankroll ($)", min_value=20, value=100)
total_sessions = st.number_input("Number of Sessions", min_value=1, value=5)
session_bankroll = round(total_bankroll / total_sessions, 2)
max_bet = round(session_bankroll * 0.25, 2)

# --- Display Status ---
st.markdown("### 💰 Bankroll Status")
st.markdown(f"**Total Bankroll:** ${total_bankroll:.2f} | **Sessions:** {total_sessions}")

st.markdown("### 📊 Game Plan Summary")
st.markdown(f"**Bankroll per Session:** ${session_bankroll:.2f} | **Max Bet per Session:** ${max_bet:.2f}")

# --- Recommendation Engine ---
def recommend_games(df, session_bankroll, max_bet):
    for col in ["Volatility", "RTP", "Bonus_Frequency", "Advantage_Play_Potential", "Min_Bet"]:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    df["Stop_Loss"] = np.maximum(session_bankroll * 0.6, df["Min_Bet"])

    df["Score"] = (
        df["RTP"] * 0.3 +
        (1 - df["Volatility"]) * 0.2 +
        df["Bonus_Frequency"] * 0.3 +
        df["Advantage_Play_Potential"] * 0.2
    )

    filtered_df = df[
        (df["Min_Bet"] <= max_bet) &
        (df["Stop_Loss"] <= session_bankroll)
    ]

    recommended = filtered_df.sort_values(by="Score", ascending=False).head(10)
    return recommended

recommended = recommend_games(games_df.copy(), session_bankroll, max_bet)

# --- Display Recommendations ---
st.markdown("### 🧠 Recommended Games")
if not recommended.empty:
    for _, row in recommended.iterrows():
        st.markdown(f"""
        **{row['Name']}**
        🎰 Type: {row['Type']}  
        💵 Min Bet: ${row['Min_Bet']} | 🎯 Stop-Loss: ${row['Stop_Loss']:.2f}  
        📈 RTP: {row['RTP']} | 🎲 Volatility: {row['Volatility']}  
        🔁 Bonus Freq: {row['Bonus_Frequency']} | 🧠 AP Score: {row['Advantage_Play_Potential']}  
        📝 {row['Tips']}
        """)
else:
    st.warning("No games meet your current session settings. Try increasing bankroll or reducing max bet.")
