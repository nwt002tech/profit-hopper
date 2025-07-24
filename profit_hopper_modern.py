
import streamlit as st
import pandas as pd

# Sample game list (replace with actual game logic)
games = ["Game A", "Game B", "Game C"]

# Set initial session state if not already set
if "session_log" not in st.session_state:
    st.session_state["session_log"] = []

st.title("🎰 Profit Hopper - Casino Strategy Assistant")

with st.form("session_form"):
    game = st.selectbox("🎮 Select a game", games)
    bankroll = st.number_input("💰 Bankroll ($)", min_value=1, step=1)
    max_bet = st.number_input("🎯 Max Bet ($)", min_value=1, step=1)
    stop_loss = st.number_input("🛑 Stop-Loss ($)", min_value=1, step=1)
    session_notes = st.text_area("📝 Notes (optional)", height=100)
    submitted = st.form_submit_button("➕ Add Session")

    if submitted and game:
        new_entry = {
            "Game": game,
            "Bankroll": bankroll,
            "Max Bet": max_bet,
            "Stop-Loss": stop_loss,
            "Notes": session_notes
        }
        st.session_state["session_log"].append(new_entry)
        st.success("Session added!")

if st.session_state["session_log"]:
    st.subheader("📊 Session Log")
    df = pd.DataFrame(st.session_state["session_log"])
    st.dataframe(df, use_container_width=True)

    with st.expander("🗑️ Clear Log"):
        if st.button("Clear All Sessions"):
            st.session_state["session_log"] = []
            st.success("All sessions cleared.")
