
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Profit Hopper", layout="centered")

# Apply custom CSS for tighter line spacing
st.markdown(
    """
    <style>
        .game-detail p {
            margin: 0;
            line-height: 1.0;
            font-size: 0.95em;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# Dummy data for demonstration
data = {
    "Name": ["Stinkin’ Rich", "Buffalo Gold"],
    "Type": ["Slot", "Slot"],
    "Min_Bet": [0.96, 0.40],
    "Stop_Loss": [12.00, 10.00],
    "Advantage_Play_Potential": [1.0, 0.8],
    "Volatility": [2, 3],
    "Bonus_Frequency": [0.29, 0.35],
    "Expected_RTP": [97.16, 96.00],
    "Tips": [
        "Play when bonus frequency is high.",
        "Look for machines in bonus state."
    ]
}
df = pd.DataFrame(data)

# Display games
st.title("🎰 Recommended Games")

for index, row in df.iterrows():
    with st.container():
        st.markdown(f"""
        ### {row['Name']}
        <div class="game-detail">
        <p>🎰 Type: {row['Type']}</p>
        <p>💸 Min Bet: {row['Min_Bet']}</p>
        <p>🚫 Stop Loss: {row['Stop_Loss']}</p>
        <p>🧠 Advantage Play: {row['Advantage_Play_Potential']}</p>
        <p>🎲 Volatility: {row['Volatility']}</p>
        <p>🎁 Bonus Frequency: {row['Bonus_Frequency']}</p>
        <p>🔢 RTP: {row['Expected_RTP']}</p>
        <p>💡 Tips: {row['Tips']}</p>
        </div>
        """, unsafe_allow_html=True)
