
import streamlit as st
import pandas as pd

# Constants
CSV_URL = "https://raw.githubusercontent.com/nwt002tech/profit-hopper/main/extended_game_list.csv"

# App title
st.title("🎯 Profit Hopper")

# Load and process game data
@st.cache_data
def load_game_data():
    df = pd.read_csv(CSV_URL)
    numeric_fields = ["Min_Bet", "Volatility", "Bonus_Frequency", "Advantage_Play_Potential", "Expected_RTP"]
    for field in numeric_fields:
        df[field] = pd.to_numeric(df[field], errors="coerce")
    df.dropna(subset=["Name", "Type", "Min_Bet", "Expected_RTP"], inplace=True)
    return df

games_df = load_game_data()

# Sidebar inputs
st.sidebar.header("Session Settings")
total_bankroll = st.sidebar.number_input("Total Bankroll ($)", min_value=10.0, value=100.0, step=10.0)
num_sessions = st.sidebar.slider("Number of Sessions", 1, 10, 4)
session_bankroll = total_bankroll / num_sessions
max_bet = session_bankroll * 0.25

# Recommendation logic
def recommend_games(df, session_bankroll, max_bet):
    df = df.copy()
    df = df[df["Min_Bet"] <= max_bet]
    df["Score"] = (
        df["Expected_RTP"] * 0.4 +
        df["Advantage_Play_Potential"] * 0.3 +
        df["Bonus_Frequency"] * 0.2 +
        (1 - df["Volatility"] / 10) * 0.1
    )
    df["Stop_Loss"] = max((session_bankroll * 0.6), df["Min_Bet"]).round(2)
    df = df.sort_values(by="Score", ascending=False)
    return df

# Game Plan Display
st.subheader("🎮 Recommended Games")

try:
    recommended = recommend_games(games_df, session_bankroll, max_bet)
    if recommended.empty:
        st.warning("No games meet the criteria for your bankroll and session settings.")
    else:
        for _, row in recommended.iterrows():
            advantage_desc = "High" if row["Advantage_Play_Potential"] >= 0.8 else "Medium" if row["Advantage_Play_Potential"] >= 0.4 else "Low"
            volatility_desc = "Low" if row["Volatility"] <= 3 else "Medium" if row["Volatility"] <= 6 else "High"
            bonus_desc = "Frequent" if row["Bonus_Frequency"] >= 0.6 else "Occasional" if row["Bonus_Frequency"] >= 0.3 else "Rare"

            st.markdown(f"""
**{row['Name']}**
    • Type: {row["Type"]}
    • Min Bet: ${row["Min_Bet"]:.2f}
    • Stop Loss: ${row["Stop_Loss"]}
    • Advantage Play: {advantage_desc}
    • Volatility: {volatility_desc}
    • Bonus Frequency: {bonus_desc}
    • RTP: {row["Expected_RTP"]:.2f}%
    • Tips: {row["Tips"]}
""")
except Exception as e:
    st.error(f"Failed to load recommendations: {e}")
