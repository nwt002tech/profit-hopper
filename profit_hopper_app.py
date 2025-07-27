
import streamlit as st
import pandas as pd

# App title
st.set_page_config(page_title="Profit Hopper", layout="wide")
st.title("💰 Profit Hopper")
st.caption("Your personalized casino strategy assistant.")

# Load game list from GitHub
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/nwt002tech/profit-hopper/main/extended_game_list.csv"
    return pd.read_csv(url)

games_df = load_data()

# User inputs
total_bankroll = st.number_input("Total Bankroll ($)", min_value=1.0, value=100.0, step=1.0)
num_sessions = st.number_input("Number of Sessions", min_value=1, value=5, step=1)
session_bankroll = round(total_bankroll / num_sessions, 2)
max_bet = round(session_bankroll * 0.25, 2)

st.markdown(f"**💼 Session Bankroll:** ${session_bankroll} &nbsp;&nbsp;&nbsp; 🎯 **Max Bet/Game:** ${max_bet}")

# Game recommendation logic
def recommend_games(df, session_bankroll, max_bet):
    numeric_fields = [
        "Advantage_Play_Potential", "Volatility", "Bonus_Frequency",
        "Expected_RTP", "Min_Bet"
    ]
    for field in numeric_fields:
        df[field] = pd.to_numeric(df[field], errors="coerce")

    df["Stop_Loss"] = session_bankroll * 0.6
    df["Score"] = (
        df["Advantage_Play_Potential"] * 0.2 +
        (1 / (df["Volatility"] + 1e-5)) * 0.2 +
        df["Bonus_Frequency"] * 0.2 +
        df["Expected_RTP"] * 0.2 +
        (1 - (df["Min_Bet"] / max_bet).clip(upper=1)) * 0.2
    )

    filtered = df[df["Min_Bet"] <= max_bet].copy()
    filtered = filtered.sort_values("Score", ascending=False).reset_index(drop=True)
    return filtered

try:
    recommended = recommend_games(games_df, session_bankroll, max_bet)

    for idx, row in recommended.iterrows():
        st.markdown(
            f"""**{row['Name']}**<br>
&nbsp;&nbsp;🎰 Type: {row['Type']}<br>
&nbsp;&nbsp;💸 Min Bet: {row['Min_Bet']}<br>
&nbsp;&nbsp;🚫 Stop Loss: {round(row['Stop_Loss'], 2)}<br>
&nbsp;&nbsp;🧠 Advantage Play: {row['Advantage_Play_Potential']}<br>
&nbsp;&nbsp;🎲 Volatility: {row['Volatility']}<br>
&nbsp;&nbsp;🎁 Bonus Frequency: {row['Bonus_Frequency']}<br>
&nbsp;&nbsp;🔢 RTP: {row['Expected_RTP']}<br>
&nbsp;&nbsp;💡 Tips: {row['Tips']}<br><br>
""",
            unsafe_allow_html=True,
        )

except Exception as e:
    st.error(f"Failed to load recommendations: {e}")
