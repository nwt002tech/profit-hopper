
import streamlit as st
import pandas as pd
from datetime import datetime

# === Game Recommendation (Data-Driven) ===
game_data = [
    {"name": "Jacks or Better Video Poker", "rtp": 99.54, "volatility": "Low", "bonus_freq": "None", "min_bet": 0.25, "notes": "Great for conservative play. Use only 1-credit bets."},
    {"name": "88 Fortunes", "rtp": 96.0, "volatility": "Low", "bonus_freq": "Medium", "min_bet": 0.88, "notes": "Better with pot nearly full. Use when bet under session unit."},
    {"name": "Ultimate Fire Link", "rtp": 96.5, "volatility": "Medium", "bonus_freq": "High", "min_bet": 0.50, "notes": "Only play if ball count > 450 or Mini > $20."},
    {"name": "Lightning Link", "rtp": 96.1, "volatility": "Medium-High", "bonus_freq": "Medium", "min_bet": 0.50, "notes": "Look for high Mini/Major values. Better as bankroll grows."},
    {"name": "Buffalo Gold", "rtp": 96.0, "volatility": "High", "bonus_freq": "Low", "min_bet": 0.60, "notes": "Use in later sessions with profit buffer. High variance."},
    {"name": "Triple Double Bonus Poker", "rtp": 97.0, "volatility": "High", "bonus_freq": "None", "min_bet": 0.25, "notes": "Big payout potential. Use in mid-to-late sessions."},
    {"name": "Cleopatra Keno", "rtp": 94.0, "volatility": "Low", "bonus_freq": "Medium", "min_bet": 0.20, "notes": "Reliable time extender. Great for early game play."},
    {"name": "Dancing Drums", "rtp": 95.0, "volatility": "Medium", "bonus_freq": "Medium", "min_bet": 0.88, "notes": "Look for near full drums or high Mini."}
]

def score_game(game, session_unit, risk_level):
    rtp_score = game["rtp"]
    bet_factor = 1 if game["min_bet"] <= session_unit else 0.5
    vol_score = {"Low": 2, "Medium": 1, "Medium-High": 0.5, "High": 0}[game["volatility"]]
    risk_tolerance = {"Low": 1, "Medium": 1.5, "High": 2}[risk_level]
    vol_score *= risk_tolerance
    return (rtp_score * bet_factor * vol_score)

def get_recommended_games(session_unit, max_bet, risk):
    scored = []
    for game in game_data:
        score = score_game(game, session_unit, risk)
        scored.append((score, game))
    sorted_games = sorted(scored, key=lambda x: x[0], reverse=True)
    return [(g["name"], g["notes"]) for _, g in sorted_games]

st.set_page_config(page_title="Profit Hopper", layout="centered")

if "tracker" not in st.session_state:
    st.session_state.tracker = []

with st.sidebar:
    st.header("🎯 Setup")
    bankroll = st.number_input("💵 Starting Bankroll ($)", min_value=10, value=100, step=10)
    sessions = st.number_input("🎮 Sessions", min_value=1, value=5)
    risk = st.selectbox("📊 Risk Level", ["Low", "Medium", "High"])
    profit_goal_percent = st.slider("🏁 Profit Goal (%)", 5, 100, 20)

session_unit = bankroll / sessions
risk_factor = {"Low": 40, "Medium": 30, "High": 20}
max_bet = session_unit / risk_factor[risk]
profit_goal = bankroll * (1 + profit_goal_percent / 100)

df = pd.DataFrame(st.session_state.tracker)
total_in = df["Amount In"].sum() if not df.empty else 0
total_out = df["Amount Out"].sum() if not df.empty else 0
net = total_out - total_in

st.markdown("### 📊 Quick Summary")
st.markdown(
    "<div style='line-height: 1.5; font-size: 16px;'>"
    f"<b>💼 Bankroll</b>: Start ${bankroll:.0f} | Goal ${profit_goal:.0f}<br>"
    f"<b>🧮 Strategy</b>: ${session_unit:.0f}/session | Max Bet ${max_bet:.2f}<br>"
    f"<b>📈 Status</b>: In ${total_in:.0f} | Out ${total_out:.0f} | Net ${net:.0f}"
    "</div>",
    unsafe_allow_html=True
)

st.markdown("### 🎯 Recommended Game Order")
recommended = get_recommended_games(session_unit, max_bet, risk)
for idx, (game, note) in enumerate(recommended, 1):
    st.markdown("**{}. {}** — {}".format(idx, game, note))

tab1, tab2 = st.tabs(["📋 Tracker", "📊 Log"])
with tab1:
    st.subheader("➕ Add Session")
    with st.form("session_form", clear_on_submit=True):
        game = st.text_input("Game / Machine Name")
        amount_in = st.number_input("Amount Inserted ($)", min_value=0.0, step=1.0)
        amount_out = st.number_input("Cashout Amount ($)", min_value=0.0, step=1.0)
        bonus_hit = st.radio("Bonus Hit?", ["Yes", "No"], horizontal=True)
        rule_followed = st.radio("Followed Rule?", ["Yes", "No"], horizontal=True)
        notes = st.text_area("Notes")
        submitted = st.form_submit_button("Add")

        if submitted:
            log_time = datetime.now().strftime("%Y-%m-%d %I:%M:%S %p")
            win_loss = amount_out - amount_in
            st.session_state.tracker.append({
                "Date/Time": log_time,
                "Game": game,
                "Amount In": amount_in,
                "Amount Out": amount_out,
                "Win/Loss": win_loss,
                "Bonus Hit": bonus_hit,
                "Rule Followed": rule_followed,
                "Notes": notes
            })
            st.rerun()

with tab2:
    st.subheader("🧾 Session Log")
    if not df.empty:
        df.index += 1
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No sessions logged yet.")
