
import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Profit Hopper", layout="centered")

# JS code to detect local time and pass to Streamlit
local_time = st.experimental_get_query_params().get("time", [None])[0]

# Initialize session state
if "tracker" not in st.session_state:
    st.session_state.tracker = []
if "local_time" not in st.session_state and local_time:
    st.session_state.local_time = local_time

# --- Sidebar Setup ---
with st.sidebar:
    st.header("🎯 Setup")
    bankroll = st.number_input("💵 Starting Bankroll ($)", min_value=10, value=100, step=10)
    sessions = st.number_input("🎮 Sessions", min_value=1, value=5)
    risk = st.selectbox("📊 Risk Level", ["Low", "Medium", "High"])
    profit_goal_percent = st.slider("🏁 Profit Goal (%)", 5, 100, 20)

# --- Strategy Logic ---
session_unit = bankroll / sessions
risk_factor = {"Low": 40, "Medium": 30, "High": 20}
max_bet = session_unit / risk_factor[risk]
profit_goal = bankroll * (1 + profit_goal_percent / 100)

# --- Updated Totals ---
df = pd.DataFrame(st.session_state.tracker)
total_in = df["Amount In"].sum() if not df.empty else 0
total_out = df["Amount Out"].sum() if not df.empty else 0
net = total_out - total_in

# --- Ultra-Compact Summary Display (just 3 lines) ---
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

# --- Tabs ---
tab1, tab2 = st.tabs(["📋 Tracker", "📊 Log"])

# --- Tracker Input ---
with tab1:
    st.subheader("➕ Add Session")
    with st.form("session_form", clear_on_submit=True):
        game = st.text_input("Game / Machine Name")
        amount_in = st.number_input("Amount Inserted ($)", min_value=0.0, step=1.0, key="amount_in")
        amount_out = st.number_input("Cashout Amount ($)", min_value=0.0, step=1.0, key="amount_out")
        bonus_hit = st.radio("Bonus Hit?", ["Yes", "No"], horizontal=True, key="bonus_hit")
        rule_followed = st.radio("Followed Rule?", ["Yes", "No"], horizontal=True, key="rule_followed")
        notes = st.text_area("Notes", key="notes")
        submitted = st.form_submit_button("Add")

        if submitted:
            if "local_time" in st.session_state:
                timestamp = st.session_state.local_time
            else:
                timestamp = datetime.now().strftime("%Y-%m-%d %I:%M:%S %p")
            win_loss = amount_out - amount_in
            st.session_state.tracker.append({
                "Date/Time": timestamp,
                "Game": game,
                "Amount In": amount_in,
                "Amount Out": amount_out,
                "Win/Loss": win_loss,
                "Bonus Hit": bonus_hit,
                "Rule Followed": rule_followed,
                "Notes": notes
            })
            st.rerun()

# --- Log Display ---
with tab2:
    st.subheader("🧾 Session Log")
    if not df.empty:
        df.index += 1
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No sessions logged yet.")

# --- JS injection for local time detection ---
st.markdown("""
<script>
const now = new Date();
const formatted = now.toLocaleString('en-US', {
  year: 'numeric', month: '2-digit', day: '2-digit',
  hour: '2-digit', minute: '2-digit', second: '2-digit',
  hour12: true
}).replace(',', '');
if (!window.location.search.includes("time=")) {
  window.location.search = '?time=' + encodeURIComponent(formatted);
}
</script>
""", unsafe_allow_html=True)
