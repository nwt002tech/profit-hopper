
import streamlit as st
import pandas as pd

def recommend_games(df, session_bankroll, max_bet):
    df = df.copy()
    numeric_fields = ["Volatility", "Bonus_Frequency", "RTP", "Min_Bet", "Advantage_Play_Potential"]
    for field in numeric_fields:
        df[field] = pd.to_numeric(df[field], errors="coerce")
    df.dropna(subset=numeric_fields, inplace=True)
    df = df[df["Min_Bet"] <= max_bet]
    df["Score"] = (
        df["RTP"] * 0.4 +
        df["Bonus_Frequency"] * 0.2 +
        df["Advantage_Play_Potential"] * 0.2 +
        (1 - df["Volatility"]) * 0.2
    )
    return df.sort_values("Score", ascending=False).reset_index(drop=True)

st.set_page_config(page_title="Profit Hopper", layout="wide")
st.title("💰 Profit Hopper: Smart Casino Game Recommendations")

games_df = pd.read_csv("extended_game_list.csv")

st.sidebar.header("🎯 Session Settings")
total_bankroll = st.sidebar.number_input("Total Bankroll ($)", min_value=10, value=100)
sessions = st.sidebar.slider("Number of Sessions", 1, 20, 5)
session_bankroll = round(total_bankroll / sessions, 2)
max_bet = round(session_bankroll * 0.25, 2)

recommended = recommend_games(games_df, session_bankroll, max_bet)

tab1, tab2, tab3 = st.tabs(["📋 Game Plan", "📈 Tracker", "📊 Summary"])

with tab1:
    st.subheader("🎮 Recommended Games")
    st.markdown(f"**Bankroll per Session:** ${session_bankroll} | **Max Bet Allowed:** ${max_bet}")
    for _, row in recommended.iterrows():
        st.markdown(f"""
**🎰 {row['Name']}**
- 📊 RTP: {row['RTP']}%
- 📈 Volatility: {row['Volatility']}
- 🎁 Bonus Frequency: {row['Bonus_Frequency']}
- Minimum Bet: ${row['Min_Bet']}
- Advantage Play: {row['Advantage_Play_Potential']}
- Best Casino 🎰 Type: {row.get('Best_Casino_Type', 'N/A')}
- 💡 Tips: {row.get('Tips', 'N/A')}
---
""")

with tab2:
    st.subheader("📈 Session Tracker (Coming Soon)")

with tab3:
    st.subheader("📊 Summary")
    st.markdown(f"""
- Total Bankroll: **${total_bankroll}**
- Sessions: **{sessions}**
- Session Bankroll: **${session_bankroll}**
- Max Bet per Game: **${max_bet}**
""")
