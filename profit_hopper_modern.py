
# Profit Hopper App - Enhanced Version
# Version: 3.0.2
# Updated: 2025-07-24 05:58 PM

import streamlit as st
import pandas as pd
import json
from datetime import datetime
import pytz

st.set_page_config(page_title="Profit Hopper", layout="centered")

@st.cache_data
def load_game_data():
    with open("profit_hopper_assets/enhanced_game_data_full.json", "r") as f:
        return pd.DataFrame(json.load(f))

games_df = load_game_data()

st.sidebar.title("Session Setup")
total_bankroll = st.sidebar.number_input("Total Bankroll ($)", min_value=10, value=100, step=10)
num_sessions = st.sidebar.slider("Number of Sessions", 1, 20, 5)
session_bankroll = round(total_bankroll / num_sessions, 2)
max_bet = round(session_bankroll / 4, 2)

def analyze_games(df, session_bankroll, max_bet):
    filtered = df.copy()
    filtered["Min_Bet_OK"] = filtered["Denomination_Options"].apply(lambda opts: any(b <= max_bet for b in opts))
    filtered = filtered[filtered["Min_Bet_OK"]]
    filtered["Stop_Loss"] = filtered["Denomination_Options"].apply(lambda opts: min([b for b in opts if b <= max_bet], default=max_bet) * 4)
    filtered = filtered[filtered["Stop_Loss"] < session_bankroll]
    volatility_map = {"Low": 3, "Medium": 2, "High": 1, "Very High": 0}
    filtered["Vol_Score"] = filtered["Volatility"].map(volatility_map).fillna(1)
    filtered["Score"] = (
        filtered["RTP"] * 100
        + filtered["Bonus_Frequency"] * 100
        + filtered["Vol_Score"] * 5
    )
    sorted_games = filtered.sort_values(by="Score", ascending=False).head(num_sessions + 2)
    return sorted_games

recommended_games = analyze_games(games_df, session_bankroll, max_bet)

tab1, tab2, tab3 = st.tabs(["Game Plan", "Tracker", "Summary"])

with tab1:
    st.markdown("### Game Plan Summary")
    col1, col2 = st.columns(2)
    col1.metric("Total Bankroll", f"${total_bankroll}")
    col2.metric("Sessions", f"{num_sessions}")
    col1.metric("Session Bankroll", f"${session_bankroll}")
    col2.metric("Max Bet", f"${max_bet}")

    st.markdown("---")
    st.markdown("### Recommended Games")

    
for idx, row in recommended_games.iterrows():
    game_output = f"""**{row['Name']}**
🎰 Min Bet: ${row['Min_Bet']} | 🛑 Stop-Loss: ${row['Stop_Loss']:.2f}
📝 {row['Strategy_Tip']}"""
    st.markdown(game_output)
        st.markdown(
            "**{}**  
🎰 Min Bet: ${} | 🛑 Stop-Loss: ${:.2f}  
📝 {}".format(
                row['Name'], row['Min_Bet'], row['Stop_Loss'], row['Strategy_Tip']
            )
        )

with tab2:
    st.markdown("### Session Tracker")
    with st.form("session_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        game = col1.text_input("Game Played")
        amount_in = col1.number_input("Amount In ($)", min_value=0.0, value=0.0, step=0.25)
        amount_out = col2.number_input("Amount Out ($)", min_value=0.0, value=0.0, step=0.25)
        bonus = col2.checkbox("Bonus Hit?")
        followed_strategy = col2.checkbox("Followed Strategy?")
        submitted = st.form_submit_button("Add Entry")

        if submitted and game:
            tz = datetime.now().astimezone().tzinfo
            entry_time = datetime.now(tz).strftime('%Y-%m-%d %I:%M %p')
            new_entry = {
                "Time": entry_time,
                "Game": game,
                "In": amount_in,
                "Out": amount_out,
                "Bonus": bonus,
                "Followed": followed_strategy
            }
            if "session_log" not in st.session_state:
                st.session_state["session_log"] = []
            st.session_state["session_log"].append(new_entry)

    if "session_log" in st.session_state and st.session_state["session_log"]:
        st.markdown("#### Logged Sessions")
        st.dataframe(pd.DataFrame(st.session_state["session_log"]))

with tab3:
    st.markdown("### Bankroll Summary")
    if "session_log" in st.session_state:
        df = pd.DataFrame(st.session_state["session_log"])
        total_in = df["In"].sum()
        total_out = df["Out"].sum()
        net = total_out - total_in
        col1, col2, col3 = st.columns(3)
        col1.metric("Total In", f"${total_in:.2f}")
        col2.metric("Total Out", f"${total_out:.2f}")
        col3.metric("Net", f"${net:.2f}")
    else:
        st.info("No sessions logged yet.")
