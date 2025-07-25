
import streamlit as st
import pandas as pd

# Load game data from extended_game_list.csv
games_df = pd.read_csv("extended_game_list.csv")

# Bankroll and session settings
total_bankroll = 100.00
total_sessions = 5
session_bankroll = total_bankroll / total_sessions
max_bet = session_bankroll * 0.25

# Filter and score games
def recommend_games(df, session_bankroll, max_bet):
    df = df.copy()
    df["Stop_Loss"] = pd.DataFrame({
        "A": [session_bankroll * 0.6] * len(df),
        "B": df["Min_Bet"]
    }).max(axis=1).round(2)
    df["Score"] = (
        df["Bonus_Frequency"] * 0.4 +
        df["Advantage_Play_Potential"] * 0.2 +
        df["RTP"] * 0.2 +
        (100 - df["Volatility"]) * 0.2
    )
    filtered = df[(df["Min_Bet"] <= max_bet) & (df["Stop_Loss"] >= df["Min_Bet"])]
    return filtered.sort_values(by="Score", ascending=False).reset_index(drop=True)

recommended = recommend_games(games_df, session_bankroll, max_bet)

# Layout display
st.markdown("### 💰 Bankroll Status")
st.markdown(f"**Total Bankroll:** ${total_bankroll:.2f} | **Sessions:** {total_sessions}")

st.markdown("### 🎯 Game Plan Summary")
st.markdown(f"**Bankroll/Session:** ${session_bankroll:.2f} | **Max Bet/Session:** ${max_bet:.2f}")

st.markdown("### Recommended Games")
for idx, row in recommended.iterrows():
    st.markdown(
        f"""**{row['Name']}**
- Min Bet: ${row['Min_Bet']:.2f}
- Stop-Loss: ${row['Stop_Loss']:.2f}
- Volatility: {row['Volatility']}
- RTP: {row['RTP']}%
- Bonus Frequency: {row['Bonus_Frequency']}
- Advantage Play Potential: {row['Advantage_Play_Potential']}
- Tips: {row['Tips']}"""
    )
