import streamlit as st
import pandas as pd
from datetime import datetime
import pytz

APP_VERSION = "v3.4.2"

@st.cache_data
def load_games():
    try:
        df = pd.read_csv("game_list.csv")
        return df
    except:
        return pd.DataFrame(columns=["Name", "Type", "Volatility", "Bonus", "Min_Bet", "RTP"])

def recommend_games(games_df, session_bankroll, max_bet):
    df = games_df.copy()
    df = df[df["Min_Bet"] <= max_bet]
    df["Score"] = (
        (df["RTP"] / 100) +
        df["Bonus"].map(lambda b: 0.2 if b else 0) +
        df["Volatility"].map(lambda v: 0.3 if v == "Low" else (0.2 if v == "Medium" else 0.1))
    )
    df["Stop_Loss"] = session_bankroll * 0.6
    df["Stop_Loss"] = pd.to_numeric(df[["Stop_Loss", "Min_Bet"]].max(axis=1), errors="coerce").round(2)
    return df.sort_values("Score", ascending=False).reset_index(drop=True)

if "session_log" not in st.session_state:
    st.session_state["session_log"] = []

st.sidebar.title("🎯 Profit Hopper")
st.sidebar.markdown("**App Version:** v3.4.2")
total_bankroll = st.sidebar.number_input("Total Bankroll", value=100.0, step=10.0)
sessions = st.sidebar.number_input("Number of Sessions", value=5, step=1)
session_bankroll = round(total_bankroll / sessions, 2)
max_bet = round(session_bankroll * 0.25, 2)

tab1, tab2, tab3 = st.tabs(["📋 Game Plan", "🧾 Tracker", "📊 Summary"])

with tab1:
    st.markdown("### 🎯 Game Plan Summary")
    st.markdown(f"**Total Bankroll:** ${total_bankroll:.2f} | **Sessions:** {sessions} | **Session Bankroll:** ${session_bankroll:.2f} | **Max Bet:** ${max_bet:.2f}")

    games_df = load_games()
    recommended = recommend_games(games_df, session_bankroll, max_bet)

    st.markdown("---")
    st.markdown("### 🎮 Recommended Games to Play (Best Order):")
    for i, row in recommended.iterrows():
        st.markdown(
            f"""**{i+1}. {row['Name']}**
🎰 Min Bet: ${row['Min_Bet']} | 🛑 Stop-Loss: ${row['Stop_Loss']}
📝 Type: {row['Type']} | Volatility: {row['Volatility']} | Bonus: {"Yes" if row['Bonus'] else "No"}"""
        )

with tab2:
    st.markdown("### ➕ Add Session Entry")
    with st.form("session_form", clear_on_submit=True):
        game = st.selectbox("Game Played", recommended["Name"].tolist())
        amount_in = st.number_input("Money In ($)", min_value=0.0, step=1.0)
        amount_out = st.number_input("Money Out ($)", min_value=0.0, step=1.0)
        bonus_hit = st.checkbox("Bonus Hit?")
        followed_strategy = st.checkbox("Followed Strategy?")
        submitted = st.form_submit_button("Add Entry")
        if submitted and game:
            local_time = datetime.now().astimezone().strftime("%Y-%m-%d %I:%M %p")
            new_entry = {
                "Time": local_time,
                "Game": game,
                "In": amount_in,
                "Out": amount_out,
                "Bonus": bonus_hit,
                "Strategy": followed_strategy
            }
            st.session_state["session_log"].append(new_entry)
            st.success("Entry added.")

with tab3:
    st.markdown("### 🧾 Session Log")
    if st.session_state["session_log"]:
        df = pd.DataFrame(st.session_state["session_log"])
        st.dataframe(df, use_container_width=True)

        total_in = df["In"].sum()
        total_out = df["Out"].sum()
        net = total_out - total_in

        st.markdown(f"**Money In:** ${total_in:.2f} | **Money Out:** ${total_out:.2f} | **Net:** ${net:.2f}")
    else:
        st.info("No session data logged yet.")
