import streamlit as st
import pandas as pd

# Load the game data
games_df = pd.read_csv("extended_game_list.csv")

# Set up the page
st.set_page_config(page_title="Profit Hopper", layout="wide")
st.title("🎯 Profit Hopper – Smart Bankroll Strategy App")

# Sidebar inputs
total_bankroll = st.sidebar.number_input("Enter your total bankroll ($)", min_value=1, value=100)
num_sessions = st.sidebar.slider("Number of planned sessions", min_value=1, max_value=50, value=5)
session_bankroll = round(total_bankroll / num_sessions, 2)
st.sidebar.markdown(f"💰 **Bankroll per session: ${session_bankroll}**")

max_bet = st.sidebar.number_input("Max bet per spin ($)", min_value=1.0, value=5.0)
min_score = st.sidebar.slider("Minimum recommendation score", min_value=0.0, max_value=10.0, value=5.0)

# Recommendation engine
def recommend_games(df, session_bankroll, max_bet):
    df = df.copy()
    # Convert all necessary fields to numeric (if they aren’t already)
    numeric_fields = [
        "RTP", "Volatility", "Bonus_Frequency",
        "Advantage_Play_Potential", "Min_Bet", "Max_Bet"
    ]
    for field in numeric_fields:
        df[field] = pd.to_numeric(df[field], errors="coerce")

    # Drop rows with missing critical values
    df = df.dropna(subset=numeric_fields)

    # Scoring model (weights can be adjusted)
    df["Score"] = (
        df["RTP"] * 0.4 +
        (10 - df["Volatility"]) * 0.2 +
        df["Bonus_Frequency"] * 0.1 +
        df["Advantage_Play_Potential"] * 0.2
    )

    # Calculate dynamic stop-loss
    df["Stop_Loss"] = (session_bankroll * 0.6).clip(lower=df["Min_Bet"]).round(2)

    # Filter based on max bet and score threshold
    filtered = df[
        (df["Max_Bet"] <= max_bet) &
        (df["Score"] >= min_score)
    ].sort_values(by="Score", ascending=False)

    return filtered

# Main app
recommended = recommend_games(games_df, session_bankroll, max_bet)

st.header("🎮 Recommended Games This Session")
if recommended.empty:
    st.warning("No games meet your criteria. Try adjusting your max bet or score threshold.")
else:
    for _, row in recommended.iterrows():
        st.markdown(f"""### 🎰 {row['Name']}
**Type:** {row['Best_Casino_Type']}  
**Volatility:** {row['Volatility']}  
**RTP:** {row['RTP']}  
**Bonus Frequency:** {row['Bonus_Frequency']}  
**Advantage Play Potential:** {row['Advantage_Play_Potential']}  
**Recommended Denom:** {row['Recommended_Denom']}  
**Min Bet:** ${row['Min_Bet']}  
**Max Bet:** ${row['Max_Bet']}  
**Stop Loss:** ${row['Stop_Loss']}  

📝 {row['Tips']}""")

# Bankroll summary
st.sidebar.markdown("---")
st.sidebar.subheader("📊 Session Summary")
st.sidebar.markdown(f"**Total Bankroll:** ${total_bankroll}")
st.sidebar.markdown(f"**Sessions:** {num_sessions}")
st.sidebar.markdown(f"**Bankroll per Session:** ${session_bankroll}")
st.sidebar.markdown(f"**Max Bet per Session:** ${max_bet}")
