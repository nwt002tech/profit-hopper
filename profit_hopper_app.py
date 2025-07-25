
import streamlit as st
import pandas as pd

# Load extended game list from GitHub
@st.cache_data
def load_game_data():
    url = "https://raw.githubusercontent.com/nwt002tech/profit-hopper/main/extended_game_list.csv"
    return pd.read_csv(url)

def recommend_games(df, session_bankroll, max_bet):
    df = df.copy()
    df["Volatility"] = pd.to_numeric(df["Volatility"], errors="coerce")
    df["Bonus_Frequency"] = pd.to_numeric(df["Bonus_Frequency"], errors="coerce")
    df["RTP"] = pd.to_numeric(df["RTP"], errors="coerce")
    df["Min_Bet"] = pd.to_numeric(df["Min_Bet"], errors="coerce")

    df.dropna(subset=["Volatility", "Bonus_Frequency", "RTP", "Min_Bet"], inplace=True)

    df["Score"] = (
        df["RTP"] * 0.5 +
        df["Bonus_Frequency"] * 0.3 +
        (1 - df["Volatility"]) * 0.2
    )
    df = df[df["Min_Bet"] <= max_bet]
    df = df.sort_values(by="Score", ascending=False)
    df["Stop_Loss"] = (session_bankroll * 0.6).clip(lower=df["Min_Bet"]).round(2)
    return df.head(15)

# App layout
st.set_page_config(page_title="Profit Hopper", layout="wide")
st.title("🎯 Profit Hopper - Bankroll Strategy Assistant")

# Input fields
total_bankroll = st.number_input("Enter Total Bankroll ($)", min_value=10.0, value=100.0, step=10.0)
num_sessions = st.number_input("Enter Number of Sessions", min_value=1, value=5, step=1)

session_bankroll = round(total_bankroll / num_sessions, 2)
max_bet = round(session_bankroll * 0.25, 2)

# Bankroll Summary
st.markdown("### 💰 Bankroll Status")
st.markdown(f"**Total Bankroll:** ${total_bankroll:.2f} | **Sessions:** {num_sessions} | "
            f"**Bankroll/Session:** ${session_bankroll:.2f} | **Max Bet/Session:** ${max_bet:.2f}")

# Load data and get recommendations
games_df = load_game_data()
recommended = recommend_games(games_df, session_bankroll, max_bet)

# Display Recommendations
st.markdown("### ✅ Recommended Games")
for idx, row in recommended.iterrows():
    st.markdown(f"""
**{row['Name']}**
🎰 Min Bet: ${row['Min_Bet']} | 🛑 Stop-Loss: ${row['Stop_Loss']}
📝 {row['Tips']}""")
