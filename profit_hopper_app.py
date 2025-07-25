
import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Profit Hopper", layout="wide")

APP_VERSION = "v1.0.0"

games_data = [
    {"Name": "Cleopatra", "Min_Bet": 0.20, "Volatility": 3, "Bonus_Hit_Freq": 0.18, "Category": "Slots"},
    {"Name": "Miss Kitty", "Min_Bet": 0.50, "Volatility": 2, "Bonus_Hit_Freq": 0.22, "Category": "Slots"},
    {"Name": "Jacks or Better", "Min_Bet": 0.25, "Volatility": 1, "Bonus_Hit_Freq": 0.12, "Category": "Video Poker"},
    {"Name": "Caveman Keno", "Min_Bet": 0.25, "Volatility": 2, "Bonus_Hit_Freq": 0.19, "Category": "Video Keno"},
    {"Name": "Buffalo Gold", "Min_Bet": 0.40, "Volatility": 5, "Bonus_Hit_Freq": 0.10, "Category": "Slots"},
]
games_df = pd.DataFrame(games_data)

if "session_log" not in st.session_state:
    st.session_state["session_log"] = []

st.sidebar.markdown("## Setup")
total_bankroll = st.sidebar.number_input("Total Starting Bankroll", value=100.0, step=10.0)
total_sessions = st.sidebar.number_input("Number of Sessions", value=5, min_value=1)
session_bankroll = round(total_bankroll / total_sessions, 2)
max_bet = round(session_bankroll * 0.25, 2)

st.markdown(f"### Profit Hopper {APP_VERSION}")
st.markdown(f"**Bankroll Status:** In: ${sum([x['amount_in'] for x in st.session_state['session_log']]):.2f} | Out: ${sum([x['amount_out'] for x in st.session_state['session_log']]):.2f} | Net: ${sum([x['amount_out'] - x['amount_in'] for x in st.session_state['session_log']]):.2f}")
st.markdown(f"**Game Plan:** Total Bankroll: ${total_bankroll:.2f} | Sessions: {total_sessions} | Bankroll/Session: ${session_bankroll:.2f} | Max Bet: ${max_bet:.2f}")

tab1, tab2, tab3 = st.tabs(["Game Plan", "Tracker", "Summary"])

with tab1:
    st.subheader("Recommended Games")
    filtered = games_df[games_df["Min_Bet"] <= max_bet]
    if not filtered.empty:
        filtered["Score"] = (
            (1 / filtered["Volatility"]) * 0.6 +
            filtered["Bonus_Hit_Freq"] * 0.4
        )
        filtered["Stop_Loss"] = (session_bankroll * 0.5).clip(lower=filtered["Min_Bet"]).round(2)
        recommended_games = filtered.sort_values(by="Score", ascending=False).head(total_sessions + 2)

        for idx, row in recommended_games.iterrows():
            game_output = f"**{row['Name']}**
"
            game_output += f"Min Bet: ${row['Min_Bet']} | Stop-Loss: ${row['Stop_Loss']}
"
            game_output += f"Category: {row['Category']}
"
            game_output += "---"
            st.markdown(game_output)
    else:
        st.warning("No games found matching your max bet criteria.")

with tab2:
    st.subheader("Session Tracker")
    with st.form("tracker_form"):
        col1, col2 = st.columns(2)
        with col1:
            game = st.text_input("Game Name")
        with col2:
            amount_in = st.number_input("Amount In", value=20.0)
            amount_out = st.number_input("Amount Out", value=0.0)
        submitted = st.form_submit_button("Add Entry")
        if submitted and game:
            new_entry = {
                "datetime": datetime.now().strftime("%Y-%m-%d %I:%M %p"),
                "game": game,
                "amount_in": amount_in,
                "amount_out": amount_out
            }
            st.session_state["session_log"].append(new_entry)
            st.success(f"Logged session for {game}")

    if st.session_state["session_log"]:
        st.dataframe(pd.DataFrame(st.session_state["session_log"]))

with tab3:
    st.subheader("Session Summary")
    if st.session_state["session_log"]:
        df = pd.DataFrame(st.session_state["session_log"])
        total_in = df["amount_in"].sum()
        total_out = df["amount_out"].sum()
        net = total_out - total_in
        st.markdown(f"**Total In:** ${total_in:.2f}  
**Total Out:** ${total_out:.2f}  
**Net Profit:** ${net:.2f}")
    else:
        st.info("No sessions logged yet.")
