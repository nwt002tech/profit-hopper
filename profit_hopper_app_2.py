import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# Initialize session state
if 'bankroll_history' not in st.session_state:
    st.session_state.bankroll_history = []
if 'simulation_results' not in st.session_state:
    st.session_state.simulation_results = None

# Page config
st.set_page_config(
    page_title="Casino Bankroll Strategy Advisor",
    page_icon="🎰",
    layout="wide"
)

# Main title
st.title("🎲 Casino Bankroll Management Strategy")
st.subheader("Maximize your winning potential while minimizing risk")

# Sidebar inputs
with st.sidebar:
    st.header("Bankroll Parameters")
    initial_bankroll = st.number_input("Initial Bankroll ($)", min_value=100, value=1000, step=100)
    risk_tolerance = st.select_slider("Risk Tolerance", options=["Conservative", "Moderate", "Aggressive"])
    betting_strategy = st.selectbox("Betting Strategy", ["Fixed Fraction", "Kelly Criterion", "Martingale", "D'Alembert"])
    game_type = st.selectbox("Game Type", ["Blackjack", "Roulette", "Craps", "Baccarat", "Slots"])
    house_edge = st.slider("House Edge (%)", min_value=0.1, max_value=20.0, value=5.0, step=0.1) / 100
    
    # Strategy-specific parameters
    if betting_strategy == "Kelly Criterion":
        win_probability = st.slider("Win Probability", min_value=0.1, max_value=0.9, value=0.48, step=0.01)
        win_payout = st.slider("Win Payout (x bet)", min_value=1.0, max_value=10.0, value=2.0, step=0.1)
    
    st.divider()
    st.caption("Developed by Casino Strategy Pro™")

# Main content columns
col1, col2 = st.columns([1, 1])

# Calculate strategy
with col1:
    st.header("Recommended Strategy")
    
    # Calculate bet size based on strategy
    if betting_strategy == "Fixed Fraction":
        if risk_tolerance == "Conservative":
            fraction = 0.01
        elif risk_tolerance == "Moderate":
            fraction = 0.025
        else:  # Aggressive
            fraction = 0.05
        
        bet_size = initial_bankroll * fraction
        st.metric("Recommended Bet Size", f"${bet_size:.2f}")
        st.info(f"Bet {fraction*100:.1f}% of your bankroll on each wager")
        
    elif betting_strategy == "Kelly Criterion":
        # Kelly formula: f = (bp - q) / b
        # Where f = fraction of bankroll to bet
        # b = net odds (payout - 1)
        # p = win probability
        # q = loss probability (1 - p)
        b = win_payout - 1
        p = win_probability
        q = 1 - p
        kelly_fraction = (b * p - q) / b
        
        # Apply risk tolerance adjustment
        if risk_tolerance == "Conservative":
            fraction = kelly_fraction * 0.5
        elif risk_tolerance == "Moderate":
            fraction = kelly_fraction * 0.75
        else:  # Aggressive
            fraction = kelly_fraction
        
        bet_size = initial_bankroll * fraction
        st.metric("Optimal Bet Fraction", f"{fraction*100:.2f}%")
        st.metric("Recommended Bet Size", f"${bet_size:.2f}")
        
    elif betting_strategy == "Martingale":
        st.metric("Base Bet Size", "$25.00")
        st.warning("Double bet after each loss. Reset to base after win.")
        st.info("High risk strategy - requires large bankroll")
        
    elif betting_strategy == "D'Alembert":
        st.metric("Base Bet Size", "$50.00")
        st.warning("Increase bet by base after loss. Decrease by base after win.")
        st.info("Moderate risk progression strategy")
    
    # Bankroll management tips
    st.divider()
    st.subheader("Bankroll Management Tips")
    st.write("1. Never bet more than 5% of your bankroll on a single wager")
    st.write("2. Set win/loss limits before you start playing")
    st.write("3. Keep detailed records of all your gambling sessions")
    st.write("4. Avoid chasing losses - take breaks when needed")
    st.write("5. Consider the house edge when choosing games")

# Simulation and visualization
with col2:
    st.header("Bankroll Simulation")
    
    # Simulation parameters
    num_sessions = st.slider("Number of Gambling Sessions", 1, 100, 20)
    bets_per_session = st.slider("Bets per Session", 1, 100, 20)
    
    if st.button("Run Simulation", key="simulate"):
        # Initialize bankroll
        bankroll = initial_bankroll
        history = [bankroll]
        
        # Strategy-specific parameters
        if betting_strategy == "Fixed Fraction":
            fraction = 0.025 if risk_tolerance == "Moderate" else 0.01 if risk_tolerance == "Conservative" else 0.05
        elif betting_strategy == "Kelly Criterion":
            fraction = max(0.01, min(0.2, fraction))  # Constrain fraction
        
        # Run simulation
        for session in range(num_sessions):
            session_bankroll = bankroll
            for bet in range(bets_per_session):
                # Determine bet size based on strategy
                if betting_strategy == "Fixed Fraction":
                    bet_amount = fraction * session_bankroll
                elif betting_strategy == "Kelly Criterion":
                    bet_amount = fraction * session_bankroll
                elif betting_strategy == "Martingale":
                    bet_amount = 25  # Base bet for Martingale
                elif betting_strategy == "D'Alembert":
                    bet_amount = 50  # Base bet for D'Alembert
                
                # Ensure we don't bet more than available
                bet_amount = min(bet_amount, session_bankroll)
                
                # Determine win/loss (consider house edge)
                if np.random.random() > (0.5 + house_edge/2):
                    # Win
                    if betting_strategy in ["Fixed Fraction", "Kelly Criterion"]:
                        session_bankroll += bet_amount
                    else:
                        session_bankroll += bet_amount  # Even money payout
                else:
                    # Loss
                    session_bankroll -= bet_amount
                
                # Check for bankruptcy
                if session_bankroll <= 0:
                    session_bankroll = 0
                    break
            
            bankroll = session_bankroll
            history.append(bankroll)
        
        # Store results
        st.session_state.bankroll_history = history
        st.session_state.simulation_results = {
            "final_bankroll": bankroll,
            "max_bankroll": max(history),
            "min_bankroll": min(history),
            "bankrupt": history[-1] <= 0
        }
    
    # Display simulation results
    if st.session_state.simulation_results:
        results = st.session_state.simulation_results
        
        st.subheader("Simulation Results")
        col_a, col_b, col_c = st.columns(3)
        col_a.metric("Final Bankroll", f"${results['final_bankroll']:.2f}")
        col_b.metric("Max Bankroll", f"${results['max_bankroll']:.2f}")
        col_c.metric("Min Bankroll", f"${results['min_bankroll']:.2f}")
        
        if results['bankrupt']:
            st.error("Bankroll reached $0 - Bankrupt!")
        else:
            roi = ((results['final_bankroll'] - initial_bankroll) / initial_bankroll) * 100
            st.success(f"Return on Investment: {roi:.1f}%")
        
        # Plot bankroll history
        fig, ax = plt.subplots()
        ax.plot(st.session_state.bankroll_history, 'b-', linewidth=2)
        ax.axhline(y=initial_bankroll, color='r', linestyle='--', label='Starting Bankroll')
        ax.set_title("Bankroll Over Time")
        ax.set_xlabel("Session Number")
        ax.set_ylabel("Bankroll ($)")
        ax.grid(True)
        ax.legend()
        
        st.pyplot(fig)
    else:
        st.info("Run the simulation to see bankroll projections")

# Additional strategy notes
st.divider()
st.header("Strategy Explanations")

expander = st.expander("Betting Strategy Details")
with expander:
    st.subheader("Fixed Fraction Betting")
    st.write("Bet a fixed percentage of your current bankroll on each wager. This strategy automatically adjusts bet sizes based on your bankroll fluctuations.")
    
    st.subheader("Kelly Criterion")
    st.write("Mathematically optimal strategy that maximizes bankroll growth based on your edge in a game. Requires accurate estimation of win probability and payout odds.")
    
    st.subheader("Martingale System")
    st.write("Progressive betting system where you double your bet after each loss. Resets to base bet after a win. High risk of ruin during losing streaks.")
    
    st.subheader("D'Alembert System")
    st.write("Moderate progression system where you increase bets by one unit after a loss and decrease by one unit after a win. Less aggressive than Martingale.")

# Footer
st.divider()
st.caption("Disclaimer: This app provides educational information only. Gambling involves risk. Please gamble responsibly.")