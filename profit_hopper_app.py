
import streamlit as st
import pandas as pd

# Load game data
@st.cache_data
def load_data():
    return pd.read_csv("https://raw.githubusercontent.com/nwt002tech/profit-hopper/main/extended_game_list.csv")

games_df = load_data()

# User-defined bankroll and session settings
total_bankroll = st.sidebar.number_input("Total Bankroll ($)", min_value=10, max_value=10000, value=100)
total_sessions = st.sidebar.number_input("Total Sessions", min_value=1, max_value=100, value=5)
session_bankroll = total_bankroll / total_sessions
max_bet = round(session_bankroll * 0.25, 2)

# Game recommendation logic
def recommend_games(df, session_bankroll, max_bet):
    df = df.copy()
    df = df.dropna(subset=["Volatility", "Bonus_Frequency", "Advantage_Play_Potential", "Min_Bet"])
    df["Volatility"] = pd.to_numeric(df["Volatility"], errors="coerce")
    df["Bonus_Frequency"] = pd.to_numeric(df["Bonus_Frequency"], errors="coerce")
    df["Advantage_Play_Potential"] = pd.to_numeric(df["Advantage_Play_Potential"], errors="coerce")
    df["Min_Bet"] = pd.to_numeric(df["Min_Bet"], errors="coerce")

    df = df.dropna()

    # Score games using weighted metrics
    df["Score"] = (
        df["Bonus_Frequency"] * 0.4 +
        df["Advantage_Play_Potential"] * 0.2 +
        (5 - df["Volatility"]) * 0.4
    )

    # Calculate stop-loss
    df["Stop_Loss"] = (session_bankroll * 0.6).clip(lower=df["Min_Bet"]).round(2)

    # Filter out games with min bet higher than max bet
    filtered_df = df[df["Min_Bet"] <= max_bet]

    return filtered_df.sort_values(by="Score", ascending=False).reset_index(drop=True)

# Layout
st.title("Profit Hopper – Game Plan Assistant")

st.markdown("### Bankroll Summary")
st.markdown(f"**Total Bankroll:** ${total_bankroll:.2f} | **Sessions:** {total_sessions}")
st.markdown(f"**Bankroll/Session:** ${session_bankroll:.2f} | **Max Bet/Session:** ${max_bet:.2f}")

st.markdown("### Recommended Games")
recommended = recommend_games(games_df, session_bankroll, max_bet)

if recommended.empty:
    st.warning("No suitable games found for your current bankroll and session settings.")
else:
    for _, row in recommended.iterrows():
        st.markdown(f'''**{row["Name"]}**
Type: {row["Best_Casino_Type"]}
Bonus Frequency: {row["Bonus_Frequency"]}
Volatility: {row["Volatility"]}
AP Potential: {row["Advantage_Play_Potential"]}
Tip: {row["Tips"]}
Stop-Loss: ${row["Stop_Loss"]:.2f}
''')
