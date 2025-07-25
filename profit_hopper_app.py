
import streamlit as st
import pandas as pd

# Load game data directly from GitHub
csv_url = "https://raw.githubusercontent.com/nwt002tech/profit-hopper/main/extended_game_list.csv"
games_df = pd.read_csv(csv_url)

def recommend_games(df, session_bankroll, max_bet):
    df = df.copy()
    df = df[df["Min_Bet"] <= max_bet]
    df["Stop_Loss"] = session_bankroll * 0.6
    df["Score"] = (
        df["Bonus_Frequency"] * 0.4 +
        df["Advantage_Play_Potential"] * 0.2 +
        df["Hit_Frequency"] * 0.2 -
        df["Volatility"] * 0.2
    )
    return df.sort_values("Score", ascending=False).head(10)

# UI
st.title("Profit Hopper: Game Plan Assistant")

# Inputs
total_bankroll = st.number_input("Enter Total Bankroll ($)", value=100)
total_sessions = st.number_input("Enter Total Sessions", value=5)
session_bankroll = total_bankroll / total_sessions
max_bet = session_bankroll / 4

# Display Game Plan Summary
st.markdown("### Bankroll Status")
st.markdown(f"**Total Bankroll:** ${total_bankroll:.2f} | **Sessions:** {total_sessions}")

st.markdown("### Game Plan Summary")
st.markdown(f"**Bankroll/Session:** ${session_bankroll:.2f} | **Max Bet/Session:** ${max_bet:.2f}")

# Recommend Games
recommended = recommend_games(games_df, session_bankroll, max_bet)
st.markdown("### Recommended Games")

for _, row in recommended.iterrows():
    st.markdown(
        f"**{row['Name']}**  
"
        f"Min Bet: ${row['Min_Bet']} | Score: {row['Score']:.2f}  
"
        f"Stop-Loss: ${row['Stop_Loss']:.2f}  
"
        f"Tips: {row['Tips']}"
    )
