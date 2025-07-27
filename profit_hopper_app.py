
import streamlit as st
import pandas as pd
import requests

# App Configuration
st.set_page_config(page_title="Profit Hopper", layout="wide")

st.title("🎯 Profit Hopper")
st.markdown("##### Smarter game recommendations based on your bankroll")

# Load game data from GitHub
GITHUB_CSV_URL = "https://raw.githubusercontent.com/nwt002tech/profit-hopper/main/extended_game_list.csv"
try:
    df = pd.read_csv(GITHUB_CSV_URL)
except Exception as e:
    st.error(f"Failed to load game list: {e}")
    st.stop()

# User Inputs
total_bankroll = st.number_input("Total Bankroll ($)", min_value=10.0, value=100.0, step=10.0)
num_sessions = st.number_input("Number of Sessions", min_value=1, value=5, step=1)
session_bankroll = round(total_bankroll / num_sessions, 2)
max_bet = round(session_bankroll * 0.25, 2)

st.markdown(f"**📊 Bankroll per Session:** ${session_bankroll}")
st.markdown(f"**🎯 Max Bet per Game:** ${max_bet}")

# Recommendation Logic
def recommend_games(df, session_bankroll, max_bet):
    try:
        for field in ["Min_Bet", "Volatility", "Bonus_Frequency", "Expected_RTP", "Advantage_Play_Potential"]:
            df[field] = pd.to_numeric(df[field], errors="coerce").fillna(0)

        df["Stop_Loss"] = df["Min_Bet"].apply(lambda x: max(round(session_bankroll * 0.6, 2), x))

        df["Score"] = (
            df["Advantage_Play_Potential"] * 0.3 +
            (1 / (df["Volatility"] + 1e-6)) * 0.2 +
            df["Bonus_Frequency"] * 0.2 +
            df["Expected_RTP"] * 0.2 +
            (1 - df["Min_Bet"] / session_bankroll) * 0.1
        )

        filtered = df[df["Min_Bet"] <= max_bet].sort_values("Score", ascending=False)
        return filtered.head(20)

    except Exception as e:
        st.error(f"Failed to load recommendations: {e}")
        return pd.DataFrame()

# Display Recommendations
recommended = recommend_games(df, session_bankroll, max_bet)
if not recommended.empty:
    for _, row in recommended.iterrows():
        detail_lines = [
            f"**{row['Name']}**",
            f"&nbsp;&nbsp;- Type: {row['Type']}",
            f"&nbsp;&nbsp;- Min Bet: ${row['Min_Bet']}",
            f"&nbsp;&nbsp;- Stop Loss: ${row['Stop_Loss']}",
            f"&nbsp;&nbsp;- Advantage Play: {row['Advantage_Play_Potential']}",
            f"&nbsp;&nbsp;- Volatility: {row['Volatility']}",
            f"&nbsp;&nbsp;- Bonus Frequency: {row['Bonus_Frequency']}",
            f"&nbsp;&nbsp;- RTP: {row['Expected_RTP']}%",
            f"&nbsp;&nbsp;- Tips: {row['Tips']}"
        ]
        st.markdown("<br>".join(detail_lines), unsafe_allow_html=True)
else:
    st.warning("No games meet the criteria for your bankroll and session settings.")
