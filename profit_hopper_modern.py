
import streamlit as st
import datetime
import pandas as pd

st.set_page_config(layout="wide")
st.markdown("### 🎰 Profit Hopper v1.5.4 — Smart Bankroll Optimizer")

# Game dataset with varied examples
full_game_db = [
    {"Name": "Jacks or Better", "Min_Bet": 0.25, "Volatility": "Low", "Bonus_Feature": "No", "RTP": 0.99, "Strategy_Tip": "Play full-pay versions only."},
    {"Name": "Cleopatra", "Min_Bet": 0.20, "Volatility": "Medium", "Bonus_Feature": "Yes", "RTP": 0.93, "Strategy_Tip": "Watch for bonus symbol frequency."},
    {"Name": "Miss Kitty", "Min_Bet": 0.50, "Volatility": "Medium", "Bonus_Feature": "Yes", "RTP": 0.94, "Strategy_Tip": "Look for stacked wilds early."},
    {"Name": "Caveman Keno", "Min_Bet": 0.25, "Volatility": "Medium", "Bonus_Feature": "Yes", "RTP": 0.92, "Strategy_Tip": "Use patterns and bonus eggs."},
    {"Name": "Buffalo Gold", "Min_Bet": 0.40, "Volatility": "High", "Bonus_Feature": "Yes", "RTP": 0.90, "Strategy_Tip": "High volatility, big bonus potential."}
]

# Sidebar Inputs
st.sidebar.header("Session Settings")
bankroll = st.sidebar.number_input("Total Bankroll ($)", min_value=10, value=100)
sessions = st.sidebar.slider("Number of Sessions", 1, 10, 5)

session_unit = round(bankroll / sessions, 2)
max_bet = round(session_unit * 0.15, 2)

# Game Recommendation Logic
def get_stop_loss(min_bet, volatility, session_unit):
    spins = 8 if volatility == "Low" else 10 if volatility == "Medium" else 12
    base_stop = min_bet * spins
    max_allowed = session_unit * 0.75
    return round(min(base_stop, max_allowed), 2)

def recommend_games(session_unit, max_bet, sessions):
    recs = []
    for game in full_game_db:
        if game['Min_Bet'] > max_bet:
            continue
        stop_loss = get_stop_loss(game['Min_Bet'], game['Volatility'], session_unit)
        score = 0
        if game['Volatility'] == "Low": score += 2
        elif game['Volatility'] == "Medium": score += 1
        if game['Bonus_Feature'] == "Yes": score += 1
        if game['RTP'] >= 0.96: score += 2
        recs.append({
            "Name": game["Name"],
            "Min_Bet": game["Min_Bet"],
            "Stop_Loss": stop_loss,
            "Strategy_Tip": game["Strategy_Tip"],
            "Score": score
        })
    return sorted(recs, key=lambda x: x["Score"], reverse=True)[:sessions + 2]

# Tabs
tab1, tab2, tab3 = st.tabs(["🎯 Game Plan", "📝 Tracker", "📊 Summary"])

# Game Plan Tab
with tab1:
    st.markdown("### 📊 Game Plan Summary")
    st.markdown(f"**Bankroll:** ${bankroll:.2f} | **Sessions:** {sessions} | **Session Bankroll:** ${session_unit:.2f} | **Max Bet/Game:** ${max_bet:.2f}")
    if "log" in st.session_state and st.session_state.log:
        total_in = sum(x['Amount'] for x in st.session_state.log if x['Result'] == "Loss")
        total_out = sum(x['Amount'] for x in st.session_state.log if x['Result'] == "Win")
        net = round(total_out - total_in, 2)
    else:
        total_in = total_out = net = 0.00
    st.markdown(f"**💸 In:** ${total_in:.2f}  **💰 Out:** ${total_out:.2f}  **📈 Net:** ${net:.2f}")
    st.divider()

    st.subheader("📋 Recommended Games to Play")
    recs = recommend_games(session_unit, max_bet, sessions)
    for i, g in enumerate(recs, 1):
        st.markdown(f"**{i}. {g['Name']}**")
        st.markdown(f"🎰 Min Bet: ${g['Min_Bet']:.2f} | 🛑 Stop-Loss: ${g['Stop_Loss']:.2f}")
        st.markdown(f"📝 {g['Strategy_Tip']}")
        st.markdown("---")

# Tracker Tab
with tab2:
    st.subheader("🎯 Session Log")
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
    st.subheader("📊 Bankroll Summary")
    if st.session_state.log:
        total_in = sum(x['Amount'] for x in st.session_state.log if x['Result'] == "Loss")
        total_out = sum(x['Amount'] for x in st.session_state.log if x['Result'] == "Win")
        net = round(total_out - total_in, 2)
        st.metric("💸 Total In (Spent)", f"${total_in:.2f}")
        st.metric("💰 Total Out (Winnings)", f"${total_out:.2f}")
        st.metric("📈 Net Profit", f"${net:.2f}")
    else:
        st.info("No session data yet.")
