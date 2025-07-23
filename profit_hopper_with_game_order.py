import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import pytz

# Attempt to use browser JS to detect timezone offset
try:
    from streamlit_js_eval import streamlit_js_eval
    _HAS_JS_EVAL = True
except Exception:
    _HAS_JS_EVAL = False

st.set_page_config(page_title="Profit Hopper", layout="centered")

# --- Session State Init ---
if "tracker" not in st.session_state:
    st.session_state.tracker = []
if "tz_offset_minutes" not in st.session_state:
    st.session_state.tz_offset_minutes = None
if "local_time_str" not in st.session_state:
    st.session_state.local_time_str = ""
if "local_tz_name" not in st.session_state:
    st.session_state.local_tz_name = None

# --- Detect Browser Timezone Offset ---
offset = None
if _HAS_JS_EVAL:
    try:
        # getTimezoneOffset() returns (UTC - Local) minutes
        off = streamlit_js_eval(js_expressions='new Date().getTimezoneOffset()', key='tz_off')
        if off is not None:
            offset = int(off)
    except Exception:
        offset = None

if offset is not None:
    st.session_state.tz_offset_minutes = offset
    utc_now = datetime.utcnow()
    local_dt = utc_now - timedelta(minutes=offset)  # Local = UTC - offset
else:
    # Fallback: Use America/Chicago (user request) if detection fails
    utc_now = datetime.utcnow().replace(tzinfo=pytz.utc)
    local_dt = utc_now.astimezone(pytz.timezone("America/Chicago"))

st.session_state.local_time_str = local_dt.strftime("%I:%M %p %m/%d/%Y")

# --- Sidebar settings ---
with st.sidebar:
    st.header("🎯 Setup")
    bankroll = st.number_input("💵 Starting Bankroll ($)", min_value=10, value=100, step=10)
    sessions = st.number_input("🎮 Sessions", min_value=1, value=5)
    risk = st.selectbox("📊 Risk Level", ["Low", "Medium", "High"])
    profit_goal_percent = st.slider("🏁 Profit Goal (%)", 5, 100, 20)

# --- Strategy calculations ---
session_unit = bankroll / sessions
risk_factor = {"Low": 40, "Medium": 30, "High": 20}
max_bet = session_unit / risk_factor[risk]
profit_goal = bankroll * (1 + profit_goal_percent / 100)

# --- Summary section ---
df = pd.DataFrame(st.session_state.tracker)
total_in = df["Amount In"].sum() if not df.empty else 0.0
total_out = df["Amount Out"].sum() if not df.empty else 0.0
net = total_out - total_in

st.markdown("### 📊 Quick Summary")
st.markdown(
    f"""<div style='line-height: 1.5; font-size: 16px;'>
    <b>💼 Bankroll</b>: Start ${bankroll:.0f} | Goal ${profit_goal:.0f}<br>
    <b>🧮 Strategy</b>: ${session_unit:.0f}/session | Max Bet ${max_bet:.2f}<br>
    <b>📈 Status</b>: In ${total_in:.0f} | Out ${total_out:.0f} | Net ${net:.0f}
    </div>""",
    unsafe_allow_html=True
)


# === Game Recommendation Logic ===
def get_recommended_games(session_unit, max_bet, risk):
    games = []

    if risk == "Low":
        games.append(("Jacks or Better Video Poker", "Play 1-credit at $0.25 or less; very low variance"))
        games.append(("Triple Double Bonus Poker", "Stick to 1 credit only; medium payout potential"))
        games.append(("88 Fortunes", f"Bet below ${min(max_bet, 1.76):.2f}; look for full pot"))
        games.append(("Dancing Drums", "Bet minimum; watch for near bonus triggers"))
        games.append(("Ultimate Fire Link", "Only play if balls > 450 and mini > $15"))
    elif risk == "Medium":
        games.append(("Buffalo Gold", f"Use in later sessions; keep bets under ${max_bet:.2f}"))
        games.append(("Lightning Link", "Check for high Mini/Major; bet under session unit"))
        games.append(("Quick Hit Platinum", "Only play when 6+ hits are close; low-med volatility"))
        games.append(("88 Fortunes", f"Medium bet around ${min(max_bet, 1.76):.2f}; ideal for medium risk"))
        games.append(("Cleopatra Keno", "Play 4-card version, low bet, consistent numbers"))
    else:  # High risk
        games.append(("Dragon Link", "Chase jackpots; end of session only"))
        games.append(("Buffalo Gold Max", "Final session Hail Mary play"))
        games.append(("5 Dragons Grand", "Look for bonus close to triggering"))
        games.append(("Quick Hit Riches", "Play if progressive meters are high"))
        games.append(("Video Poker - Double Double Bonus", "1 credit max; high payout volatility"))

    return games


# === Recommended Game Section ===
st.markdown("### 🎯 Recommended Game Order")
recommended = get_recommended_games(session_unit, max_bet, risk)
for idx, (game, note) in enumerate(recommended, 1):
    st.markdown(f"**{idx}. {game}** — {note}")

st.markdown("---")

tab1, tab2 = st.tabs(["📋 Tracker", "📊 Log"])

# --- Tracker Form ---
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
            win_loss = amount_out - amount_in
            # capture fresh timestamp at submit (so not stale)
            if st.session_state.tz_offset_minutes is not None:
                utc_now = datetime.utcnow()
                local_dt = utc_now - timedelta(minutes=st.session_state.tz_offset_minutes)
            else:
                utc_now = datetime.utcnow().replace(tzinfo=pytz.utc)
                local_dt = utc_now.astimezone(pytz.timezone("America/Chicago"))
            timestamp_str = local_dt.strftime("%I:%M %p %m/%d/%Y")
            st.session_state.tracker.append({
                "Date/Time": timestamp_str,
                "Game": game,
                "Amount In": amount_in,
                "Amount Out": amount_out,
                "Win/Loss": win_loss,
                "Bonus Hit": bonus_hit,
                "Rule Followed": rule_followed,
                "Notes": notes,
            })
            st.success("Session added.")
            st.rerun()

# --- Log Table ---
with tab2:
    st.subheader("🧾 Session Log")
    if not df.empty:
        df_display = df.copy()
        df_display.index += 1  # 1-based row numbers
        st.dataframe(df_display, use_container_width=True)
    else:
        st.info("No sessions logged yet.")

