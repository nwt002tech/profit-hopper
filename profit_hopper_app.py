import streamlit as st
import pandas as pd
import numpy as np
from io import StringIO

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
        df['RTP'] = pd.to_numeric(df['RTP'], errors='coerce')  # Changed from Expected_RTP
        df['Min_Bet'] = pd.to_numeric(df['Min_Bet'], errors='coerce')
        df['Advantage_Play_Potential'] = pd.to_numeric(df['Advantage_Play_Potential'], errors='coerce')
        df['Volatility'] = pd.to_numeric(df['Volatility'], errors='coerce')
        df['Bonus_Frequency'] = pd.to_numeric(df['Bonus_Frequency'], errors='coerce')
        
        return df.dropna(subset=['RTP', 'Min_Bet'])
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
                (game_df['Min_Bet'] <= max_bet) &
                (game_df['RTP'].notna())  # Changed from Expected_RTP
            ].copy()
            
            if not filtered_games.empty:
                # Calculate score - using RTP instead of Expected_RTP
                filtered_games['Score'] = (
                    (filtered_games['RTP'] * 0.5) +  # Changed from Expected_RTP
                    (filtered_games['Bonus_Frequency'] * 0.2) +
                    (filtered_games['Advantage_Play_Potential'] * 0.2) +
                    ((6 - filtered_games['Volatility']) * 0.1)  # Inverse weighting
                )
                
                # Sort and display
                filtered_games = filtered_games.sort_values('Score', ascending=False)
                
                st.subheader(f"Recommended Games ({len(filtered_games)} matches)")
                
                for _, row in filtered_games.iterrows():
                    with st.container():
                        st.markdown(f"""
                        <div class="game-card