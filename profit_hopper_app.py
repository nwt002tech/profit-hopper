import streamlit as st
import pandas as pd
import re
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

# Configure page for mobile
st.set_page_config(layout="wide", initial_sidebar_state="collapsed", page_title="Profit Hopper Casino Manager")

# Define descriptive mapping functions
def map_advantage(value):
    mapping = {
        5: "⭐️⭐️⭐️⭐️⭐️ Excellent advantage opportunities",
        4: "⭐️⭐️⭐️⭐️ Strong potential for skilled players",
        3: "⭐️⭐️⭐️ Moderate advantage play value",
        2: "⭐️⭐️ Low advantage value",
        1: "⭐️ Minimal advantage potential"
    }
    return mapping.get(value, "Unknown")

def map_volatility(value):
    mapping = {
        1: "📈 Very low volatility (frequent small wins)",
        2: "📈 Low volatility",
        3: "📊 Medium volatility",
        4: "📉 High volatility",
        5: "📉 Very high volatility (rare big wins)"
    }
    return mapping.get(value, "Unknown")

def map_bonus_freq(value):
    if value >= 0.4:
        return "🎁🎁🎁 Very frequent bonuses"
    elif value >= 0.3:
        return "🎁🎁 Frequent bonus features"
    elif value >= 0.2:
        return "🎁 Occasional bonuses"
    elif value >= 0.1:
        return "🎁 Rare bonuses"
    else:
        return "🎁 Very rare bonuses"

# Normalize column names
def normalize_column_name(name):
    """Convert column names to consistent lowercase with underscores"""
    return re.sub(r'\W+', '_', name.lower().strip())

# Load game data with caching
@st.cache_data(ttl=3600)  # Refresh every hour
def load_game_data():
    try:
        url = "https://raw.githubusercontent.com/nwt002tech/profit-hopper/2b42fd9699f541c353极3d80f84b6f8ef73ba60/extended_game_list.csv"
        df = pd.read_csv(url)
        
        # Normalize column names
        df.columns = [normalize_column_name(col) for col in df.columns]
        
        # Create standard column names
        col_map = {
            'rtp': ['rtp', 'expected_rtp'],
            'min_bet': ['min_bet', 'minbet', 'minimum_bet', 'min_bet_amount'],
            'advantage_play_potential': ['advantage_play_potential', 'app', 'advantage_potential'],
            'volatility': ['volatility', 'vol'],
            'bonus_frequency': ['bonus_frequency', 'bonus_freq', 'bon极_rate'],
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
    if 'bankroll' not in st.session_state:
        st.session_state.bankroll = 1000.0
    if 'session_count' not in st.session_state:
        st.session_state.session_count = 10
    
    # CSS for sticky header and mobile optimization
    st.markdown("""
    <style>
    /* Unique class names to avoid conflicts */
    .ph-sticky-header {
        position: sticky;
        top: 0;
        background: white;
        z-index: 100;
        padding: 10px 0;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    
    .ph-game-card {
        padding: 15px;
        margin: 15px 0;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        background-color: #f8f9fa;
        border-left: 4px solid #4e89ae;
    }
    
    .ph-game-title {
        font-weight: bold;
        font-size: 1.1rem;
        margin-bottom: 8px;
        color: #2c3e50;
    }
    
    .ph-game-detail {
        margin: 6px 0;
        padding-left: 25px;
        position: relative;
        font-size: 0.95rem;
    }
    
    .ph-game-detail::before {
        content: "•";
        position: absolute;
        left: 10px;
        color: #4e89ae;
        font-size: 1.2rem;
    }
    
    .ph-stop-loss {
        color: #e74c3c;
        font-weight: bold;
    }
    
    .ph-game-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
        gap: 20px;
    }
    
    @media (max-width: 768px) {
        .ph-game-grid {
            grid-template-columns: 1fr;
        }
        .ph-game-card {
            padding: 12px;
            margin: 12px 0;
        }
        .ph-game-detail {
            padding-left: 20px;
        }
        .ph-game-detail::before {
            left: 5px;
        }
    }
    
    .session-card {
        padding: 15px;
        margin: 10px 0;
        border-radius: 8px;
        background-color: #f8f9fa;
        border-left: 4px solid #3498db;
    }
    
    .positive-profit {
        color: #27ae60;
        font-weight: bold;
    }
    
    .negative-profit {
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
                                            value=st.session_state.bankroll,
                                            step=100.0,
                                            format="%.2f",
                                            key='bankroll_input')
            st.session_state.bankroll = total_bankroll
        with col2:
            num_sessions = st.number_input("📅 Number of Sessions", 
                                          min_value=1, 
                                          value=st.session_state.session_count,
                                          step=1,
                                          key='session_count_input')
            st.session_state.session_count = num_sessions
    
    # Calculations
    session_bankroll = total_bankroll / num_sessions
    max_bet = session_bankroll * 0.25
    stop_loss = session_bankroll * 0.6
    
    # Sticky header
    st.markdown(f"""
    <div class="ph-sticky-header">
        <div style="display:flex; justify-content:space-around; text-align:center">
            <div><strong>💰 Total Bankroll</strong><br>${total_bankroll:,.2f}</div>
            <div><strong>📅 Session Bankroll</strong><br>${session_bankroll:,.2f}</div>
            <div><strong>💸 Max Bet</strong><br>${max_bet:,.2f}</div>
            <div><strong>🚫 Stop Loss</strong><br><span class="ph-stop-loss">${stop_loss:,.2f}</span></div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Main tabs
    tab1, tab2, tab3 = st.tabs(["🎮 Game Plan", "📊 Session Tracker", "📈 Bankroll Analytics"])
    
    # Game Plan Tab
    with tab1:
        # Load and filter games
        game_df = load_game_data()
        
        if not game_df.empty:
            # Game filters
            st.subheader("Game Filters")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                min_rtp = st.slider("Minimum RTP (%)", 85.0, 99.9, 92.0, step=0.1)
                game_type = st.selectbox("Game Type", ["All"] + list(game_df['type'].unique()))
                
            with col2:
                max_min_bet = st.slider("Max Min Bet", 
                                       float(game_df['min_bet'].min()), 
                                       float(game_df['min_bet'].max() * 2), 
                                       float(max_bet), 
                                       step=1.0)
                advantage_filter = st.selectbox("Advantage Play Potential", 
                                              ["All", "High (4-5)", "Medium (3)", "Low (1-2)"])
                
            with col3:
                volatility_filter = st.selectbox("Volatility", 
                                               ["All", "Low (1-2)", "Medium (3)", "High (4-5)"])
                search_query = st.text_input("Search Game Name")
            
            # Apply filters
            filtered_games = game_df[
                (game_df['min_bet'] <= max_min_bet) &
                (game_df['rtp'] >= min_rtp) &
                (game_df['rtp'].notna())
            ]
            
            # Apply game type filter
            if game_type != "All":
                filtered_games = filtered_games[filtered_games['type'] == game_type]
                
            # Apply advantage filter
            if advantage_filter == "High (4-5)":
                filtered_games = filtered_games[filtered_games['advantage_play_potential'] >= 4]
            elif advantage_filter == "Medium (3)":
                filtered_games = filtered_games[filtered_games['advantage_play_potential'] == 3]
            elif advantage_filter == "Low (1-2)":
                filtered_games = filtered_games[filtered_games['advantage_play_potential'] <= 2]
                
            # Apply volatility filter
            if volatility_filter == "Low (1-2)":
                filtered_games = filtered_games[filtered_games['volatility'] <= 2]
            elif volatility_filter == "Medium (3)":
                filtered_games = filtered_games[filtered_games['volatility'] == 3]
            elif volatility_filter == "High (4-5)":
                filtered_games = filtered_games[filtered_games['volatility'] >= 4]
                
            # Apply search filter
            if search_query:
                filtered_games = filtered_games[
                    filtered_games['game_name'].str.contains(search_query, case=False)
                ]
            
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
                st.caption(f"Showing games with RTP ≥ {min_rtp}% and min bet ≤ ${max_min_bet:,.2f}")
                
                # Display games in a responsive grid
                st.markdown('<div class="ph-game-grid">', unsafe_allow_html=True)
                
                for _, row in filtered_games.head(50).iterrows():  # Limit to top 50
                    # Use unique class names prefixed with "ph-"
                    game_card = f"""
                    <div class="ph-game-card">
                        <div class="ph-game-title">🎰 {row['game_name']}</div>
                        
                        <div class="ph-game-detail">
                            <strong>🗂️ Type:</strong> {row['type']}
                        </div>
                        
                        <div class="ph-game-detail">
                            <strong>💸 Min Bet:</strong> ${row['min_bet']:,.2f}
                        </div>
                        
                        <div class="ph-game-detail">
                            <strong>🧠 Advantage Play:</strong> {map_advantage(int(row['advantage_play_potential']))}
                        </div>
                        
                        <div class="ph-game-detail">
                            <strong>🎲 Volatility:</strong> {map_volatility(int(row['volatility']))}
                        </div>
                        
                        <div class="ph-game-detail">
                            <strong>🎁 Bonus Frequency:</strong> {map_bonus_freq(row['bonus_frequency'])}
                        </div>
                        
                        <div class="ph-game-detail">
                            <strong>🔢 RTP:</strong> {row['rtp']:.2f}%
                        </div>
                        
                        <div class="ph-game-detail">
                            <strong>💡 Tips:</strong> {row['tips']}
                        </div>
                    </div>
                    """
                    st.markdown(game_card, unsafe_allow_html=True)
                
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.warning("No games match your current filters. Try adjusting your criteria.")
        else:
            st.error("Failed to load game data. Please check the CSV format and column names.")
    
    # Session Tracker Tab
    with tab2:
        st.subheader("Session Tracker")
        
        with st.expander("➕ Add New Session", expanded=True):
            with st.form("session_form"):
                col1, col2 = st.columns(2)
                with col1:
                    session_date = st.date_input("📅 Date", value=datetime.today())
                    money_in = st.number_input("💵 Money In", min_value=0.0, value=float(session_bankroll))
                with col2:
                    game_played = st.selectbox("🎮 Game Played", options=["Select Game"] + list(game_df['game_name'].unique()) if not game_df.empty else ["Select Game"])
                    money_out = st.number_input("💰 Money Out", min_value=0.0, value=0.0)
                
                session_notes = st.text_area("📝 Session Notes", placeholder="Record any observations, strategies, or important events during the session...")
                
                submitted = st.form_submit_button("💾 Save Session")
                
                if submitted:
                    if game_played == "Select Game":
                        st.warning("Please select a game")
                    else:
                        profit = money_out - money_in
                        st.session_state.session_log.append({
                            "date": session_date,
                            "game": game_played,
                            "money_in": money_in,
                            "money_out": money_out,
                            "profit": profit,
                            "notes": session_notes
                        })
                        st.success(f"Session added: ${profit:+,.2f} profit")
                        st.session_state.bankroll += profit
                        st.experimental_rerun()
        
        if st.session_state.session_log:
            st.subheader("Session History")
            
            # Sort sessions by date descending
            sorted_sessions = sorted(st.session_state.session_log, key=lambda x: x['date'], reverse=True)
            
            for i, session in enumerate(sorted_sessions, 1):
                profit = session['profit']
                profit_class = "positive-profit" if profit >= 0 else "negative-profit"
                
                session_card = f"""
                <div class="session-card">
                    <div><strong>📅 {session['date']}</strong> | 🎮 {session['game']}</div>
                    <div>💵 In: ${session['money_in']:,.2f} | 💰 Out: ${session['money_out']:,.2f} | 
                    <span class="{profit_class}">📈 Profit: ${profit:+,.2f}</span></div>
                    <div><strong>📝 Notes:</strong> {session['notes']}</div>
                    <div style="margin-top: 5px;">
                        <button onclick="deleteSession({i-1})" style="background-color: #e74c3c; color: white; border: none; padding: 5px 10px; border-radius: 4px; cursor: pointer;">Delete</button>
                    </div>
                </div>
                """
                st.markdown(session_card, unsafe_allow_html=True)
            
            # JavaScript for session deletion
            st.markdown("""
            <script>
            function deleteSession(index) {
                const data = {index: index};
                fetch('/delete_session', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(data)
                }).then(response => {
                    if (response.ok) {
                        location.reload();
                    }
                });
            }
            </script>
            """, unsafe_allow_html=True)
        else:
            st.info("No sessions recorded yet. Add your first session above.")
    
    # Bankroll Analytics Tab
    with tab3:
        st.subheader("Bankroll Analytics")
        
        if not st.session_state.session_log:
            st.info("No sessions recorded yet. Add sessions to see analytics.")
        else:
            # Calculate cumulative values
            cumulative_profit = sum(session['profit'] for session in st.session_state.session_log)
            current_bankroll = st.session_state.bankroll
            
            # Calculate performance metrics
            total_invested = sum(session['money_in'] for session in st.session_state.session_log)
            roi = (cumulative_profit / total_invested) * 100 if total_invested > 0 else 0
            avg_session_profit = cumulative_profit / len(st.session_state.session_log)
            
            # Display key metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("💰 Current Bankroll", f"${current_bankroll:,.2f}",
                         delta=f"${cumulative_profit:+,.2f}")
            with col2:
                st.metric("📈 Total Profit/Loss", f"${cumulative_profit:+,.2f}")
            with col3:
                st.metric("📊 ROI", f"{roi:.1f}%")
            
            # Profit/loss chart
            profit_history = [0]
            dates = [st.session_state.session_log[0]['date']]
            cumulative = 0
            
            for session in sorted(st.session_state.session_log, key=lambda x: x['date']):
                cumulative += session['profit']
                profit_history.append(cumulative)
                dates.append(session['date'])
            
            st.subheader("Bankroll Growth")
            chart_data = pd.DataFrame({
                "Date": dates,
                "Bankroll": [st.session_state.bankroll - cumulative_profit] + [st.session_state.bankroll - cumulative_profit + p for p in profit_history[1:]]
            }).set_index("Date")
            
            st.line_chart(chart_data)
            
            # Game performance analysis
            st.subheader("Game Performance")
            game_performance = {}
            for session in st.session_state.session_log:
                game = session['game']
                if game not in game_performance:
                    game_performance[game] = {
                        'sessions': 0,
                        'total_profit': 0,
                        'total_invested': 0
                    }
                game_performance[game]['sessions'] += 1
                game_performance[game]['total_profit'] += session['profit']
                game_performance[game]['total_invested'] += session['money_in']
            
            # Create performance DataFrame
            perf_df = pd.DataFrame.from_dict(game_performance, orient='index')
            perf_df['ROI'] = (perf_df['total_profit'] / perf_df['total_invested']) * 100
            perf_df['Avg Profit'] = perf_df['total_profit'] / perf_df['sessions']
            perf_df = perf_df.sort_values('ROI', ascending=False)
            
            st.dataframe(perf_df[['sessions', 'total_profit', 'Avg Profit', 'ROI']].rename(columns={
                'sessions': 'Sessions',
                'total_profit': 'Total Profit',
                'Avg Profit': 'Avg Profit/Session',
                'ROI': 'ROI (%)'
            }).style.format({
                'Total Profit': '${:,.2f}',
                'Avg Profit/Session': '${:,.2f}',
                'ROI (%)': '{:.1f}%'
            }))
            
            # Win/Loss distribution
            st.subheader("Win/Loss Distribution")
            profits = [s['profit'] for s in st.session_state.session_log]
            wins = [p for p in profits if p >= 0]
            losses = [p for p in profits if p < 0]
            
            if wins or losses:
                fig, ax = plt.subplots()
                ax.hist([wins, losses], bins=15, label=['Wins', 'Losses'], color=['green', 'red'], stacked=True)
                ax.axvline(x=0, color='gray', linestyle='--')
                ax.set_title("Profit/Loss Distribution")
                ax.set_xlabel("Profit/Loss Amount")
                ax.set_ylabel("Frequency")
                ax.legend()
                st.pyplot(fig)
            else:
                st.info("No win/loss data available")

# Run the app
if __name__ == "__main__":
    main()