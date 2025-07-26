
import streamlit as st
import pandas as pd

# Load game list directly from GitHub
GITHUB_CSV_URL = "https://raw.githubusercontent.com/nwt002tech/profit-hopper/main/extended_game_list.csv"

def recommend_games(df, session_bankroll, max_bet):
    fields_to_numeric = ["Volatility", "Bonus_Frequency", "Advantage_Play_Potential", "RTP", "Min_Bet"]
    for field in fields_to_numeric:
        if field in df.columns:
            df[field] = pd.to_numeric(df[field], errors="coerce")
        else:
            df[field] = 0.0

    # Drop rows with missing or zero values in key fields
    df.dropna(subset=fields_to_numeric, inplace=True)

    # Score calculation
    df["Score"] = (
        df["RTP"] * 0.3 +
        (1 - df["Volatility"]) * 0.2 +
        df["Bonus_Frequency"] * 0.2 +
        df["Advantage_Play_Potential"] * 0.3
    )

    # Calculate dynamic stop-loss based on session bankroll
    df["Stop_Loss"] = (session_bankroll * 0.6).clip(lower=df["Min_Bet"]).round(2)

    # Filter games based on max bet
    filtered = df[df["Min_Bet"] <= max_bet]

    # Sort and recommend
    return filtered.sort_values(by="Score", ascending=False)

# Streamlit App
st.set_page_config(page_title="Profit Hopper", layout="wide")

st.title("💰 Profit Hopper: Casino Strategy Assistant")

total_bankroll = st.number_input("🎯 Total Bankroll", min_value=10.0, step=10.0, value=100.0)
num_sessions = st.number_input("🧮 Number of Sessions", min_value=1, step=1, value=5)
max_bet = st.number_input("🎲 Max Bet Per Game", min_value=0.25, step=0.25, value=5.0)

session_bankroll = round(total_bankroll / num_sessions, 2)

st.markdown(f"**💼 Session Bankroll:** ${session_bankroll}")

try:
    games_df = pd.read_csv(GITHUB_CSV_URL)
    recommended = recommend_games(games_df, session_bankroll, max_bet)

    st.subheader("✅ Recommended Games")

    for _, row in recommended.iterrows():
        st.markdown(f'''
            ### 🎰 {row['Name']}
            - **Type:** {row.get("Type", "N/A")}
            - **Volatility:** {row.get("Volatility", "N/A")}
            - **Bonus Frequency:** {row.get("Bonus_Frequency", "N/A")}
            - **RTP:** {row.get("RTP", "N/A")}%
            - **Min Bet:** ${row.get("Min_Bet", "N/A")}
            - **Stop-Loss:** ${row.get("Stop_Loss", "N/A")}
            - **Advantage Play Potential:** {row.get("Advantage_Play_Potential", "N/A")}
            - **Best Casino Type:** {row.get("Best_Casino_Type", "N/A")}
            - **Tips:** {row.get("Tips", "N/A")}
        ''')

except Exception as e:
    st.error(f"Failed to load recommendations: {e}")
