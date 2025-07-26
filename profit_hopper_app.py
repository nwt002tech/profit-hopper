
import streamlit as st
import pandas as pd

# Load the game list from GitHub
csv_url = "https://raw.githubusercontent.com/nwt002tech/profit-hopper/main/extended_game_list.csv"
df = pd.read_csv(csv_url)

# UI Configuration
st.set_page_config(page_title="Profit Hopper", layout="centered")

# Sidebar Inputs
st.sidebar.header("💼 Bankroll Settings")
total_bankroll = st.sidebar.number_input("Total Bankroll ($)", min_value=10, value=120)
session_count = st.sidebar.number_input("Number of Sessions", min_value=1, value=6)

# Calculated session values
session_bankroll = total_bankroll / session_count
max_bet = round(session_bankroll * 0.25, 2)

# Display top bar summary
st.markdown(f"""
### 🎯 Session Summary
- **Total Bankroll:** ${total_bankroll}
- **Sessions:** {session_count}
- **Per-Session Bankroll:** ${session_bankroll:.2f}
- **Recommended Max Bet:** ${max_bet}
""")

# Ensure numeric values
numeric_fields = ["Min_Bet", "Volatility", "Bonus_Frequency", "RTP", "Advantage_Play_Potential"]
for field in numeric_fields:
    df[field] = pd.to_numeric(df[field], errors="coerce")

# Filter games that match session limits
filtered = df[df["Min_Bet"] <= max_bet].copy()

# Apply scoring model
filtered["Score"] = (
    filtered["Advantage_Play_Potential"] * 0.3 +
    (filtered["Bonus_Frequency"] * 0.25) +
    (filtered["RTP"] * 0.002) -
    filtered["Volatility"] * 0.15
)
filtered["Stop_Loss"] = (session_bankroll * 0.6).round(2)
filtered = filtered.sort_values(by="Score", ascending=False)

# Display recommended games
st.subheader("✅ Recommended Games")
if filtered.empty:
    st.warning("No games meet the bankroll criteria. Try increasing bankroll or reducing session count.")
else:
    for _, row in filtered.iterrows():
        st.markdown(f"""
        ---
        **🎰 {row['Name']}**
        - 💰 Min Bet: ${row['Min_Bet']}
        - ⚖️ Volatility: {row['Volatility']}
        - 🎯 Bonus Frequency: {row['Bonus_Frequency']}
        - 🎲 RTP: {row['RTP']}%
        - 🧠 Advantage Play: {row['Advantage_Play_Potential']}
        - 🏦 Stop Loss: ${row['Stop_Loss']}
        - 🏨 Best Casino Type: {row['Best_Casino_Type']}
        - 🎁 Bonus Clues: _{row['Bonus_Trigger_Clues']}_
        - 💡 Tip: _{row['Tips']}_
        """)
