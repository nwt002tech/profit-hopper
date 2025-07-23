
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import pytz

# Try to use JS eval to get timezone
try:
    from streamlit_js_eval import streamlit_js_eval
    _JS = True
except:
    _JS = False

st.set_page_config(page_title="📱 Profit Hopper", layout="centered")

# --- Session state ---
if "tracker" not in st.session_state:
    st.session_state.tracker = []
if "tz_offset_minutes" not in st.session_state:
    st.session_state.tz_offset_minutes = None

# --- Detect browser time offset ---
offset = None
if _JS:
    try:
        offset = streamlit_js_eval("new Date().getTimezoneOffset()", key="offset")
        if offset is not None:
            st.session_state.tz_offset_minutes = int(offset)
    except:
        offset = None

# --- Time function ---
def get_local_time():
    utc_now = datetime.utcnow()
    if st.session_state.tz_offset_minutes is not None:
        return (utc_now - timedelta(minutes=st.session_state.tz_offset_minutes)).strftime("%I:%M %p %m/%d/%Y")
    else:
        return utc_now.strftime("%I:%M %p %m/%d/%Y")

# --- Style ---
st.markdown("""
    <style>
    .block-container { padding-top: 1rem; padding-bottom: 2rem; }
    input, textarea, .stButton > button {
        font-size: 18px !important;
    }
    .stTabs [data-baseweb="tab-list"] {
        flex-wrap: wrap;
        justify-content: center;
    }
    </style>
""", unsafe_allow_html=True)

# --- App Header ---
st.markdown("## 🐸 Profit Hopper")
st.markdown("Track your bankroll, wins/losses, and strategy sessions — on the go!")

# --- Tabs ---
tab1, tab2 = st.tabs(["➕ Tracker", "📊 Log"])

# --- Form Tab ---
with tab1:
    st.markdown("### ➕ Add Session")
    with st.form("track", clear_on_submit=True):
        game = st.text_input("🎰 Game / Machine")
        in_amt = st.number_input("💸 Amount In", 0.0, 10000.0, step=1.0)
        out_amt = st.number_input("💵 Amount Out", 0.0, 10000.0, step=1.0)
        bonus = st.radio("🎁 Bonus Hit?", ["Yes", "No"], horizontal=True)
        rule = st.radio("📏 Followed Rule?", ["Yes", "No"], horizontal=True)
        notes = st.text_area("📝 Notes")
        go = st.form_submit_button("✅ Log Session")
        if go:
            net = out_amt - in_amt
            timestamp = get_local_time()
            st.session_state.tracker.append({
                "Date/Time": timestamp,
                "Game": game,
                "Amount In": in_amt,
                "Amount Out": out_amt,
                "Win/Loss": net,
                "Bonus Hit": bonus,
                "Rule Followed": rule,
                "Notes": notes
            })
            st.success("✅ Session Logged!")
            st.rerun()

# --- Log Tab ---
with tab2:
    st.markdown("### 🧾 Log History")
    df = pd.DataFrame(st.session_state.tracker)
    if not df.empty:
        df.index += 1
        st.dataframe(df, use_container_width=True)
        st.download_button("⬇️ Download CSV", data=df.to_csv(index=False), file_name="profit_hopper_log.csv")
    else:
        st.info("No sessions logged yet.")
