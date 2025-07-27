import streamlit as st
import pandas as pd
import re

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

# Normalize column names
def normalize_column_name(name):
    """Convert column names to consistent lowercase with underscores"""
    return re.sub(r'\W+', '_', name.lower().strip())

# Load game data with caching
@st.cache_data
def load_game_data():
    try:
        url = "https://raw.githubusercontent.com/nwt002tech/profit-hopper/2b42fd9699f541c3532363d80f84b6f8ef73ba60/extended_game_list.csv"
        df = pd.read_csv(url)
        
        # Normalize column names
        df.columns = [normalize_column_name(col) for col in df.columns]
        
        # Create standard column names
        col_map = {
            'rtp': ['rtp', 'expected_rtp'],
            'min_bet': ['min_bet', 'minbet', 'minimum_bet', 'min_bet_amount'],
            'advantage_play_potential': ['advantage_play_potential', 'app', 'advantage_potential'],
            'volatility': ['volatility', 'vol'],
            'bonus_frequency': ['bonus_frequency', 'bonus_freq', 'bonus_rate'],
            'game_name': ['game_name', 'name', 'title', 'game'],
            'type': ['type', 'game_type', 'category'],
            'tips': ['tips', 'tip', 'strategy']
        }
        
        # Create final standardized columns
        for standard, variants in col_map.items():
            for variant in variants:
                if variant in df.columns:
                    df[standard] = df[variant]
                    break
        
        # Check required columns
        if 'rtp' not in df.columns or 'min_bet' not in df.columns:
            missing = [col for col in ['rtp', 'min_bet'] if col not in df.columns]
            st.error(f"Missing required columns: {', '.join(missing)}")
            return pd.DataFrame()
        
        # Convert columns to numeric
        numeric_cols = ['rtp', 'min_bet', 'advantage_play_potential', 'volatility', 'bonus_frequency']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Set defaults for optional columns
        if 'advantage_play_potential' not in df.columns:
            df['advantage_play_potential'] = 3  # Default: moderate
        if 'volatility' not in df.columns:
            df['volatility'] = 3  # Default: medium
        if 'bonus_frequency' not in df.columns:
            df['bonus_frequency'] = 0.2  # Default: occasional
            
        # Set defaults for display columns
        if 'game_name' not in df.columns:
            df['game_name'] = "Unknown Game"
        if 'type' not in df.columns:
            df['type'] = "Unknown"
        if 'tips' not in df.columns:
            df['tips'] = "No tips available"
        
        # Drop rows with missing required data
        return df.dropna(subset=['rtp', 'min_bet'])
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
    /* Sticky header styles */
    .sticky-header {
        position: sticky;
        top: 0;
        background: white;
        z-index: 100;
        padding: 10px 0;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    
    /* Game card styles */
    .game-card {
        padding: 15px;
        margin: 15px 0;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        background-color: #f8f9fa;
        border-left: 4px solid #4e89ae;
    }
    
    /* Game title styles */
    .game-title {
        font-weight: bold;
        font-size: 1.1rem;
        margin-bottom: 8px;
        color: #2c3e50;
    }
    
    /* Game detail styles */
    .game-detail {
        margin: 6px 0;
        padding-left: 25px;
        position: relative;
        font-size: 0.95rem;
    }
    
    /* Emoji bullet styles */
    .game-detail::before {
        content: "•";
        position: absolute;
        left: 10px;
        color: #4e89ae;
        font-size: 1.2rem;
    }
    
    /* Mobile responsive styles */
    @media (max-width: 768px) {
        .game-card {
            padding: 12px;
            margin: 12px 0;
        }
        .game-detail {
            padding-left: 20px;
        }
        .game-detail::before {
            left: 5px;
        }
    }
    
    /* Stop loss highlight */
    .stop-loss {
        color: #e74c3c;
        font-weight: bold;
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
            # Apply filters
            filtered_games = game_df[
                (game_df['min_bet'] <= max_bet) &
                (game_df['rtp'].notna())
            ].copy()
            
            if not filtered_games.empty:
                # Calculate score
                filtered_games['Score'] = (
                    (filtered_games['rtp'] * 0.5) +
                    (filtered_games['bonus_frequency'] * 0.2) +
                    (filtered_games['advantage_play_potential'] * 0.2) +
                    ((6 - filtered_games['volatility']) * 0.1)
                )
                
                # Sort and display
                filtered_games = filtered_games.sort_values('Score', ascending=False)
                
                st.subheader(f"Recommended Games ({len(filtered_games)} matches)")
                
                for _, row in filtered_games.iterrows():
                    game_card = f"""
                    <div class="game-card">
                        <div class="game-title">🎰 {row['game_name']}</div>
                        
                        <div class="game-detail">
                            <strong>🗂️ Type:</strong> {row['type']}
                        </div>
                        
                        <div class="game-detail">
                            <strong>💸 Min Bet:</strong> ${row['min_bet']:,.2f}
                        </div>
                        
                        <div class="game-detail">
                            <strong>🚫 Stop Loss:</strong> 
                            <span class="stop-loss">${stop_loss:,.2f}</span>
                        </div>
                        
                        <div class="game-detail">
                            <strong>🧠 Advantage Play:</strong> {map_advantage(int(row['advantage_play_potential']))}
                        </div>
                        
                        <div class="game-detail">
                            <strong>🎲 Volatility:</strong> {map_volatility(int(row['volatility']))}
                        </div>
                        
                        <div class="game-detail">
                            <strong>🎁 Bonus Frequency:</strong> {map_bonus_freq(row['bonus_frequency'])}
                        </div>
                        
                        <div class="game-detail">
                            <strong>🔢 RTP:</strong> {row['rtp']:.2f}%
                        </div>
                        
                        <div class="game-detail">
                            <strong>💡 Tips:</strong> {row['tips']}
                        </div>
                    </div>
                    """
                    st.markdown(game_card, unsafe_allow_html=True)
            else:
                st.warning("No games match your current bankroll and settings")
        else:
            st.error("Failed to load game data. Please check the CSV format and column names.")
    
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
                <div style="margin: 10px 0; padding: 10px; background: #f8f9fa; border-radius: 8px;">
                    <strong>Session {i}:</strong><br>
                    💵 In: ${session['money_in']:,.2f} | 
                    💰 Out: ${session['money_out']:,.2f} | 
                    <span style="color:{color}; font-weight:bold;">📈 Profit: ${profit:+,.2f}</span>
                </div>
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