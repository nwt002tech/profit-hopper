import streamlit as st
import pandas as pd

# Load external game list
csv_url = "https://raw.githubusercontent.com/nwt002tech/profit-hopper/main/extended_game_list.csv"
games_df = pd.read_csv(csv_url)

# Map Advantage_Play_Potential values
potential_map = {"Low": 1, "Medium": 2, "High": 3}
games_df["Advantage_Play_Potential"] = games_df["Advantage_Play_Potential"].map(potential_map).fillna(1)

# Sidebar inputs
st.sidebar.header("Bankroll Settings")
total_bankroll = st.sidebar.number_input("Total Bankroll ($)", min_value=20.0, value=100.0, step=10.0)
total_sessions = st.sidebar.slider("Total Sessions", min_value=1, max_value=20, value=5)

# Calculated session settings
session_bankroll = total_bankroll / total_sessions
max_bet = round(session_bankroll * 0.25, 2)

# Game recommendation function
def recommend_games(df, session_bankroll, max_bet):
    df = df.copy()
    df["Score"] = (
        df["RTP"] * 0.25 +
        df["Bonus_Frequency"] * 0.25 +
        (1 - df["Volatility"]) * 0.2 +
        df["Advantage_Play_Potential"] * 0.2 +
        df["Expected_Return"] * 0.1
    )
    df = df[df["Min_Bet"] <= max_bet]
    df["Stop_Loss"] = df["Min_Bet"].apply(lambda x: round(max(x, session_bankroll * 0.6), 2))
    return df.sort_values(by="Score", ascending=False).head(10)

# Run recommendation
recommended = recommend_games(games_df, session_bankroll, max_bet)

# Display bankroll and session summary
st.markdown("### 💰 Bankroll Status")
st.markdown(f"**Total Bankroll:** ${total_bankroll:.2f} | **Sessions:** {total_sessions}")

st.markdown("### 🎯 Game Plan Summary")
st.markdown(f"**Bankroll/Session:** ${session_bankroll:.2f} | **Max Bet/Session:** ${max_bet:.2f}")

# Display recommended games
st.markdown("## 🧠 Recommended Games to Play")
for _, row in recommended.iterrows():
    st.markdown(
        f"**{row['Name']}**

"
        f"🎰 *{row['Type']}* | 💵 Min Bet: ${row['Min_Bet']} | 🔒 Stop-Loss: ${row['Stop_Loss']}

"
        f"📈 RTP: {row['RTP']} | 🎁 Bonus Frequency: {row['Bonus_Frequency']} | ⚡ Volatility: {row['Volatility']}

"
        f"🧮 Expected Return: {row['Expected_Return']} | 🧠 AP Potential: {int(row['Advantage_Play_Potential'])}

"
        f"📝 {row['Tips']}"
    )