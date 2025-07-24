
import streamlit as st
import datetime
import pandas as pd

st.set_page_config(layout="wide")
st.markdown("### 🎰 Profit Hopper v1.5.1 — Smart Bankroll Optimizer")

# Internal Game Dataset
full_game_db = [
  {
    "Name": "Cleopatra Keno",
    "Volatility": "Medium",
    "Min_Bet": 0.2,
    "RTP": 0.94,
    "Bonus_Feature": "Yes",
    "Strategy_Tip": "Bonus hits vary by variant."
  },
  {
    "Name": "Caveman Keno",
    "Volatility": "Medium",
    "Min_Bet": 0.25,
    "RTP": 0.93,
    "Bonus_Feature": "Yes",
    "Strategy_Tip": "Bonus hits vary by variant."
  },
  {
    "Name": "Multi-Card Keno",
    "Volatility": "Low",
    "Min_Bet": 0.25,
    "RTP": 0.92,
    "Bonus_Feature": "No",
    "Strategy_Tip": ""
  },
  {
    "Name": "4-Card Keno",
    "Volatility": "Low",
    "Min_Bet": 0.25,
    "RTP": 0.91,
    "Bonus_Feature": "No",
    "Strategy_Tip": ""
  },
  {
    "Name": "Classic Video Keno",
    "Volatility": "Low",
    "Min_Bet": 0.25,
    "RTP": 0.9,
    "Bonus_Feature": "No",
    "Strategy_Tip": ""
  },
  {
    "Name": "Jacks or Better",
    "Volatility": "Low",
    "Min_Bet": 0.25,
    "RTP": 0.99,
    "Bonus_Feature": "No",
    "Strategy_Tip": "Play full-pay machines."
  },
  {
    "Name": "Bonus Poker",
    "Volatility": "Medium",
    "Min_Bet": 0.25,
    "RTP": 0.98,
    "Bonus_Feature": "No",
    "Strategy_Tip": "Better return on high pairs and quads."
  },
  {
    "Name": "Double Double Bonus",
    "Volatility": "High",
    "Min_Bet": 0.25,
    "RTP": 0.97,
    "Bonus_Feature": "No",
    "Strategy_Tip": "Big wins rely on 4 Aces with kicker."
  },
  {
    "Name": "Quick Hit Platinum",
    "Volatility": "Medium",
    "Min_Bet": 0.3,
    "RTP": 0.94,
    "Bonus_Feature": "Yes",
    "Strategy_Tip": "Check meter progression and number of visible symbols."
  },
  {
    "Name": "Dragon Link",
    "Volatility": "High",
    "Min_Bet": 0.5,
    "RTP": 0.96,
    "Bonus_Feature": "Yes",
    "Strategy_Tip": "Preferable when fireball hold & spin occurs frequently."
  }
]

# Sidebar Inputs
st.sidebar.header("Session Settings")
bankroll = st.sidebar.number_input("Total Bankroll ($)", min_value=10, value=100)
sessions = st.sidebar.slider("Number of Sessions", 1, 10, 5)

session_unit = round(bankroll / sessions, 2)
max_bet = round(session_unit * 0.25, 2)

# Recommendation logic
def recommend_games(bankroll, session_unit, max_bet):
    recommendations = []
    for game in full_game_db:
        if game['Min_Bet'] <= max_bet:
            score = 0
            if game['Volatility'] == "Low": score += 2
            elif game['Volatility'] == "Medium": score += 1
            if game['Bonus_Feature'] == "Yes": score += 1
            if game['RTP'] > 0.95: score += 2
            # Improved stop-loss logic
            calculated_stop = min(session_unit * 0.5, game['Min_Bet'] * 4)
            stop_loss = round(max(calculated_stop, game['Min_Bet'] * 3), 2)
            recommendations.append({
                "Name": game['Name'],
                "Min_Bet": game['Min_Bet'],
                "Stop_Loss": stop_loss,
                "Strategy_Tip": game['Strategy_Tip'],
                "Score": score
            })
    sorted_games = sorted(recommendations, key=lambda x: x["Score"], reverse=True)
    return sorted_games[:sessions + 2]

# Tabs
tab1, tab2, tab3 = st.tabs(["🎯 Game Plan", "📝 Tracker", "📊 Summary"])

# Game Plan Tab
with tab1:
    st.subheader("Recommended Games")
    st.markdown("**Session Unit:** $0.00 ∣ **Max Bet:** $1.00".format(session_unit, max_bet))
    recommendations = recommend_games(bankroll, session_unit, max_bet)
    for i, game in enumerate(recommendations, 1):
        st.markdown("**0. 1**".format(i, game['Name']))
        st.markdown("🎰 Min Bet: $0.00 ∣ 🛑 Stop-Loss: $1.00".format(game['Min_Bet'], game['Stop_Loss']))
        st.markdown("📝 0".format(game['Strategy_Tip'] or 'No special strategy'))
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
        st.metric("💸 Total In (Spent)", "$0.00".format(total_in))
        st.metric("💰 Total Out (Winnings)", "$0.00".format(total_out))
        st.metric("📈 Net Profit", "$0.00".format(net))
    else:
        st.info("No session data yet.")
