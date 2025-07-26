import streamlit as st
import pandas as pd

# Load game list from GitHub
CSV_URL = "https://raw.githubusercontent.com/nwt002tech/profit-hopper/main/extended_game_list.csv"
df = pd.read_csv(CSV_URL)

# Session and bankroll settings
total_bankroll = 100.00
total_sessions = 5
session_bankroll = total_bankroll / total_sessions
max_bet = session_bankroll * 0.25

# Game scoring and recommendation
def recommend_games(df, session_bankroll, max_bet):
    df = df.copy()
    df = df.dropna(subset=["Volatility", "Bonus_Frequency", "Advantage_Play_Potential"])
    df["Score"] = (
        df["Volatility"] * -0.4 +
        df["Bonus_Frequency"] * 0.5 +
        df["Advantage_Play_Potential"] * 0.2
    )
    df["Stop_Loss"] = pd.Series([max(session_bankroll * 0.6, row["Min_Bet"]) for _, row in df.iterrows()]).round(2)
    df = df[df["Min_Bet"] <= max_bet]
    return df.sort_values("Score", ascending=False).head(10)

recommended = recommend_games(df, session_bankroll, max_bet)

# Layout with Game Plan, Tracker, Summary
st.title("🎯 Profit Hopper")

st.markdown("### 💰 Bankroll Status")
st.markdown(f"**Total Bankroll:** ${total_bankroll:.2f} | **Sessions:** {total_sessions}")

st.markdown("### 🧠 Game Plan Summary")
st.markdown(f"**Bankroll/Session:** ${session_bankroll:.2f} | **Max Bet/Session:** ${max_bet:.2f}")

tab1, tab2, tab3 = st.tabs(["📋 Game Plan", "🧾 Tracker", "📊 Summary"])

with tab1:
    st.subheader("🎮 Recommended Games")
    for _, row in recommended.iterrows():
        st.markdown(
            f"**{row['Name']}**
"
            f"🎰 Category: {row['Category']}

"
            f"📈 Volatility: {row['Volatility']} | 🎁 Bonus Frequency: {row['Bonus_Frequency']}
"
            f"🧠 AP Potential: {row['Advantage_Play_Potential']} | 💸 Stop-Loss: ${row['Stop_Loss']}
"
            f"📝 {row['Tips']}
"
            "---"
        )

with tab2:
    st.subheader("🔄 Session Tracker")
    st.info("Tracker coming soon!")

with tab3:
    st.subheader("📈 Summary")
    st.success("Summary stats will be here.")
