
import streamlit as st
import pandas as pd
from datetime import datetime
import pytz
import streamlit.components.v1 as components

st.set_page_config(page_title="Profit Hopper", layout="centered")

# Store session data
if "tracker" not in st.session_state:
    st.session_state.tracker = []
if "user_timezone" not in st.session_state:
    st.session_state.user_timezone = None

# JS to detect timezone string and send it to Streamlit
components.html("""
<script>
const tz = Intl.DateTimeFormat().resolvedOptions().timeZone;
const input = window.parent.document.querySelector('input[data-testid="user-tz-field"]');
if (input && tz) {
    input.value = tz;
    input.dispatchEvent(new Event("input", { bubbles: true }));
}
</script>
""", height=0)

# Hidden input to catch user's timezone
tz_input = st.text_input(" ", key="user-tz-field", label_visibility="collapsed")
if tz_input and not st.session_state.user_timezone:
    st.session_state.user_timezone = tz_input

# Convert UTC timestamp to user's timezone
def convert_utc_to_user_tz(utc_str, user_tz):
    try:
        utc_dt = datetime.strptime(utc_str, "%Y-%m-%d %H:%M:%S").replace(tzinfo=pytz.utc)
        local_dt = utc_dt.astimezone(pytz.timezone(user_tz))
        return local_dt.strftime("%Y-%m-%d %I:%M:%S %p")
    except Exception:
        return utc_str

# Sidebar
with st.sidebar:
    st.header("🎯 Setup")
    bankroll = st.number_input("💵 Starting Bankroll ($)", min_value=10, value=100, step=10)
    sessions = st.number_input("🎮 Sessions", min_value=1, value=5)
    risk = st.selectbox("📊 Risk Level", ["Low", "Medium", "High"])
    profit_goal_percent = st.slider("🏁 Profit Goal (%)", 5, 100, 20)

# Strategy logic
session_unit = bankroll / sessions
risk_factor = {"Low": 40, "Medium": 30, "High": 20}
max_bet = session_unit / risk_factor[risk]
profit_goal = bankroll * (1 + profit_goal_percent / 100)

# Summary section
df = pd.DataFrame(st.session_state.tracker)
total_in = df["Amount In"].sum() if not df.empty else 0
total_out = df["Amount Out"].sum() if not df.empty else 0
net = total_out - total_in

st.markdown("### 📊 Quick Summary")
st.markdown(
    f"<div style='line-height: 1.5; font-size: 16px;'>"
    f"<b>💼 Bankroll</b>: Start ${bankroll:.0f} | Goal ${profit_goal:.0f}<br>"
    f"<b>🧮 Strategy</b>: ${session_unit:.0f}/session | Max Bet ${max_bet:.2f}<br>"
    f"<b>📈 Status</b>: In ${total_in:.0f} | Out ${total_out:.0f} | Net ${net:.0f}"
    f"</div>",
    unsafe_allow_html=True
)

st.markdown("---")

tab1, tab2 = st.tabs(["📋 Tracker", "📊 Log"])

# Tracker form
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
            utc_now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
            win_loss = amount_out - amount_in
            st.session_state.tracker.append({
                "UTC Timestamp": utc_now,
                "Game": game,
                "Amount In": amount_in,
                "Amount Out": amount_out,
                "Win/Loss": win_loss,
                "Bonus Hit": bonus_hit,
                "Rule Followed": rule_followed,
                "Notes": notes
            })
            st.rerun()

# Log display
with tab2:
    st.subheader("🧾 Session Log")
    if not df.empty:
        user_tz = st.session_state.get("user_timezone", "UTC")
        df["Date/Time"] = df["UTC Timestamp"].apply(lambda x: convert_utc_to_user_tz(x, user_tz))
        df.index += 1
        display_df = df[["Date/Time", "Game", "Amount In", "Amount Out", "Win/Loss", "Bonus Hit", "Rule Followed", "Notes"]]
        st.dataframe(display_df, use_container_width=True)
    else:
        st.info("No sessions logged yet.")
