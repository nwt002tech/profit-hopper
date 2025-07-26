
import streamlit as st
import pandas as pd

@st.cache_data
def load_game_data():
    url = "https://raw.githubusercontent.com/nwt002tech/profit-hopper/main/extended_game_list.csv"
    return pd.read_csv(url)

def recommend_games(df, session_bankroll, max_bet):
    df = df.copy()

    numeric_fields = [
        "RTP", "Volatility", "Bonus_Frequency", "Hit_Frequency",
        "Advantage_Play_Potential", "Min_Bet"
    ]
    for field in numeric_fields:
        if field in df.columns:
            df[field] = pd.to_numeric(df[field], errors="coerce").fillna(0)

    # Calculate Stop_Loss dynamically based on session bankroll and Min_Bet
    df["Stop_Loss"] = pd.Series(session_bankroll * 0.6, index=df.index).clip(lower=df["Min_Bet"]).round(2)

    # Scoring system based on weighted metrics
    df["Score"] = (
        df["RTP"] * 0.3 +
        (1 - df["Volatility"]) * 0.2 +
        df["Bonus_Frequency"] * 0.2 +
        df["Hit_Frequency"] * 0.1 +
        df["Advantage_Play_Potential"] * 0.2
    )

    filtered_df = df[df["Min_Bet"] <= max_bet]
    recommended = filtered_df.sort_values(by="Score", ascending=False).reset_index(drop=True)
    return recommended

# --- App UI ---
st.title("🎯 Profit Hopper - Casino Strategy Assistant")

total_bankroll = st.number_input("💰 Total Bankroll", value=100.0, step=10.0)
num_sessions = st.number_input("🎯 Number of Sessions", value=5, step=1)
session_bankroll = round(total_bankroll / num_sessions, 2)
max_bet = round(session_bankroll * 0.25, 2)

st.markdown(f"**Session Bankroll:** ${session_bankroll} | **Max Bet per Game:** ${max_bet}")

# Load and analyze games
try:
    games_df = load_game_data()
    recommended = recommend_games(games_df, session_bankroll, max_bet)

    st.subheader("🧠 Recommended Games")
    for idx, row in recommended.iterrows():
        st.markdown(f"""
        **🎰 {row['Name']}**
        - 📂 Type: {row.get('Best_Casino_Type', 'N/A')}
        - 🎲 Min Bet: ${row['Min_Bet']}
        - 🛑 Stop Loss: ${row['Stop_Loss']}
        - 🔁 Bonus Frequency: {row['Bonus_Frequency']}
        - 🧠 AP Potential: {row['Advantage_Play_Potential']}
        - 📊 Score: {row['Score']:.2f}
        """)
except Exception as e:
    st.error(f"Failed to load recommendations: {e}")
