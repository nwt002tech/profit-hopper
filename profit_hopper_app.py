import streamlit as st
import pandas as pd
import re
import numpy as np
from datetime import datetime
import altair as alt
import base64

# Configure page for mobile
st.set_page_config(layout="wide", initial_sidebar_state="expanded", page_title="Profit Hopper Casino Manager")

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
        url = "https://raw.githubusercontent.com/nwt002tech/profit-hopper/main/extended_game_list.csv"
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
        required_cols = ['rtp', 'min_bet']
        missing = [col for col in required_cols if col not in df.columns]
        if missing:
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

# CSV download helper
def get_csv_download_link(df, filename):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    return f'<a href="data:file/csv;base64,{b64}" download="{filename}">Download CSV</a>'

# Main app function
def main():
    # Initialize session state for tracker
    if 'session_log' not in st.session_state:
        st.session_state.session_log = []
    if 'current_trip_id' not in st.session_state:
        st.session_state.current_trip_id = 1
    if 'casino_list' not in st.session_state:
        st.session_state.casino_list = sorted([
            "L'auberge Lake Charles",
            "Golden Nugget Lake Charles",
            "Caesar's Horseshoe Lake Charles",
            "Delta Downs",
            "Island View",
            "Paragon Marksville",
            "Coushatta"
        ])
    if 'trip_settings' not in st.session_state:
        st.session_state.trip_settings = {
            'casino': st.session_state.casino_list[0] if st.session_state.casino_list else "",
            'starting_bankroll': 1000.0,
            'num_sessions': 10
        }
    
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
    
    .trip-card {
        padding: 15px;
        margin: 10px 0;
        border-radius: 8px;
        background-color: #e3f2fd;
        border-left: 4px solid #1976d2;
    }
    
    .positive-profit {
        color: #27ae60;
        font-weight: bold;
    }
    
    .negative-profit {
        color: #e74c3c;
        font-weight: bold;
    }
    
    .download-button {
        background-color: #4CAF50;
        color: white;
        padding: 8px 16px;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        font-size: 16px;
        margin: 4px 2px;
        cursor: pointer;
        border-radius: 4px;
        border: none;
    }
    
    .trip-info-box {
        background-color: #e8f5e9;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 20px;
        border-left: 4px solid #4caf50;
    }
    
    .trip-id-badge {
        background-color: #1976d2;
        color: white;
        padding: 5px 10px;
        border-radius: 4px;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header with logo and title
    st.markdown("""
    <div style="text-align:center; padding:20px 0; background:linear-gradient(135deg, #1a2a6c, #b21f1f, #fdbb2d); border-radius:10px; margin-bottom:30px;">
        <h1 style="color:white; margin:0;">🏆 Profit Hopper Casino Manager</h1>
        <p style="color:white; margin:0;">Smart Bankroll Management & Game Recommendations</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar for trip settings
    with st.sidebar:
        st.header("Trip Settings")
        
        # Trip ID display
        st.markdown(f"""
        <div style="display:flex; align-items:center; margin-bottom:20px;">
            <span style="font-weight:bold; margin-right:10px;">Current Trip ID:</span>
            <span class="trip-id-badge">{st.session_state.current_trip_id}</span>
        </div>
        """, unsafe_allow_html=True)
        
        # Casino selection
        new_casino = st.text_input("Add New Casino")
        if new_casino and new_casino not in st.session_state.casino_list:
            st.session_state.casino_list.append(new_casino)
            st.session_state.casino_list.sort()
            st.session_state.trip_settings['casino'] = new_casino
            st.success(f"Added {new_casino} to casino list")
        
        casino = st.selectbox("Casino", 
                             options=st.session_state.casino_list,
                             index=st.session_state.casino_list.index(
                                 st.session_state.trip_settings['casino']
                             ) if st.session_state.trip_settings['casino'] in st.session_state.casino_list else 0,
                             key='casino_select')
        st.session_state.trip_settings['casino'] = casino
        
        # Bankroll and sessions
        starting_bankroll = st.number_input("Starting Bankroll ($)", 
                                           min_value=0.0, 
                                           value=st.session_state.trip_settings['starting_bankroll'],
                                           step=100.0,
                                           format="%.2f",
                                           key='bankroll_input')
        st.session_state.trip_settings['starting_bankroll'] = starting_bankroll
        
        num_sessions = st.number_input("Number of Sessions", 
                                      min_value=1, 
                                      value=st.session_state.trip_settings['num_sessions'],
                                      step=1,
                                      key='session_count_input')
        st.session_state.trip_settings['num_sessions'] = num_sessions
        
        # New trip button
        if st.button("Start New Trip"):
            st.session_state.current_trip_id += 1
            st.session_state.session_log = []
            st.success(f"Started new trip! Trip ID: {st.session_state.current_trip_id}")
        
        st.markdown("---")
        
        # Trip summary
        st.subheader("Trip Summary")
        trip_sessions = [s for s in st.session_state.session_log if s['trip_id'] == st.session_state.current_trip_id]
        trip_profit = sum(s['profit'] for s in trip_sessions)
        current_bankroll = st.session_state.trip_settings['starting_bankroll'] + trip_profit
        
        st.markdown(f"**Casino:** {st.session_state.trip_settings['casino']}")
        st.markdown(f"**Starting Bankroll:** ${st.session_state.trip_settings['starting_bankroll']:,.2f}")
        st.markdown(f"**Current Bankroll:** ${current_bankroll:,.2f}")
        st.markdown(f"**Sessions Completed:** {len(trip_sessions)}/{st.session_state.trip_settings['num_sessions']}")
        
        st.markdown("---")
        st.warning("""
        **Gambling Risk Notice:**  
        - These strategies don't guarantee profits  
        - Never gamble with money you can't afford to lose  
        - Set strict loss limits before playing  
        - Gambling addiction help: 1-800-522-4700
        """)
    
    # Calculations
    session_bankroll = st.session_state.trip_settings['starting_bankroll'] / st.session_state.trip_settings['num_sessions']
    max_bet = session_bankroll * 0.25
    stop_loss = session_bankroll * 0.6
    
    # Current trip sessions
    current_trip_sessions = [s for s in st.session_state.session_log if s['trip_id'] == st.session_state.current_trip_id]
    trip_profit = sum(s['profit'] for s in current_trip_sessions)
    current_bankroll = st.session_state.trip_settings['starting_bankroll'] + trip_profit
    
    # Sticky header
    st.markdown(f"""
    <div class="ph-sticky-header">
        <div style="display:flex; justify-content:space-around; text-align:center">
            <div><strong>💰 Current Bankroll</strong><br>${current_bankroll:,.2f}</div>
            <div><strong>📅 Session Bankroll</strong><br>${session_bankroll:,.2f}</div>
            <div><strong>💸 Max Bet</strong><br>${max_bet:,.2f}</div>
            <div><strong>🚫 Stop Loss</strong><br><span class="ph-stop-loss">${stop_loss:,.2f}</span></div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Main tabs
    tab1, tab2, tab3 = st.tabs(["🎮 Game Plan", "📊 Session Tracker", "📈 Trip Analytics"])
    
    # Game Plan Tab
    with tab1:
        st.info("Find the best games for your bankroll based on RTP, volatility, and advantage play potential")
        
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
                
                for _, row in filtered_games.head(50).iterrows():
                    # Create the game card HTML
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
                    
                    # Render the game card with HTML interpretation
                    st.markdown(game_card, unsafe_allow_html=True)
                
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.warning("No games match your current filters. Try adjusting your criteria.")
        else:
            st.error("Failed to load game data. Please check the CSV format and column names.")
    
    # Session Tracker Tab
    with tab2:
        st.info("Track your gambling sessions to monitor performance and bankroll growth")
        
        # Trip info box
        st.markdown(f"""
        <div class="trip-info-box">
            <div style="display:flex; justify-content:space-between; margin-bottom:10px;">
                <div><strong>Current Trip:</strong> #{st.session_state.current_trip_id}</div>
                <div><strong>Casino:</strong> {st.session_state.trip_settings['casino']}</div>
            </div>
            <div style="display:flex; justify-content:space-between;">
                <div><strong>Starting Bankroll:</strong> ${st.session_state.trip_settings['starting_bankroll']:,.2f}</div>
                <div><strong>Current Bankroll:</strong> ${current_bankroll:,.2f}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.subheader("Session Tracker")
        
        with st.expander("➕ Add New Session", expanded=True):
            with st.form("session_form"):
                col1, col2 = st.columns(2)
                with col1:
                    session_date = st.date_input("📅 Date", value=datetime.today())
                    money_in = st.number_input("💵 Money In", 
                                              min_value=0.0, 
                                              value=float(session_bankroll),
                                              step=5.0)  # Increment by $5
                with col2:
                    game_options = ["Select Game"] + list(game_df['game_name'].unique()) if not game_df.empty else ["Select Game"]
                    game_played = st.selectbox("🎮 Game Played", options=game_options)
                    money_out = st.number_input("💰 Money Out", 
                                               min_value=0.0, 
                                               value=0.0,
                                               step=5.0)  # Increment by $5
                
                session_notes = st.text_area("📝 Session Notes", placeholder="Record any observations, strategies, or important events during the session...")
                
                submitted = st.form_submit_button("💾 Save Session")
                
                if submitted:
                    if game_played == "Select Game":
                        st.warning("Please select a game")
                    else:
                        profit = money_out - money_in
                        st.session_state.session_log.append({
                            "trip_id": st.session_state.current_trip_id,
                            "date": session_date.strftime("%Y-%m-%d"),
                            "casino": st.session_state.trip_settings['casino'],
                            "game": game_played,
                            "money_in": money_in,
                            "money_out": money_out,
                            "profit": profit,
                            "notes": session_notes
                        })
                        st.success(f"Session added: ${profit:+,.2f} profit")
        
        # Display current trip sessions
        current_trip_sessions = [s for s in st.session_state.session_log if s['trip_id'] == st.session_state.current_trip_id]
        
        if current_trip_sessions:
            st.subheader(f"Trip #{st.session_state.current_trip_id} Sessions")
            
            # Sort sessions by date descending
            sorted_sessions = sorted(current_trip_sessions, key=lambda x: x['date'], reverse=True)
            
            for idx, session in enumerate(sorted_sessions):
                profit = session['profit']
                profit_class = "positive-profit" if profit >= 0 else "negative-profit"
                
                session_card = f"""
                <div class="session-card">
                    <div><strong>📅 {session['date']}</strong> | 🎮 {session['game']}</div>
                    <div>💵 In: ${session['money_in']:,.2f} | 💰 Out: ${session['money_out']:,.2f} | 
                    <span class="{profit_class}">📈 Profit: ${profit:+,.2f}</span></div>
                    <div><strong>📝 Notes:</strong> {session['notes']}</div>
                </div>
                """
                st.markdown(session_card, unsafe_allow_html=True)
            
            # Export sessions to CSV
            st.subheader("Export Data")
            if st.button("💾 Export Session History to CSV"):
                session_df = pd.DataFrame(current_trip_sessions)
                st.markdown(get_csv_download_link(session_df, f"trip_{st.session_state.current_trip_id}_sessions.csv"), unsafe_allow_html=True)
        else:
            st.info("No sessions recorded for this trip yet. Add your first session above.")
    
    # Trip Analytics Tab
    with tab3:
        st.info("Analyze your trip performance and track your bankroll growth")
        
        if not current_trip_sessions:
            st.info("No sessions recorded for this trip yet. Add sessions to see analytics.")
        else:
            # Calculate cumulative values
            trip_profit = sum(s['profit'] for s in current_trip_sessions)
            current_bankroll = st.session_state.trip_settings['starting_bankroll'] + trip_profit
            
            # Calculate performance metrics
            total_invested = sum(s['money_in'] for s in current_trip_sessions)
            roi = (trip_profit / total_invested) * 100 if total_invested > 0 else 0
            avg_session_profit = trip_profit / len(current_trip_sessions)
            
            # Display key metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("💰 Current Bankroll", f"${current_bankroll:,.2f}",
                         delta=f"${trip_profit:+,.2f}")
            with col2:
                st.metric("📈 Total Profit/Loss", f"${trip_profit:+,.2f}")
            with col3:
                st.metric("📊 ROI", f"{roi:.1f}%")
            
            # Bankroll growth chart
            bankroll_history = [st.session_state.trip_settings['starting_bankroll']]
            dates = [min(s['date'] for s in current_trip_sessions)]
            cumulative = 0
            
            for session in sorted(current_trip_sessions, key=lambda x: x['date']):
                cumulative += session['profit']
                bankroll_history.append(st.session_state.trip_settings['starting_bankroll'] + cumulative)
                dates.append(session['date'])
            
            st.subheader("Bankroll Growth")
            chart_data = pd.DataFrame({
                "Date": dates,
                "Bankroll": bankroll_history
            })
            st.line_chart(chart_data.set_index("Date"))
            
            # Game performance analysis
            st.subheader("Game Performance")
            game_performance = {}
            for session in current_trip_sessions:
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
            
            # Win/Loss distribution using Altair
            st.subheader("Win/Loss Distribution")
            profits = [s['profit'] for s in current_trip_sessions]
            
            if profits:
                df = pd.DataFrame({
                    'Profit': profits,
                    'Type': ['Win' if p >= 0 else 'Loss' for p in profits]
                })
                
                chart = alt.Chart(df).mark_bar().encode(
                    alt.X("Profit:Q", bin=alt.Bin(maxbins=20), title='Profit/Loss Amount'),
                    alt.Y('count()', title='Frequency'),
                    color=alt.Color('Type', scale=alt.Scale(
                        domain=['Win', 'Loss'],
                        range=['#27ae60', '#e74c3c']
                    ))
                ).properties(
                    title='Profit/Loss Distribution'
                )
                
                st.altair_chart(chart, use_container_width=True)
            else:
                st.info("No profit data available")
                
            # Export analytics data
            st.subheader("Export Analytics")
            if st.button("📊 Export Trip Analytics to CSV"):
                analytics_df = pd.DataFrame({
                    'Metric': ['Trip ID', 'Casino', 'Starting Bankroll', 'Current Bankroll', 
                              'Total Profit/Loss', 'ROI', 'Avg Session Profit', 'Sessions Completed'],
                    'Value': [st.session_state.current_trip_id, st.session_state.trip_settings['casino'], 
                             st.session_state.trip_settings['starting_bankroll'], current_bankroll,
                             trip_profit, f"{roi}%", avg_session_profit, len(current_trip_sessions)]
                })
                st.markdown(get_csv_download_link(analytics_df, f"trip_{st.session_state.current_trip_id}_analytics.csv"), unsafe_allow_html=True)

# Run the app
if __name__ == "__main__":
    main()