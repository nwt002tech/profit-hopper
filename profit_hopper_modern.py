
import streamlit as st
import pandas as pd
from datetime import datetime

# === Embedded Game Dataset ===
game_data = [{"Name": "Jacks or Better", "RTP": 99.54, "Volatility": "Low", "Bonus_Freq": "None", "Min_Bet": 0.25, "Notes": "High RTP. Best with full-pay version."}, {"Name": "Double Bonus Poker", "RTP": 99.11, "Volatility": "Medium", "Bonus_Freq": "None", "Min_Bet": 0.25, "Notes": "Requires skilled play. Great RTP."}, {"Name": "Cleopatra Keno", "RTP": 94.0, "Volatility": "Low", "Bonus_Freq": "Medium", "Min_Bet": 0.2, "Notes": "Time extender. Good early option."}, {"Name": "88 Fortunes", "RTP": 96.0, "Volatility": "Low", "Bonus_Freq": "Medium", "Min_Bet": 0.88, "Notes": "Only if pot appears full."}, {"Name": "Ultimate Fire Link", "RTP": 96.5, "Volatility": "Medium", "Bonus_Freq": "High", "Min_Bet": 0.5, "Notes": "Play only if ball count > 450."}, {"Name": "Lightning Link", "RTP": 96.1, "Volatility": "Medium-High", "Bonus_Freq": "Medium", "Min_Bet": 0.5, "Notes": "Look for high Mini/Major."}, {"Name": "Buffalo Gold", "RTP": 96.0, "Volatility": "High", "Bonus_Freq": "Low", "Min_Bet": 0.6, "Notes": "High variance. Good for last session."}, {"Name": "Dancing Drums", "RTP": 95.0, "Volatility": "Medium", "Bonus_Freq": "Medium", "Min_Bet": 0.88, "Notes": "Only if drums near full."}, {"Name": "Money Bags", "RTP": 94.89, "Volatility": "Medium", "Bonus_Freq": "Low", "Min_Bet": 0.5, "Notes": "Watch for bonus meter close to full."}, {"Name": "Dragon Link", "RTP": 96.0, "Volatility": "Medium", "Bonus_Freq": "Medium", "Min_Bet": 0.5, "Notes": "Best with high Mini/Major."}, {"Name": "Double Diamond", "RTP": 95.44, "Volatility": "Low", "Bonus_Freq": "None", "Min_Bet": 0.25, "Notes": "Classic 3-reel. Good early filler."}, {"Name": "Triple Double Bonus Poker", "RTP": 97.0, "Volatility": "High", "Bonus_Freq": "None", "Min_Bet": 0.25, "Notes": "Great if bankroll can swing."}, {"Name": "Huff N More Puff", "RTP": 96.0, "Volatility": "High", "Bonus_Freq": "Medium", "Min_Bet": 0.75, "Notes": "Trigger bonus with hats or major meter."}, {"Name": "Piggy Bankin", "RTP": 95.96, "Volatility": "Medium", "Bonus_Freq": "Medium", "Min_Bet": 0.5, "Notes": "Look for large pig cluster."}, {"Name": "Ocean Magic", "RTP": 96.09, "Volatility": "Medium", "Bonus_Freq": "Medium", "Min_Bet": 0.5, "Notes": "Bubble feature helps bonuses."}, {"Name": "Miss Kitty", "RTP": 94.76, "Volatility": "Medium", "Bonus_Freq": "Medium", "Min_Bet": 0.5, "Notes": "Sticky wilds in bonus."}, {"Name": "China Shores", "RTP": 96.1, "Volatility": "Medium", "Bonus_Freq": "High", "Min_Bet": 0.6, "Notes": "Free games can be frequent."}, {"Name": "Colossal Reels Spartacus", "RTP": 96.04, "Volatility": "High", "Bonus_Freq": "Medium", "Min_Bet": 0.5, "Notes": "Good for excitement rounds."}, {"Name": "Wonder 4 Tower", "RTP": 96.0, "Volatility": "High", "Bonus_Freq": "Medium", "Min_Bet": 0.8, "Notes": "Only use if multiple games show near bonus."}, {"Name": "Cash Falls", "RTP": 95.85, "Volatility": "Medium", "Bonus_Freq": "Medium", "Min_Bet": 0.6, "Notes": "Good if cash meter close to fill."}, {"Name": "Quick Hit", "RTP": 95.97, "Volatility": "Medium", "Bonus_Freq": "High", "Min_Bet": 0.5, "Notes": "Watch number of quick hits on reels."}, {"Name": "Wild Wild Buffalo", "RTP": 96.0, "Volatility": "High", "Bonus_Freq": "Medium", "Min_Bet": 0.75, "Notes": "Only with wilds close or bet boost."}, {"Name": "Power 4 Poker", "RTP": 98.76, "Volatility": "Low", "Bonus_Freq": "None", "Min_Bet": 1.0, "Notes": "Avoid unless you split bank properly."}, {"Name": "Hot Roll Poker", "RTP": 98.5, "Volatility": "Medium", "Bonus_Freq": "Medium", "Min_Bet": 0.5, "Notes": "Use when dice symbols line up."}, {"Name": "All Star Poker", "RTP": 97.81, "Volatility": "Low", "Bonus_Freq": "None", "Min_Bet": 0.25, "Notes": "Time filler. Great RTP."}, {"Name": "Vegas Star Poker", "RTP": 97.89, "Volatility": "Low", "Bonus_Freq": "None", "Min_Bet": 0.25, "Notes": "Good intro option."}, {"Name": "Mega Vault", "RTP": 95.6, "Volatility": "Medium", "Bonus_Freq": "Low", "Min_Bet": 0.5, "Notes": "Only with vault near full."}, {"Name": "Crystal Forest", "RTP": 96.0, "Volatility": "Medium", "Bonus_Freq": "High", "Min_Bet": 0.5, "Notes": "Use with maxed enchant bonuses."}, {"Name": "Wild Life Extreme", "RTP": 95.83, "Volatility": "Medium", "Bonus_Freq": "Medium", "Min_Bet": 0.6, "Notes": "Good with frequent re-triggers."}, {"Name": "Golden Jungle", "RTP": 96.01, "Volatility": "Medium", "Bonus_Freq": "Medium", "Min_Bet": 0.88, "Notes": "Prefer when temple meter is high."}, {"Name": "Rakin Bacon", "RTP": 96.01, "Volatility": "Medium", "Bonus_Freq": "Medium", "Min_Bet": 0.88, "Notes": "Great when pig looks large."}, {"Name": "Tarzan", "RTP": 95.8, "Volatility": "High", "Bonus_Freq": "Medium", "Min_Bet": 0.6, "Notes": "Big variance. Use late game."}, {"Name": "Lobstermania", "RTP": 94.0, "Volatility": "Low", "Bonus_Freq": "Low", "Min_Bet": 0.5, "Notes": "Pure fun. Avoid as main play."}, {"Name": "Wheel of Fortune", "RTP": 94.1, "Volatility": "Medium", "Bonus_Freq": "Medium", "Min_Bet": 0.75, "Notes": "Try if wheel bonus is due."}, {"Name": "The Vault", "RTP": 95.5, "Volatility": "High", "Bonus_Freq": "Medium", "Min_Bet": 0.5, "Notes": "Only when near bonus trigger."}, {"Name": "Zeus", "RTP": 95.97, "Volatility": "Medium", "Bonus_Freq": "Medium", "Min_Bet": 0.4, "Notes": "Nice animations. Avg performance."}, {"Name": "Heidi's Bier Haus", "RTP": 96.13, "Volatility": "Medium", "Bonus_Freq": "High", "Min_Bet": 0.5, "Notes": "Watch for keg spins."}, {"Name": "Quick Hit Platinum", "RTP": 96.5, "Volatility": "Medium", "Bonus_Freq": "High", "Min_Bet": 0.5, "Notes": "Best with 6+ quick hits showing."}, {"Name": "King of Africa", "RTP": 96.0, "Volatility": "Medium", "Bonus_Freq": "Low", "Min_Bet": 0.4, "Notes": "Better after 3 dry bonuses."}, {"Name": "Reel 'Em In!", "RTP": 95.0, "Volatility": "Medium", "Bonus_Freq": "Medium", "Min_Bet": 0.3, "Notes": "Use when fish meter is stacked."}, {"Name": "Wheel of Prosperity", "RTP": 96.09, "Volatility": "Medium", "Bonus_Freq": "Medium", "Min_Bet": 0.6, "Notes": "Look for bonus symbol patterns."}, {"Name": "Stacked Wilds", "RTP": 95.6, "Volatility": "High", "Bonus_Freq": "Low", "Min_Bet": 0.6, "Notes": "Great in final risk sessions."}, {"Name": "3x4x5x Times Pay", "RTP": 95.91, "Volatility": "Medium", "Bonus_Freq": "None", "Min_Bet": 0.25, "Notes": "Classic multiplier. Low variance."}, {"Name": "Money Storm", "RTP": 95.5, "Volatility": "High", "Bonus_Freq": "Low", "Min_Bet": 0.6, "Notes": "Huge wins possible, rare though."}, {"Name": "Vault of Riches", "RTP": 95.3, "Volatility": "Medium", "Bonus_Freq": "Medium", "Min_Bet": 0.5, "Notes": "Meter matters."}, {"Name": "Tower Stack", "RTP": 96.0, "Volatility": "Medium", "Bonus_Freq": "High", "Min_Bet": 0.5, "Notes": "Ideal with full stack or feature."}, {"Name": "Carnival of Mystery", "RTP": 96.1, "Volatility": "Medium", "Bonus_Freq": "Medium", "Min_Bet": 0.6, "Notes": "Look for bonus wheels."}, {"Name": "Wild Nights", "RTP": 95.9, "Volatility": "Medium", "Bonus_Freq": "Medium", "Min_Bet": 0.5, "Notes": "Stars = best time to play."}, {"Name": "Gold Pays", "RTP": 94.8, "Volatility": "Low", "Bonus_Freq": "None", "Min_Bet": 0.25, "Notes": "Flat RTP game, use only early."}]

# === Game Scoring Function ===
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

def get_recommended_games(session_unit, max_bet, risk, num_needed):
    scored = []
    for game in game_data:
        score = score_game(game, session_unit, risk, max_bet)
        if score > 0:
            scored.append((score, game))
    sorted_games = sorted(scored, key=lambda x: x[0], reverse=True)
    return [g for _, g in sorted_games][:num_needed]

# === Streamlit Config ===
st.set_page_config(page_title="Profit Hopper", layout="centered")

if "tracker" not in st.session_state:
    st.session_state.tracker = []

with st.sidebar:
    st.header("🎯 Setup")
    initial_bankroll = st.number_input("💵 Starting Bankroll ($)", min_value=10, value=100, step=10)
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

# === Summary Header ===
st.markdown("### 📊 Quick Summary")
st.markdown(
    f"<div style='line-height: 1.5; font-size: 16px;'>"
    f"<b>💼 Bankroll</b>: Start ${initial_bankroll:.0f} | Goal ${profit_goal:.0f} | Now ${current_bankroll:.0f}<br>"
    f"<b>🧮 Strategy</b>: ${session_unit:.0f}/session | Max Bet ${max_bet:.2f} | Remaining Sessions: {remaining_sessions}<br>"
    f"<b>📈 Status</b>: In ${total_in:.0f} | Out ${total_out:.0f} | Net ${net:.0f}"
    "</div>",
    unsafe_allow_html=True
)

# === Game Recommendations ===
st.markdown("### 🎯 Recommended Game Order")
num_needed = remaining_sessions + 2
recommended = get_recommended_games(session_unit, max_bet, risk, num_needed)

if recommended:
    st.markdown("_Choose next available game from the top down. All meet your current bankroll strategy._")
    for idx, game in enumerate(recommended, 1):
        st.markdown(f"**{idx}. {game['Name']}** — Min Bet: ${game['Min_Bet']:.2f} — {game['Notes']}")
else:
    st.warning("No games match your current bankroll and session strategy.")

# === Tracker Section ===
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
