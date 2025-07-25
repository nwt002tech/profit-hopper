import streamlit as st
import pandas as pd

# Load game list from external CSV
@st.cache_data
def load_games():
    return pd.read_csv("extended_game_list.csv")

# Game recommendation logic
def recommend_games(df, session_bankroll, max_bet):
    df = df.copy()
    df = df[df["Min_Bet"] <= max_bet]
    df["Stop_Loss"] = df["Min_Bet"].apply(lambda x: max(round(session_bankroll * 0.6, 2), x))
    df["Score"] = (
        df["RTP"] * 0.4 +
        df["Bonus_Frequency"] * 0.3 +
        df["Advantage_Play_Potential"] * 0.2 +
        df["Volatility"] * -0.1
    )
    return df.sort_values(by="Score", ascending=False).head(10)

# UI setup
st.title("🎯 Profit Hopper - Bankroll Strategy Assistant")

# Sidebar inputs
st.sidebar.header("💰 Bankroll Settings")
total_bankroll = st.sidebar.number_input("Total Bankroll ($)", min_value=20.0, value=100.0, step=10.0)
total_sessions = st.sidebar.slider("Number of Sessions", min_value=1, max_value=20, value=5)
session_bankroll = total_bankroll / total_sessions
max_bet = round(session_bankroll * 0.25, 2)

# Display summary
st.markdown("### 💰 Bankroll Status")
st.markdown(f"**Total Bankroll:** ${total_bankroll:.2f} | **Sessions:** {total_sessions}")
st.markdown("### 🎯 Game Plan Summary")
st.markdown(f"**Bankroll/Session:** ${session_bankroll:.2f} | **Max Bet/Session:** ${max_bet:.2f}")

# Load games and recommend
games_df = load_games()
recommended = recommend_games(games_df, session_bankroll, max_bet)

# Show recommendations
st.markdown("## ✅ Recommended Games")
for idx, row in recommended.iterrows():
    st.markdown(f"""**{row['Name']}**
🎰 Min Bet: ${row['Min_Bet']} | 🛑 Stop-Loss: ${row['Stop_Loss']:.2f}
📝 {row['Tips']}""")
