
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Profit Hopper", layout="wide")

# Load game list
@st.cache_data
def load_data():
    return pd.read_csv("extended_game_list.csv")

games_df = load_data()

# Sidebar: Input total bankroll and session count
st.sidebar.header("Session Settings")
total_bankroll = st.sidebar.number_input("Total Bankroll ($)", min_value=1, value=100)
session_count = st.sidebar.number_input("Number of Sessions", min_value=1, value=5)
session_bankroll = round(total_bankroll / session_count, 2)
max_bet = round(session_bankroll * 0.25, 2)

# Recommend games
def recommend_games(df, session_bankroll, max_bet):
    df = df.copy()
    df = df.dropna(subset=["Volatility", "RTP", "Advantage_Play_Potential", "Bonus_Frequency"])

    df["Volatility"] = pd.to_numeric(df["Volatility"], errors="coerce")
    df["RTP"] = pd.to_numeric(df["RTP"], errors="coerce")
    df["Advantage_Play_Potential"] = pd.to_numeric(df["Advantage_Play_Potential"], errors="coerce")
    df["Bonus_Frequency"] = pd.to_numeric(df["Bonus_Frequency"], errors="coerce")

    df["Volatility"] = df["Volatility"].clip(1, 10)

    # Dynamic Stop Loss: Lower for low volatility, higher for high volatility
    df["Stop_Loss"] = round(session_bankroll * (0.8 - (df["Volatility"] - 1) * 0.04), 2)
    df["Stop_Loss"] = df["Stop_Loss"].clip(lower=df["Min_Bet"]).round(2)

    df["Score"] = (
        df["RTP"] * 0.4 +
        df["Bonus_Frequency"] * 0.2 +
        df["Advantage_Play_Potential"] * 0.2 +
        (10 - df["Volatility"]) * 0.2
    )

    df = df[df["Min_Bet"] <= max_bet]
    return df.sort_values(by="Score", ascending=False)

recommended = recommend_games(games_df, session_bankroll, max_bet)

# Main layout
st.title("🎯 Profit Hopper Game Plan")
st.markdown(f"**Total Bankroll:** ${total_bankroll} | **Sessions:** {session_count} | **Per Session:** ${session_bankroll} | **Max Bet/Session:** ${max_bet}")

st.subheader("📋 Recommended Games")
for _, row in recommended.iterrows():
    st.markdown(
        f"### 🎰 {row['Name']}  
"
        f"🏢 Best Casino Type: {row['Best_Casino_Type']}  
"
        f"🎯 Advantage Play: {row['Advantage_Play_Potential']}  
"
        f"💰 Min Bet: ${row['Min_Bet']}  
"
        f"🔄 Volatility: {row['Volatility']}  
"
        f"🎲 Bonus Frequency: {row['Bonus_Frequency']}  
"
        f"🧠 RTP: {row['RTP']}%  
"
        f"🛑 Stop Loss: ${row['Stop_Loss']}  
"
        f"📝 {row['Tips']}"
    )
