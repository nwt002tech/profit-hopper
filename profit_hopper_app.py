import streamlit as st
import pandas as pd

# Load game list from GitHub CSV
@st.cache_data
def load_game_data():
    url = "https://raw.githubusercontent.com/nwt002tech/profit-hopper/main/extended_game_list.csv"
    df = pd.read_csv(url)

    # Convert 'Advantage_Play_Potential' from text to numeric for scoring
    ap_map = {"Low": 1, "Medium": 2, "High": 3}
    if df["Advantage_Play_Potential"].dtype == object:
        df["Advantage_Play_Potential"] = df["Advantage_Play_Potential"].map(ap_map)

    # Ensure numeric columns are clean
    for col in ["RTP", "Volatility", "Bonus_Frequency", "Advantage_Play_Potential"]:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    return df

# Score and recommend games
def recommend_games(df, session_bankroll, max_bet):
    stop_loss_value = round(session_bankroll * 0.6, 2)
    df["Stop_Loss"] = pd.Series(stop_loss_value, index=df.index).clip(lower=df["Min_Bet"])
    df["Score"] = (
        df["RTP"] * 0.3 +
        df["Bonus_Frequency"] * 0.3 +
        df["Advantage_Play_Potential"] * 0.2 +
        (1 - df["Volatility"]) * 0.2
    )
    df = df[df["Min_Bet"] <= max_bet]
    return df.sort_values(by="Score", ascending=False).head(10)

# ---- Interface ----
st.title("🎰 Profit Hopper - Smart Casino Strategy")
st.markdown("Optimize your game choices using real data.")

# User inputs
total_bankroll = st.number_input("Enter total bankroll ($):", min_value=20, value=100, step=10)
num_sessions = st.number_input("Enter number of sessions:", min_value=1, value=5, step=1)
session_bankroll = total_bankroll / num_sessions
max_bet = session_bankroll * 0.25

# Show summary
st.markdown("### 💰 Bankroll Summary")
st.markdown(f"**Total Bankroll:** ${total_bankroll:.2f} | **Sessions:** {num_sessions} | **Per Session:** ${session_bankroll:.2f} | **Max Bet:** ${max_bet:.2f}")

# Load and recommend
games_df = load_game_data()
recommended = recommend_games(games_df, session_bankroll, max_bet)

st.markdown("### 🎯 Top Recommended Games")
for _, row in recommended.iterrows():
    st.markdown(f"""**{row['Name']}**
🎰 {row.get('Type', 'Unknown')} | 💵 Min Bet: ${row.get('Min_Bet', 'N/A')} | RTP: {row.get('RTP', 'N/A')}%
🎯 Volatility: {row['Volatility']} | Bonus: {row['Bonus_Frequency']}
🧠 AP: {row['Advantage_Play_Potential']}
📝 {row['Tips']}""")