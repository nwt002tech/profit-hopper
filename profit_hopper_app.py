# Profit Hopper App - v20250726-030838
# Locked clean version with verified scoring, layout, and error handling

import streamlit as st
import pandas as pd

st.set_page_config(page_title="Profit Hopper", layout="wide")

# Load game list
@st.cache_data
def load_data():
    return pd.read_csv("extended_game_list.csv")

games_df = load_data()

# Session Settings
st.sidebar.header("Session Settings")
total_bankroll = st.sidebar.number_input("Total Bankroll ($)", min_value=10, value=100)
session_count = st.sidebar.slider("Number of Sessions", min_value=1, max_value=50, value=5)
session_bankroll = round(total_bankroll / session_count, 2)
max_bet = round(session_bankroll * 0.25, 2)

# Define scoring logic
def recommend_games(df, session_bankroll, max_bet):
    df = df.copy()

    # Replace missing values and ensure numeric types
    for col in ["RTP", "Volatility", "Bonus_Frequency", "Advantage_Play_Potential"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    # Scoring formula
    df["Score"] = (
        df["RTP"] * 0.4 +
        (1 - df["Volatility"]) * 0.25 +
        df["Bonus_Frequency"] * 0.15 +
        df["Advantage_Play_Potential"] * 0.2
    )

    # Filter by bet range
    df["Stop_Loss"] = df["Min_Bet"].clip(upper=session_bankroll * 0.6).round(2)
    valid = df[df["Min_Bet"] <= max_bet]

    return valid.sort_values("Score", ascending=False).reset_index(drop=True)

# Recommendation Logic
recommended = recommend_games(games_df, session_bankroll, max_bet)

# Layout
st.title("Profit Hopper")
st.subheader("Total Bankroll: ${:.2f} | Sessions: {} | Bankroll/Session: ${:.2f} | Max Bet: ${:.2f}".format(
    total_bankroll, session_count, session_bankroll, max_bet))

st.markdown("## Recommended Games")
for _, row in recommended.iterrows():
    st.markdown(f"""
**{row['Name']}**
- Type: {row.get('Best_Casino_Type', 'N/A')}
- Volatility: {row['Volatility']}
- RTP: {row['RTP']}%
- Bonus Frequency: {row['Bonus_Frequency']}
- Advantage Play Potential: {row['Advantage_Play_Potential']}
- Tip: {row['Tips']}
- Suggested Stop-Loss: ${row['Stop_Loss']}
---""")

