
import streamlit as st
import datetime
import pandas as pd

st.set_page_config(layout="wide")
st.markdown("### 🎰 Profit Hopper v1.5.0 — Smart Bankroll Optimizer")

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

# User Inputs
bankroll = st.number_input("Enter Total Bankroll ($)", min_value=10, value=100)
sessions = st.slider("Number of Sessions", 1, 10, 5)

session_unit = round(bankroll / sessions, 2)
max_bet = round(session_unit * 0.25, 2)

st.markdown("**Session Bankroll:** ${0:.2f} ∣ **Max Bet/Game:** ${1:.2f}".format(session_unit, max_bet))

# Game Analysis
def recommend_games(bankroll, session_unit, max_bet):
    recommendations = []
    for game in full_game_db:
        if game['Min_Bet'] <= max_bet:
            score = 0
            if game['Volatility'] == "Low": score += 2
            elif game['Volatility'] == "Medium": score += 1
            if game['Bonus_Feature'] == "Yes": score += 1
            if game['RTP'] > 0.95: score += 2
            stop_loss = round(min(session_unit * 0.75, session_unit - 1), 2)
            recommendations.append({
                "Name": game['Name'],
                "Min_Bet": game['Min_Bet'],
                "Stop_Loss": stop_loss,
                "Strategy_Tip": game['Strategy_Tip'],
                "Score": score
            })

    sorted_games = sorted(recommendations, key=lambda x: x["Score"], reverse=True)
    return sorted_games[:sessions + 2]

# Display Recommendations
st.subheader("🎯 Recommended Games to Play")
recommended = recommend_games(bankroll, session_unit, max_bet)

for i, game in enumerate(recommended, 1):
    st.markdown(f"**{i}. {game['Name']}**")
    st.markdown(f"🎰 Min Bet: ${game['Min_Bet']} ∣ 🛑 Stop-Loss: ${game['Stop_Loss']}")
    st.markdown(f"📝 {game['Strategy_Tip'] or 'No special strategy'}")
    st.markdown("---")
