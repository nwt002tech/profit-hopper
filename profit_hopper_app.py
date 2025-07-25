
import streamlit as st
import pandas as pd

# Load game data from CSV
csv_path = "extended_game_list.csv"
games_df = pd.read_csv(csv_path)

# Get user input for bankroll settings
st.title("🎰 Profit Hopper: Casino Bankroll Strategy App")
total_bankroll = st.number_input("Enter Total Bankroll ($):", min_value=20, value=100, step=10)
total_sessions = st.number_input("Enter Number of Sessions:", min_value=1, value=5, step=1)
session_bankroll = total_bankroll / total_sessions
max_bet = session_bankroll * 0.25

# Display compact summary
st.markdown("### 💰 Bankroll Status")
st.markdown(f"**Total Bankroll:** ${total_bankroll:.2f} | **Sessions:** {total_sessions}")
st.markdown("### 🎯 Game Plan Summary")
st.markdown(f"**Bankroll/Session:** ${session_bankroll:.2f} | **Max Bet/Session:** ${max_bet:.2f}")

# Recommendation function
def recommend_games(df, session_bankroll, max_bet):
    # Ensure numeric scoring fields
    for col in ["RTP", "Bonus_Frequency", "Advantage_Play_Potential", "Volatility"]:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    # Score calculation
    df["Score"] = (
        df["RTP"] * 0.4 +
        df["Bonus_Frequency"] * 0.2 +
        df["Advantage_Play_Potential"] * 0.2 +
        df["Volatility"] * -0.2
    )

    df["Min_Bet_OK"] = df["Min_Bet"] <= max_bet
    df["Stop_Loss"] = df["Min_Bet"].apply(lambda x: max(round(session_bankroll * 0.6, 2), x))

    filtered = df[df["Min_Bet_OK"]]
    sorted_df = filtered.sort_values(by="Score", ascending=False)

    return sorted_df.head(10)

# Run recommendation logic
recommended = recommend_games(games_df, session_bankroll, max_bet)

# Display recommendations
st.subheader("📋 Recommended Games")
if recommended.empty:
    st.warning("No games found matching the session parameters.")
else:
    for _, row in recommended.iterrows():
        st.markdown(f"""
**{row['Name']}**  
RTP: {row['RTP']} | Bonus Freq: {row['Bonus_Frequency']} | Advantage Play: {row['Advantage_Play_Potential']} | Volatility: {row['Volatility']}  
Min Bet: ${row['Min_Bet']} | Stop-Loss: ${row['Stop_Loss']:.2f}  
Tips: {row.get('Tips', 'No tips provided.')}
""")

