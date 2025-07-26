
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Profit Hopper", layout="wide")

# Load game list from GitHub CSV
@st.cache_data
def load_game_data():
    url = "https://raw.githubusercontent.com/nwt002tech/profit-hopper/main/extended_game_list.csv"
    df = pd.read_csv(url)

    # Convert 'Advantage_Play_Potential' from text to numeric
    ap_map = {"Low": 1, "Medium": 2, "High": 3}
    if df["Advantage_Play_Potential"].dtype == object:
        df["Advantage_Play_Potential"] = df["Advantage_Play_Potential"].map(ap_map)

    # Clean numeric fields
    for col in ["RTP", "Volatility", "Bonus_Frequency", "Advantage_Play_Potential"]:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    return df

# Game scoring engine
def recommend_games(df, session_bankroll, max_bet):
    stop_loss_value = round(session_bankroll * 0.6, 2)
    df["Stop_Loss"] = pd.Series(stop_loss_value, index=df.index).clip(lower=df["Min_Bet"])

    df["Score"] = (
        df["RTP"] * 0.3 +
        df["Bonus_Frequency"] * 0.3 +
        (3 - df["Volatility"]) * 0.2 +
        df["Advantage_Play_Potential"] * 0.2
    )

    df["Score"] = df["Score"].round(3)
    recommended = df[df["Min_Bet"] <= max_bet].sort_values(by="Score", ascending=False).reset_index(drop=True)
    return recommended

# Sidebar - session controls
st.sidebar.header("🎯 Session Setup")
total_bankroll = st.sidebar.number_input("Total Bankroll ($)", min_value=10, value=100, step=10)
total_sessions = st.sidebar.slider("Number of Sessions", 1, 20, 5)
session_bankroll = round(total_bankroll / total_sessions, 2)
max_bet = round(session_bankroll * 0.25, 2)

# Load games and compute recommendations
games_df = load_game_data()
recommended = recommend_games(games_df.copy(), session_bankroll, max_bet)

# Display Game Plan and Bankroll
st.markdown("### 💰 Bankroll Status")
st.markdown(f"**Total Bankroll:** ${total_bankroll:.2f} | **Sessions:** {total_sessions}")

st.markdown("### 🎯 Game Plan Summary")
st.markdown(f"**Bankroll/Session:** ${session_bankroll:.2f} | **Max Bet/Session:** ${max_bet:.2f}")

# Tabs for display
tabs = st.tabs(["📋 Game Plan", "📈 Tracker", "📊 Summary"])

with tabs[0]:
    st.markdown("### ✅ Recommended Games to Play")
    for idx, row in recommended.iterrows():
        st.markdown(f"""**{row['Name']}**
- 🎯 **Score:** {row['Score']}
- 💵 **Min Bet:** ${row['Min_Bet']}
- 🛑 **Stop Loss:** ${row['Stop_Loss']}
- 🔄 **Volatility:** {row['Volatility']}
- 🎰 **RTP:** {row['RTP']}%
- 🎁 **Bonus Frequency:** {row['Bonus_Frequency']}
- 📈 **Advantage Play Potential:** {row['Advantage_Play_Potential']}
- 📝 {row['Tips']}""")
        st.markdown("---")

with tabs[1]:
    st.markdown("### 📈 Tracker (Coming Soon)")

with tabs[2]:
    st.markdown("### 📊 Summary (Coming Soon)")
