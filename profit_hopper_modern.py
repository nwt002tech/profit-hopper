
import streamlit as st
import datetime
import pandas as pd

st.set_page_config(layout="wide")
st.markdown("### 🎰 Profit Hopper v1.5.2 — Smart Bankroll Optimizer")

# Internal Game Dataset (simplified example with fallbacks)
full_game_db = [
    {"Name": "Cleopatra", "Min_Bet": 0.20, "Volatility": "Medium", "Bonus_Feature": "Yes", "RTP": 0.93, "Strategy_Tip": "Watch for bonus symbol frequency."},
    {"Name": "Miss Kitty", "Min_Bet": 0.50, "Volatility": "Medium", "Bonus_Feature": "Yes", "RTP": 0.94, "Strategy_Tip": "Look for stacked wilds early."},
    {"Name": "Jacks or Better", "Min_Bet": 0.25, "Volatility": "Low", "Bonus_Feature": "No", "RTP": 0.99, "Strategy_Tip": "Play full-pay versions only."},
    {"Name": "Caveman Keno", "Min_Bet": 0.25, "Volatility": "Medium", "Bonus_Feature": "Yes", "RTP": 0.92, "Strategy_Tip": "Use patterns and bonus eggs."},
    {"Name": "Buffalo Gold", "Min_Bet": 0.40, "Volatility": "High", "Bonus_Feature": "Yes", "RTP": 0.90, "Strategy_Tip": "High volatility, big bonus potential."},
]

# Sidebar Inputs with validation
st.sidebar.header("Session Settings")
bankroll = st.sidebar.number_input("Total Bankroll ($)", min_value=10, value=100)
sessions = st.sidebar.slider("Number of Sessions", 1, 10, 5)

session_unit = round(bankroll / sessions, 2)
max_bet = round(session_unit * 0.25, 2)

# Game Recommendation Logic
def recommend_games(bankroll, session_unit, max_bet, sessions):
    recommendations = []
    for game in full_game_db:
        min_bet = game.get("Min_Bet", 0.01)
        if min_bet <= max_bet:
            score = 0
            if game.get("Volatility") == "Low": score += 2
            elif game.get("Volatility") == "Medium": score += 1
            if game.get("Bonus_Feature") == "Yes": score += 1
            if game.get("RTP", 0) > 0.95: score += 2
            stop_loss = round(max(min(session_unit * 0.5, min_bet * 4), min_bet * 3), 2)
            recommendations.append({
                "Name": game.get("Name", "Unknown"),
                "Min_Bet": min_bet,
                "Stop_Loss": stop_loss,
                "Strategy_Tip": game.get("Strategy_Tip", "No strategy tip provided."),
                "Score": score
            })
    sorted_games = sorted(recommendations, key=lambda x: x["Score"], reverse=True)
    return sorted_games[:sessions + 2]

# Tabs
tab1, tab2, tab3 = st.tabs(["🎯 Game Plan", "📝 Tracker", "📊 Summary"])

# Game Plan Tab
with tab1:
    st.subheader("Recommended Games")
    st.markdown(f"**Session Unit:** ${session_unit:.2f} ∣ **Max Bet:** ${max_bet:.2f}")
    recommendations = recommend_games(bankroll, session_unit, max_bet, sessions)
    for i, game in enumerate(recommendations, 1):
        st.markdown(f"**{i}. {game['Name']}**")
        st.markdown(f"🎰 Min Bet: ${game['Min_Bet']:.2f} ∣ 🛑 Stop-Loss: ${game['Stop_Loss']:.2f}")
        st.markdown(f"📝 {game['Strategy_Tip']}")
        st.markdown("---")

# Tracker Tab
with tab2:
    st.subheader("Session Log")
    if "log" not in st.session_state:
        st.session_state.log = []
    col1, col2, col3 = st.columns(3)
    with col1:
        result = st.selectbox("Result", ["Win", "Loss"])
    with col2:
        amount = st.number_input("Amount ($)", min_value=0.0, value=0.0)
    with col3:
        game = st.text_input("Game Played")
    if st.button("Add Entry"):
        timestamp = datetime.datetime.now().astimezone().strftime("%Y-%m-%d %I:%M %p")
        st.session_state.log.append({
            "Time": timestamp,
            "Game": game,
            "Result": result,
            "Amount": amount
        })
    if st.session_state.log:
        df = pd.DataFrame(st.session_state.log)
        st.dataframe(df)

# Summary Tab
with tab3:
    st.subheader("Bankroll Summary")
    if st.session_state.log:
        total_in = sum(x['Amount'] for x in st.session_state.log if x['Result'] == "Loss")
        total_out = sum(x['Amount'] for x in st.session_state.log if x['Result'] == "Win")
        net = round(total_out - total_in, 2)
        st.metric("💸 Total In (Spent)", f"${total_in:.2f}")
        st.metric("💰 Total Out (Winnings)", f"${total_out:.2f}")
        st.metric("📈 Net Profit", f"${net:.2f}")
    else:
        st.info("No session data yet.")
