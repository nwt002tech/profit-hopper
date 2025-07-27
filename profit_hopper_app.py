
import streamlit as st
import pandas as pd

@st.cache_data
def load_game_data():
    url = "https://raw.githubusercontent.com/nwt002tech/profit-hopper/main/extended_game_list.csv"
    return pd.read_csv(url)

def recommend_games(df, session_bankroll, max_bet):
    fields_to_numeric = ["Min_Bet", "Volatility", "Advantage_Play_Potential", "Bonus_Frequency", "RTP"]
    for field in fields_to_numeric:
        if field in df.columns:
            df[field] = pd.to_numeric(df[field], errors="coerce")

    df["Score"] = (
        df["Advantage_Play_Potential"].fillna(0) * 0.4 +
        (1 - df["Volatility"].fillna(0) / 5) * 0.2 +
        df["Bonus_Frequency"].fillna(0) * 0.2 +
        df["RTP"].fillna(0) / 100 * 0.2
    )

    df["Stop_Loss"] = (session_bankroll * 0.6).round(2)
    df = df.sort_values(by="Score", ascending=False)
    return df

st.set_page_config(page_title="Profit Hopper", layout="centered")
st.title("🎰 Profit Hopper – Game Plan")

total_bankroll = st.number_input("Total Bankroll ($)", min_value=1, value=100)
num_sessions = st.number_input("Number of Sessions", min_value=1, value=5)
session_bankroll = round(total_bankroll / num_sessions, 2)
max_bet = round(session_bankroll / 4, 2)

st.markdown(f"### 💰 Session Bankroll: ${session_bankroll} | 🎯 Max Bet: ${max_bet}")

try:
    games_df = load_game_data()
    recommended = recommend_games(games_df, session_bankroll, max_bet)

    for _, row in recommended.iterrows():
        st.markdown(f"**{row['Name']}**")
        st.markdown(
            f"""
<div style='margin-left: 20px'>
<p>🎰 Type: {row['Best_Casino_Type']}</p>
<p>💸 Min Bet: {row['Min_Bet']}</p>
<p>🚫 Stop Loss: {row['Stop_Loss']}</p>
<p>🧠 Advantage Play: {row['Advantage_Play_Potential']}</p>
<p>🎲 Volatility: {row['Volatility']}</p>
<p>🎁 Bonus Frequency: {row['Bonus_Frequency']}</p>
<p>🔢 RTP: {row['RTP']}</p>
<p>💡 Tips: {row['Tips']}</p>
</div>
            """, unsafe_allow_html=True
        )

except Exception as e:
    st.error(f"Failed to load recommendations: {e}")
