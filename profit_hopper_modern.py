
def calculate_stop_loss(min_bet, session_unit, volatility, total_bankroll):
    risk_factor = session_unit / total_bankroll if total_bankroll > 0 else 1.0
    multiplier = {
        "Low": 4.0,
        "Medium": 3.0,
        "Medium-High": 2.5,
        "High": 2.0
    }.get(volatility, 2.5)
    adj_multiplier = multiplier * (1 - 0.5 * risk_factor)
    stop_loss = min(session_unit * 0.95, max(min_bet * adj_multiplier, min_bet * 2))
    return round(stop_loss, 2)



import streamlit as st
import pandas as pd
from datetime import datetime

# === Embedded Game Dataset with Stop-Loss ===
game_data = [{"Name": "88 Fortunes", "Min_Bet": 0.88, "RTP": 96.0, "Volatility": "Medium-High", "Notes": "Look for gold symbols filled and jackpot pot nearly full."}, {"Name": "Cleopatra", "Min_Bet": 0.2, "RTP": 95.5, "Volatility": "Medium", "Notes": "Watch for bonus symbol frequency and high wild activity."}, {"Name": "Buffalo Gold", "Min_Bet": 0.6, "RTP": 94.5, "Volatility": "High", "Notes": "Better when coin bonuses appear regularly. High volatility."}, {"Name": "Quick Hit Platinum", "Min_Bet": 0.3, "RTP": 95.0, "Volatility": "Medium-High", "Notes": "Check meter progression and number of visible symbols."}, {"Name": "Dragon Link", "Min_Bet": 0.5, "RTP": 95.0, "Volatility": "High", "Notes": "Preferable when fireball hold & spin occurs frequently."}, {"Name": "Dancing Drums", "Min_Bet": 0.88, "RTP": 96.1, "Volatility": "Medium-High", "Notes": "Best when drums appear often and gold pot is full."}, {"Name": "Lightning Link", "Min_Bet": 0.5, "RTP": 94.8, "Volatility": "High", "Notes": "Check progressive meter size and bonus rate."}, {"Name": "Video Keno", "Min_Bet": 0.25, "RTP": 92.0, "Volatility": "Low", "Notes": "Use overlapping patterns and slow progression."}, {"Name": "Miss Kitty", "Min_Bet": 0.5, "RTP": 95.1, "Volatility": "Medium", "Notes": "Better play when wild symbols are frequent early."}, {"Name": "Whales of Cash", "Min_Bet": 0.4, "RTP": 94.3, "Volatility": "Medium", "Notes": "Look for stacked symbols and bonus frequency."}]

def score_game(game, session_unit, risk_level, max_bet):
    if game["Min_Bet"] > max_bet:
        return 0
    rtp_score = game["RTP"]
    vol_score = {
        "Low": 2, "Medium": 1, "Medium-High": 0.5, "High": 0.3
    }.get(game["Volatility"], 1)
    risk_tolerance = {
        "Low": 1, "Medium": 1.5, "High": 2
    }[risk_level]
    return rtp_score * vol_score * risk_tolerance

def calculate_stop_loss(min_bet, session_unit, volatility):
    base_ratio = {
        "Low": 1.0, "Medium": 0.75, "Medium-High": 0.6, "High": 0.5
    }.get(volatility, 0.75)
    return round(max(min_bet * 3, session_unit * base_ratio), 2)

def get_recommended_games(session_unit, max_bet, risk, num_needed):
    scored = []
    for game in game_data:
        stop_loss = calculate_stop_loss(game["Min_Bet"], session_unit, game["Volatility"])
        game["Recommended_Stop_Loss"] = stop_loss
        score = score_game(game, session_unit, risk, max_bet)
        if score > 0:
            scored.append((score, game))
    sorted_games = sorted(scored, key=lambda x: x[0], reverse=True)
    return [g for _, g in sorted_games][:num_needed]

st.set_page_config(page_title="Profit Hopper", layout="centered")

if "tracker" not in st.session_state:
    st.session_state.tracker = []

with st.sidebar:
    st.header("🎯 Setup")
    initial_bankroll = st.number_input("💵 Starting Bankroll", min_value=10, value=100, step=10)
    total_sessions = st.number_input("🎮 Total Sessions", min_value=1, value=5)
    risk = st.selectbox("📊 Risk Level", ["Low", "Medium", "High"])
    profit_goal_percent = st.slider("🏁 Profit Goal (%)", 5, 100, 20)

df = pd.DataFrame(st.session_state.tracker)
total_in = df["Amount In"].sum() if not df.empty else 0
total_out = df["Amount Out"].sum() if not df.empty else 0
net = total_out - total_in
current_bankroll = initial_bankroll + net

remaining_sessions = max(1, total_sessions - len(st.session_state.tracker))
session_unit = current_bankroll / remaining_sessions
risk_factor = {"Low": 40, "Medium": 30, "High": 20}[risk]
max_bet = session_unit / risk_factor
profit_goal = initial_bankroll * (1 + profit_goal_percent / 100)

st.markdown("### 📊 Quick Summary")
st.markdown(
    f"""
    <div style='font-size:15px; line-height:1.6;'>
    💼 <b>Bankroll:</b> ${initial_bankroll:.0f} → Goal: ${profit_goal:.0f} → Now: ${current_bankroll:.0f}<br>
    🧮 <b>Strategy:</b> ${session_unit:.0f}/session • Max Bet: ${max_bet:.2f} • Sessions Left: {remaining_sessions}<br>
    📈 <b>Status:</b> In: ${total_in:.0f} • Out: ${total_out:.0f} • Net: ${net:.0f}
    </div>
    """, unsafe_allow_html=True
)

st.markdown("### 🎯 Game Recommendations")
num_needed = remaining_sessions + 3  # Always list more than needed
recommended = get_recommended_games(session_unit, max_bet, risk, num_needed)

if recommended:
    for idx, game in enumerate(recommended, 1):
        st.markdown(
            f"<b>{idx}. {game['Name']}</b><br>"
            f"🎰 Min Bet: ${game['Min_Bet']:.2f} | 🛑 Stop-Loss: ${game['Recommended_Stop_Loss']:.2f}<br>"
            f"📝 {game['Notes']}",
            unsafe_allow_html=True)
else:
    st.warning("No games match your current bankroll and session strategy.")

tab1, tab2 = st.tabs(["📋 Add Session", "🧾 Log"])
with tab1:
    st.subheader("➕ New Session Entry")
    with st.form("session_form", clear_on_submit=True):
        game = st.text_input("Game / Machine Name")
        amount_in = st.number_input("Amount Inserted", min_value=0.0, step=1.0)
        amount_out = st.number_input("Cashout Amount", min_value=0.0, step=1.0)
        col1, col2 = st.columns(2)
        with col1:
            bonus_hit = st.radio("Bonus Hit?", ["Yes", "No"], horizontal=True)
        with col2:
            rule_followed = st.radio("Followed Strategy?", ["Yes", "No"], horizontal=True)
        notes = st.text_area("Notes")
        submitted = st.form_submit_button("Add Session")
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
    st.subheader("📋 Session Log")
    if not df.empty:
        df.index += 1
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No sessions logged yet.")
