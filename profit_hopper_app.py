
import streamlit as st
import pandas as pd

# Load data
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/nwt002tech/profit-hopper/main/extended_game_list.csv"
    return pd.read_csv(url)

# Recommend games function
def recommend_games(df, session_bankroll, max_bet):
    numeric_fields = ["Volatility", "Bonus_Frequency", "RTP", "Advantage_Play_Potential", "Min_Bet"]
    for field in numeric_fields:
        df[field] = pd.to_numeric(df[field], errors="coerce")

    # Example score (you can customize this)
    df["Score"] = (
        df["RTP"] * 0.3 +
        df["Bonus_Frequency"] * 0.25 +
        df["Advantage_Play_Potential"] * 0.2 +
        df["Volatility"] * -0.15
    )

    filtered = df[df["Min_Bet"] <= max_bet].copy()
    filtered = filtered.sort_values(by="Score", ascending=False)

    # Set Stop Loss dynamically based on session bankroll
    filtered["Stop_Loss"] = round(session_bankroll * 0.6, 2)

    return filtered

# Streamlit UI
st.title("🎯 Profit Hopper")

total_bankroll = st.number_input("Enter your total bankroll:", min_value=10.0, value=100.0)
num_sessions = st.number_input("Enter number of sessions:", min_value=1, value=5)

session_bankroll = round(total_bankroll / num_sessions, 2)
max_bet = round(session_bankroll * 0.25, 2)

st.markdown(f"💰 **Session Bankroll:** ${session_bankroll}")
st.markdown(f"🎯 **Max Bet per Game:** ${max_bet}")

games_df = load_data()

try:
    recommended = recommend_games(games_df, session_bankroll, max_bet)

    st.subheader("📋 Recommended Games")
    for _, row in recommended.iterrows():
        st.markdown(f"""
        **{row['Name']}**
        🎰 Type: {row['Best_Casino_Type']}  
        💸 Min Bet: ${row['Min_Bet']}  
        🚫 Stop Loss: ${row['Stop_Loss']}  
        🧠 Advantage Play: {row['Advantage_Play_Potential']}  
        🎲 Volatility: {row['Volatility']}  
        🎁 Bonus Frequency: {row['Bonus_Frequency']}  
        🔢 RTP: {row['RTP']}  
        💡 Tips: {row['Tips']}
        """)
except Exception as e:
    st.error(f"Failed to load recommendations: {e}")
