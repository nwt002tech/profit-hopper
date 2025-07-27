import streamlit as st
import pandas as pd
import numpy as np

# Configure page for mobile
st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

# Define descriptive mapping functions
def map_advantage(value):
    mapping = {
        5: "Excellent advantage opportunities",
        4: "Strong potential for skilled players",
        3: "Moderate advantage play value",
        2: "Low advantage value",
        1: "Minimal advantage potential"
    }
    return mapping.get(value, "Unknown")

def map_volatility(value):
    mapping = {
        1: "Very low volatility (frequent small wins)",
        2: "Low volatility",
        3: "Medium volatility",
        4: "High volatility",
        5: "Very high volatility (rare big wins)"
    }
    return mapping.get(value, "Unknown")

def map_bonus_freq(value):
    if value >= 0.4:
        return "Very frequent bonuses"
    elif value >= 0.3:
        return "Frequent bonus features"
    elif value >= 0.2:
        return "Occasional bonuses"
    elif value >= 0.1:
        return "Rare bonuses"
    else:
        return "Very rare bonuses"

# Load game data with caching
@st.cache_data
def load_game_data():
    try:
        url = "https://raw.githubusercontent.com/nwt002tech/profit-hopper/2b42fd9699f541c3532363d80f84b6f8ef73ba60/extended_game_list.csv"
        df = pd.read_csv(url)
        
        # Clean and convert columns - using correct column names
        df['RTP'] = pd.to_numeric(df['RTP'], errors='coerce')
        df['Min Bet'] = pd.to_numeric(df['Min Bet'], errors='coerce')
        df['Advantage Play Potential'] = pd.to_numeric(df['Advantage Play Potential'], errors='coerce')
        df['Volatility'] = pd.to_numeric(df['Volatility'], errors='coerce')
        df['Bonus Frequency'] = pd.to_numeric(df['Bonus Frequency'], errors='coerce')
        
        return df.dropna(subset=['RTP', 'Min Bet'])
    except Exception as e:
        st.error(f"Error loading game data: {str(e)}")
        return pd.DataFrame()

# Main app function
def main():
    # Initialize session state for tracker
    if 'session_log' not in st.session_state:
        st.session_state.session_log = []
    if 'bankroll_history' not in st.session_state:
        st.session_state.bankroll_history = []
    
    # CSS for sticky header and mobile optimization
    st.markdown("""
    <style>
    .sticky-header {
        position: sticky;
        top: 0;
        background: white;
        z-index: 100;
        padding: 10px 0;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    .game-card {
        padding: 15px;
        margin: 10px 0;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    .game-detail {
        margin: 4px 0;
        padding-left: 15px;
    }
    @media (max-width: 768px) {
        .game-detail { padding-left: 10px; }
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Input panel
    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            total_bankroll = st.number_input("💰 Total Bankroll", 
                                            min_value=0.0, 
                                            value=1000.0,
                                            step=100.0,
                                            format="%.2f")
        with col2:
            num_sessions = st.number_input("📅 Number of Sessions", 
                                          min_value=1, 
                                          value=10,
                                          step=1)
    
    # Calculations
    session_bankroll = total_bankroll / num_sessions
    max_bet = session_bankroll * 0.25
    stop_loss = session_bankroll * 0.6
    
    # Sticky header
    st.markdown(f"""
    <div class="sticky-header">
        <div style="display:flex; justify-content:space-around; text-align:center">
            <div><strong>💰 Total Bankroll</strong><br>${total_bankroll:,.2f}</div>
            <div><strong>📅 Session Bankroll</strong><br>${session_bankroll:,.2f}</div>
            <div><strong>💸 Max Bet</strong><br>${max_bet:,.2f}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Main tabs
    tab1, tab2, tab3 = st.tabs(["🎮 Game Plan", "📊 Tracker", "📈 Summary"])
    
    # Game Plan Tab
    with tab1:
        # Load and filter games
        game_df = load_game_data()
        
        if not game_df.empty:
            # Apply filters - using correct column names
            filtered_games = game_df[
                (game_df['Min Bet'] <= max_bet) &
                (game_df['RTP'].notna())
            ].copy()
            
            if not filtered_games.empty:
                # Calculate score
                filtered_games['Score'] = (
                    (filtered_games['RTP'] * 0.5) +
                    (filtered_games['Bonus Frequency'] * 0.2) +
                    (filtered_games['Advantage Play Potential'] * 0.2) +
                    ((6 - filtered_games['Volatility']) * 0.1)
                )
                
                # Sort and display
                filtered_games = filtered_games.sort_values('Score', ascending=False)
                
                st.subheader(f"Recommended Games ({len(filtered_games)} matches)")
                
                for _, row in filtered_games.iterrows():
                    # Use correct column names from CSV
                    game_card = f"""
                    <div class="game-card">
                        <div><strong>🎰 Name:</strong> {row['Game Name']}</div>
                        <div><strong>🗂️ Type:</strong> {row['Type']}</div>
                        <div><strong>💸 Min Bet:</strong> ${row['Min Bet']:,.2f}</div>
                        <div><strong>🚫 Stop Loss:</strong> ${stop_loss:,.2f}</div>
                        <div class="game-detail"><strong>🧠 Advantage Play:</strong> {map_advantage(int(row['Advantage Play Potential']))}</div>
                        <div class="game-detail"><strong>🎲 Volatility:</strong> {map_volatility(int(row['Volatility']))}</div>
                        <div class="game-detail"><strong>🎁 Bonus Frequency:</strong> {map_bonus_freq(row['Bonus Frequency'])}</div>
                        <div class="game-detail"><strong>🔢 RTP:</strong> {row['RTP']:.2f}%</div>
                        <div class="game-detail"><strong>💡 Tips:</strong> {row['Tips']}</div>
                    </div>
                    """
                    st.markdown(game_card, unsafe_allow_html=True)
            else:
                st.warning("No games match your current bankroll and settings")
        else:
            st.error("Failed to load game data. Please check your connection.")
    
    # Tracker Tab
    with tab2:
        st.subheader("Session Tracker")
        
        with st.form("session_form"):
            col1, col2 = st.columns(2)
            with col1:
                money_in = st.number_input("💵 Money In", min_value=0.0, value=float(session_bankroll))
            with col2:
                money_out = st.number_input("💰 Money Out", min_value=0.0, value=0.0)
            
            submitted = st.form_submit_button("➕ Add Session")
            
            if submitted:
                profit = money_out - money_in
                st.session_state.session_log.append({
                    "money_in": money_in,
                    "money_out": money_out,
                    "profit": profit
                })
                st.success(f"Session added: ${profit:+,.2f} profit")
    
        if st.session_state.session_log:
            st.subheader("Session History")
            for i, session in enumerate(st.session_state.session_log, 1):
                profit = session['profit']
                color = "green" if profit >= 0 else "red"
                st.markdown(f"""
                **Session {i}:**  
                💵 In: ${session['money_in']:,.2f} | 
                💰 Out: ${session['money_out']:,.2f} | 
                <span style="color:{color}">📈 Profit: ${profit:+,.2f}</span>
                """, unsafe_allow_html=True)
    
    # Summary Tab
    with tab3:
        st.subheader("Bankroll Summary")
        
        if not st.session_state.session_log:
            st.info("No sessions recorded yet")
        else:
            # Calculate cumulative values
            cumulative_profit = sum(session['profit'] for session in st.session_state.session_log)
            current_bankroll = total_bankroll + cumulative_profit
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("💰 Current Bankroll", f"${current_bankroll:,.2f}",
                         delta=f"${cumulative_profit:+,.2f}")
            with col2:
                st.metric("📈 Total Profit/Loss", f"${cumulative_profit:+,.2f}")
            
            # Profit/loss chart
            profit_history = [0]
            for session in st.session_state.session_log:
                profit_history.append(profit_history[-1] + session['profit'])
            
            st.subheader("Profit/Loss Trend")
            st.line_chart(pd.DataFrame({
                "Session": range(len(profit_history)),
                "Profit": profit_history
            }).set_index("Session"))

if __name__ == "__main__":
    main()