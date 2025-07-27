
import streamlit as st
import pandas as pd

@st.cache_data
def load_game_data():
    url = "https://github.com/nwt002tech/profit-hopper/raw/2b42fd9699f541c3532363d80f84b6f8ef73ba60/extended_game_list.csv"
    df = pd.read_csv(url)
    numeric_fields = ["Min_Bet", "Advantage_Play_Potential", "Volatility", "Bonus_Frequency", "Expected_RTP"]
    for field in numeric_fields:
        df[field] = pd.to_numeric(df[field], errors="coerce")
    return df.dropna(subset=["Name", "Min_Bet"])

def describe_field(value, field):
    if field == "Advantage_Play_Potential":
        if value >= 0.8: return "Very High"
        elif value >= 0.6: return "High"
        elif value >= 0.4: return "Moderate"
        else: return "Low"
    if field == "Volatility":
        if value >= 4: return "Very High"
        elif value >= 3: return "High"
        elif value >= 2: return "Medium"
        else: return "Low"
    if field == "Bonus_Frequency":
        if value >= 0.5: return "Very Frequent"
        elif value >= 0.3: return "Frequent"
        elif value >= 0.1: return "Occasional"
        else: return "Rare"
    return "N/A"

def recommend_games(df, session_bankroll, max_bet):
    df["Score"] = (
        df["Advantage_Play_Potential"] * 0.4 +
        (1 - df["Volatility"] / 5) * 0.3 +
        df["Bonus_Frequency"] * 0.3
    )
    filtered = df[df["Min_Bet"] <= max_bet].copy()
    filtered["Stop_Loss"] = (session_bankroll * 0.6).round(2)
    return filtered.sort_values(by="Score", ascending=False).reset_index(drop=True)

def render_game_details(row):
    return f"""
    🎰 **{row['Name']}**
    🏷️ Type: {row['Type']}
    💸 Min Bet: {row['Min_Bet']}
    🚫 Stop Loss: {row['Stop_Loss']}
    🧠 Advantage Play: {describe_field(row['Advantage_Play_Potential'], 'Advantage_Play_Potential')}
    🎲 Volatility: {describe_field(row['Volatility'], 'Volatility')}
    🎁 Bonus Frequency: {describe_field(row['Bonus_Frequency'], 'Bonus_Frequency')}
    🔢 RTP: {row['Expected_RTP']}%
    💡 Tips: {row['Tips']}
    """

st.title("🎯 Profit Hopper: Game Recommendations")

total_bankroll = st.number_input("Enter your total bankroll ($)", min_value=5.0, value=100.0, step=5.0)
num_sessions = st.slider("Number of sessions to split your bankroll into", 1, 10, 4)
session_bankroll = total_bankroll / num_sessions
max_bet = session_bankroll * 0.25

try:
    games_df = load_game_data()
    recommended = recommend_games(games_df, session_bankroll, max_bet)
    st.markdown(f"### Recommended Games (Session Bankroll: ${session_bankroll:.2f}, Max Bet: ${max_bet:.2f})")
    if not recommended.empty:
        for _, row in recommended.iterrows():
            st.markdown(render_game_details(row))
            st.markdown("---")
    else:
        st.warning("No games meet the criteria for your bankroll and session settings.")
except Exception as e:
    st.error(f"Failed to load recommendations: {e}")
