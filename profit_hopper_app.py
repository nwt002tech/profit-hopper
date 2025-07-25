
import streamlit as st
import pandas as pd
import requests

# === CONFIGURATION ===
CSV_URL = "https://raw.githubusercontent.com/nwt002tech/profit-hopper/main/extended_game_list.csv"

# === FUNCTIONS ===
@st.cache_data
def load_game_data():
    try:
        return pd.read_csv(CSV_URL)
    except Exception as e:
        st.error(f"Error loading game data: {e}")
        return pd.DataFrame()

def recommend_games(df, session_bankroll, max_bet):
    df = df.copy()
    df = df[df["Min_Bet"] <= max_bet]

    # Score calculation based on weighted criteria
    df["Score"] = (
        df["Volatility"] * -0.4 +
        df["Bonus_Frequency"] * 0.3 +
        df["RTP"] * 0.2 +
        df["Advantage_Play_Potential"] * 0.1
    )
    df = df.sort_values(by="Score", ascending=False)

    # Stop-Loss calculated based on risk + session bankroll
    df["Stop_Loss"] = (session_bankroll * 0.6).clip(lower=df["Min_Bet"]).round(2)
    return df.head(10)

# === APP STATE ===
st.set_page_config(page_title="Profit Hopper", layout="wide")
st.title("🎯 Profit Hopper – Smart Bankroll Strategy")

# === INPUTS ===
st.sidebar.header("📊 Strategy Settings")
total_bankroll = st.sidebar.number_input("Total Starting Bankroll ($)", min_value=20, value=100)
total_sessions = st.sidebar.slider("Number of Sessions", min_value=1, max_value=20, value=5)

session_bankroll = round(total_bankroll / total_sessions, 2)
max_bet = round(session_bankroll * 0.25, 2)

# === LOAD GAME DATA ===
game_df = load_game_data()
if game_df.empty:
    st.stop()

# === GAME PLAN TAB ===
tab1, tab2, tab3 = st.tabs(["📋 Game Plan", "🧾 Tracker", "📈 Summary"])

with tab1:
    st.markdown("### 💼 Bankroll Status")
    st.markdown(f"**Total Bankroll:** ${total_bankroll:.2f} | **Sessions:** {total_sessions} | **Session Bankroll:** ${session_bankroll:.2f} | **Max Bet:** ${max_bet:.2f}")

    st.markdown("### 🧠 Recommended Games")
    recommended = recommend_games(game_df, session_bankroll, max_bet)
    for idx, row in recommended.iterrows():
        st.markdown(f"""**{row['Name']}**
🎰 Min Bet: ${row['Min_Bet']} | 🛑 Stop-Loss: ${row['Stop_Loss']}
📝 {row['Tips']}
""")

with tab2:
    st.markdown("### 🧾 Session Tracker (Coming Soon)")

with tab3:
    st.markdown("### 📈 Summary & Log (Coming Soon)")
