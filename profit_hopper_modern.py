
# Profit Hopper App - Enhanced Version
# Version: 3.0.2
# Updated: 2025-07-24 05:58 PM

import streamlit as st
import pandas as pd
import json
from datetime import datetime
import pytz


@st.cache_data
def get_recommended_games(game_df, session_bankroll, max_bet):



    filtered = filtered[filtered["Min_Bet_OK"]]
    filtered = filtered[filtered["Stop_Loss"] < session_bankroll]
    volatility_map = {"Low": 3, "Medium": 2, "High": 1, "Very High": 0}
    filtered["Score"] = (
        filtered["RTP"] * 100
        + filtered["Bonus_Frequency"] * 100
        + filtered["Vol_Score"] * 5
    )
    return sorted_games



    with tab1:
        for idx, row in recommended_games.iterrows():
            game_output = f"""**{row['Name']}**
🎰 Min Bet: ${row['Min_Bet']} | 🛑 Stop-Loss: ${row['Stop_Loss']:.2f}
📝 {row['Strategy_Tip']}"""
            st.markdown(game_output)

    with tab2:
        if submitted and game:
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
            if "session_log" in st.session_state and st.session_state["session_log"]:
            with tab3:
            if "session_log" in st.session_state:
            net = total_out - total_in
            else:
            with tab1:
        for idx, row in recommended_games.iterrows():
            game_output = f"""**{row['Name']}**
🎰 Min Bet: ${row['Min_Bet']} | 🛑 Stop-Loss: ${row['Stop_Loss']:.2f}
📝 {row['Strategy_Tip']}"""
            st.markdown(game_output)

with tab2:
        if submitted and game:
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
            if "session_log" in st.session_state and st.session_state["session_log"]:
with tab3:
    if "session_log" in st.session_state:
        net = total_out - total_in
    else: