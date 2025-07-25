
import streamlit as st
import pandas as pd

# Load the external game list
@st.cache_data
def load_game_data():
    url = "https://raw.githubusercontent.com/nwt002tech/profit-hopper/main/extended_game_list.csv"
    return pd.read_csv(url)

def recommend_games(df, session_bankroll, max_bet):
    df = df.copy()
    # Calculate stop-loss dynamically
    df["Stop_Loss"] = (session_bankroll * 0.6).round(2)
    df["Stop_Loss"] = df[["Stop_Loss", "Min_Bet"]].max(axis=1)

    # Calculate a score based on weighted criteria
    df["Score"] = (
        df["RTP"] * 0.3 +
        df["Bonus_Frequency"] * 0.2 +
        df["Advantage_Play_Potential"] * 0.2 +
        (1 - df["Volatility"]) * 0.3
    )
    df = df.sort_values("Score", ascending=False)
    df["Score"] = df["Score"].round(2)
    return df.head(10)

# Session defaults
if "session_log" not in st.session_state:
    st.session_state["session_log"] = []

st.title("Profit Hopper App")
st.markdown("#### Smart bankroll strategy and game recommendations")

# Game Plan summary
total_bankroll = st.number_input("Enter total bankroll:", min_value=10.0, value=100.0, step=10.0)
total_sessions = st.number_input("Number of sessions:", min_value=1, value=5, step=1)
session_bankroll = total_bankroll / total_sessions
max_bet = session_bankroll * 0.25

st.markdown(f"**Bankroll/Session:** ${session_bankroll:.2f} | **Max Bet/Session:** ${max_bet:.2f}")

# Load and recommend
games_df = load_game_data()
recommended = recommend_games(games_df, session_bankroll, max_bet)

st.subheader("Recommended Games")
for idx, row in recommended.iterrows():
    st.markdown(f"**{row['Name']}**\nMin Bet: ${row['Min_Bet']} | Stop-Loss: ${row['Stop_Loss']}\nScore: {row['Score']}\nTips: {row['Tips']}")
