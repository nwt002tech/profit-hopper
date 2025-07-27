
import streamlit as st
import pandas as pd

GAME_LIST_URL = "https://raw.githubusercontent.com/nwt002tech/profit-hopper/main/extended_game_list.csv"

def recommend_games(df, session_bankroll, max_bet):
    numeric_fields = [
        "Min_Bet", "Volatility", "Bonus_Frequency", "Expected_RTP",
        "Advantage_Play_Potential"
    ]
    for field in numeric_fields:
        df[field] = pd.to_numeric(df[field], errors="coerce")

    df["Stop_Loss"] = (session_bankroll * 0.6).round(2).clip(lower=df["Min_Bet"])
    df["Score"] = (
        df["Expected_RTP"] * 0.4 +
        df["Advantage_Play_Potential"] * 0.2 +
        df["Bonus_Frequency"] * 0.2 +
        df["Volatility"].apply(lambda x: 1 / x if x > 0 else 0) * 0.1
    )
    filtered = df[df["Min_Bet"] <= max_bet].copy()
    recommended = filtered.sort_values("Score", ascending=False).head(10)
    return recommended

st.set_page_config(page_title="Profit Hopper", layout="centered")
st.title("Profit Hopper")

total_bankroll = st.number_input("Total Bankroll", min_value=1.0, value=100.0)
num_sessions = st.number_input("Number of Sessions", min_value=1, value=5)

session_bankroll = round(total_bankroll / num_sessions, 2)
max_bet = round(session_bankroll * 0.25, 2)

st.markdown(f"### Session Bankroll: ${session_bankroll} | Max Bet: ${max_bet}")

try:
    df = pd.read_csv(GAME_LIST_URL)
    recommended = recommend_games(df, session_bankroll, max_bet)

    st.subheader("Recommended Games")
    for _, row in recommended.iterrows():
        st.markdown(f"**{row['Name']}**")
        st.markdown(
            f"""<div style='padding-left: 16px; line-height: 1.2em'>
            - Type: {row['Best_Casino_Type']}<br>
            - Min Bet: ${row['Min_Bet']}<br>
            - Stop Loss: ${row['Stop_Loss']}<br>
            - Advantage Play: {row['Advantage_Play_Potential']}<br>
            - Volatility: {row['Volatility']}<br>
            - Bonus Frequency: {row['Bonus_Frequency']}<br>
            - RTP: {row['Expected_RTP']}<br>
            - Tips: {row['Tips']}
            </div>""",
            unsafe_allow_html=True
        )
except Exception as e:
    st.error(f"Failed to load recommendations: {e}")
