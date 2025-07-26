
import streamlit as st
import pandas as pd

# Load data directly from GitHub
csv_url = "https://raw.githubusercontent.com/nwt002tech/profit-hopper/main/extended_game_list.csv"
games_df = pd.read_csv(csv_url)

# Session settings (replace with actual session logic if needed)
total_bankroll = 120
num_sessions = 6
session_bankroll = total_bankroll / num_sessions
max_bet = round(session_bankroll * 0.25, 2)

def recommend_games(df, session_bankroll, max_bet):
    numeric_fields = [
        "Volatility", "Bonus_Frequency", "Expected_RTP",
        "Advantage_Play_Potential", "Min_Bet"
    ]
    for field in numeric_fields:
        df[field] = pd.to_numeric(df[field], errors="coerce")

    df = df.dropna(subset=numeric_fields)
    df["Stop_Loss"] = round(max(session_bankroll * 0.6, df["Min_Bet"].min()), 2)

    df["Score"] = (
        df["Advantage_Play_Potential"] * 0.3 +
        (1 - df["Volatility"] / 5) * 0.2 +
        df["Bonus_Frequency"] * 0.2 +
        df["Expected_RTP"] * 0.2 +
        (1 - df["Min_Bet"] / session_bankroll) * 0.1
    )

    df = df.sort_values(by="Score", ascending=False)
    return df[df["Min_Bet"] <= max_bet].head(10)

recommended = recommend_games(games_df, session_bankroll, max_bet)

st.title("🎯 Profit Hopper: Smart Game Recommender")
st.subheader(f"💰 Total Bankroll: ${total_bankroll}")
st.subheader(f"🎯 Session Bankroll: ${session_bankroll:.2f} | 🎯 Max Bet: ${max_bet:.2f}")

st.markdown("---")
st.header("🧠 Recommended Games")
if recommended.empty:
    st.warning("No games found that match the criteria.")
else:
    for _, row in recommended.iterrows():
        st.markdown(
            f"""
**{row['Name']}**

🎰 Type: {row['Best_Casino_Type']}
💸 Min Bet: {row['Min_Bet']}
🚫 Stop Loss: {row['Stop_Loss']:.2f}
🧠 Advantage Play: {row['Advantage_Play_Potential']}
🎲 Volatility: {row['Volatility']}
🎁 Bonus Frequency: {row['Bonus_Frequency']}
🔢 RTP: {row['Expected_RTP']}
💡 Tips: {row['Tips']}
""",
            unsafe_allow_html=True,
        )
