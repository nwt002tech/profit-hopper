
import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Profit Hopper", layout="wide")

# App version
APP_VERSION = "v1.0.3"

# Load game data
@st.cache_data
def load_games():
    return pd.read_csv("game_data.csv")

games_df = load_games()

# Bankroll Inputs
st.title("Profit Hopper " + APP_VERSION)
bankroll = st.sidebar.number_input("Total Bankroll", min_value=10, value=100)
sessions = st.sidebar.number_input("Number of Sessions", min_value=1, value=5)
session_bankroll = round(bankroll / sessions, 2)
max_bet = round(session_bankroll * 0.25, 2)

# Calculating Stop-Loss
def recommend_games(df, session_bankroll, max_bet):
    df["Stop_Loss"] = (session_bankroll * 0.6).round(2).clip(lower=df["Min_Bet"])
    df["Score"] = df["Volatility"].apply(lambda v: 1/v if v > 0 else 0)
    filtered = df[df["Min_Bet"] <= max_bet]
    return filtered.sort_values("Score", ascending=False).head(sessions + 2)

recommended = recommend_games(games_df, session_bankroll, max_bet)

# Top Summary
st.markdown(f"""
### Bankroll Status
- Total Bankroll: ${bankroll}
- Session Bankroll: ${session_bankroll}
- Max Bet per Game: ${max_bet}

### Recommended Game Plan
""")

# Game List Display
for idx, row in recommended.iterrows():
    st.markdown(
        f"**{row['Name']}**  
"
        f"Min Bet: ${row['Min_Bet']:.2f} | Stop-Loss: ${row['Stop_Loss']:.2f}  
"
        f"Score: {row['Score']:.2f}  
"
        f"Tip: {row['Tip']}"
    )

# Tabs for logging and tracking
tab1, tab2 = st.tabs(["Tracker", "Summary"])

with tab1:
    with st.form("session_form"):
        col1, col2 = st.columns(2)
        with col1:
            game = st.selectbox("Game Played", games_df["Name"].unique())
        with col2:
            amount_in = st.number_input("Amount In", min_value=0.0, value=0.0)
            amount_out = st.number_input("Amount Out", min_value=0.0, value=0.0)
        submitted = st.form_submit_button("Add Session")
        if "session_log" not in st.session_state:
            st.session_state["session_log"] = []

        if submitted and game:
            st.session_state["session_log"].append({
                "Timestamp": datetime.now().strftime("%Y-%m-%d %I:%M %p"),
                "Game": game,
                "In": amount_in,
                "Out": amount_out,
                "Net": round(amount_out - amount_in, 2)
            })
            st.experimental_rerun()

    st.markdown("### Session Log")
    if st.session_state["session_log"]:
        df_log = pd.DataFrame(st.session_state["session_log"])
        st.dataframe(df_log, use_container_width=True)

with tab2:
    st.markdown("### Session Summary")
    if st.session_state["session_log"]:
        df_log = pd.DataFrame(st.session_state["session_log"])
        total_in = df_log["In"].sum()
        total_out = df_log["Out"].sum()
        net = total_out - total_in
        st.metric("Total In", f"${total_in:.2f}")
        st.metric("Total Out", f"${total_out:.2f}")
        st.metric("Net Profit/Loss", f"${net:.2f}")
    else:
        st.info("No session data logged yet.")
