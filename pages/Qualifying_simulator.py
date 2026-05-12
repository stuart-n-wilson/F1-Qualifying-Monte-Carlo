# Packages and functions ---
import streamlit as st
import fastf1 as f1
import pandas as pd
import os
from datetime import datetime as dt
from simulation.simulator import run_full_monte_carlo
from utils.plotting import position_probability_plot, expected_position, position_change_bump
from utils.analysis import compare_grid, get_probability_stats, merge_stats_comparison_grid, colour_grid_change
from llm.context import build_llm_context
from llm.formatter import build_system_prompt
from llm.api import get_chat_response

os.makedirs("fastf1_cache", exist_ok=True)
f1.Cache.enable_cache("fastf1_cache")


# Title section ---
st.title('F1 Qualifying Position Simulator')
st.text('Select a qualifying session and then run thousands of simulations to see where drivers qualify.')
st.warning(
    """This app fetches live F1 data from the FastF1 API, which is currently very unstable. If you are presented with
    an error message, try selecting a different Grand Prix session. Apologies, I am currently working on mitigating this issue.""",
    icon="⚠️"
)

st.divider()

st.subheader("Choose a Qualifying session")

# User inputs to choose session ---
year = st.slider("Year", min_value=2018, max_value=dt.now().year, value=dt.now().year)
gp = st.selectbox("Grand Prix", f1.get_event_schedule(year, include_testing=False).loc[lambda df: df["EventDate"] <= pd.Timestamp.today(), "EventName"].to_list())


# Load session and cache ---
@st.cache_resource(show_spinner="Downloading the data...")
def load_session(year, gp):
    session = f1.get_session(year, gp, 'Q')
    session.load(laps=True, telemetry=False, weather=False, messages=False)
    return session

session = load_session(year, gp)

# Additional user inputs ---
n = st.number_input("Monte Carlo simulations", min_value=1, max_value=5000, value=1500)

st.divider()

st.subheader("Run the simulation")

# Run simulation ---
if st.button("Run"):
    with st.spinner("Running the simulation..."):

        df, simulated_grid = run_full_monte_carlo(session, n)
        comparison_grid = compare_grid(simulated_grid, session)
        stats = get_probability_stats(df, year)
        stats_dict = build_llm_context(df, simulated_grid, session, year)

        st.session_state.update({
            "df": df,
            "n": n,
            "run_year": year,
            "run_gp": gp,
            "simulated_grid": simulated_grid,
            "comparison_grid": comparison_grid,
            "stats": stats,
            "stats_dict": stats_dict,
            "chat_history": []
        })


if (
    "df" in st.session_state
    and st.session_state.get("run_year") == year
    and st.session_state.get("run_gp") == gp
    ):

    st.divider()
    st.subheader("Simulation Results")

    # Call variables from session state, usuable across all tabs.
    df = st.session_state.df
    comparison_grid = st.session_state.comparison_grid
    stats = st.session_state.stats
    n = st.session_state.n

    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Simulated results", "Position Analysis","Driver Analysis", "AI analysis", "Data"])

    # Simulated results
    with tab1:
        # Use df.copy() so changes not saved to df.
        st.dataframe(colour_grid_change(comparison_grid.copy()))
        st.info("A real position may be 'None' if the driver did not qualify.", icon="ℹ️")

        fig = position_change_bump(comparison_grid, session, n)
        st.plotly_chart(fig, width='stretch')

    # Position probability distribution plot
    with tab2:
        pos = st.slider("Qualifying position", min_value=1, max_value=len(session.results), value=1)

        # Protect against missing driver for position.
        match = session.results.loc[session.results['Position'].astype('Int64') == pos, 'FullName'].values
        if len(match) == 0:
            st.markdown(f"Real P{pos} qualifier: No driver qualified in this position")
        else:
            st.markdown(f"Real P{pos} qualifier: {match[0]}")
        
        sim_match = comparison_grid.loc[comparison_grid['Simulated position'] == pos, 'Driver Name'].values
        if len(sim_match) > 0:
            st.markdown(f"Simulated P{pos} qualifier: {sim_match[0]}")

        fig = position_probability_plot(st.session_state.df, session, st.session_state.n, pos)
        st.plotly_chart(fig, width='stretch')
    
    # Driver probability distribution plot
    with tab3:
        driver = st.selectbox("Driver", sorted(session.get_driver(d)['FullName'] for d in session.drivers))
        abbr = session.results.loc[session.results["FullName"] == driver, "Abbreviation"].values[0]
        position = session.results.loc[session.results['FullName'] == driver, 'Position'].values[0]

        if pd.isna(position):
            st.markdown("Real qualifying position: did not qualify.")
        else:
            st.markdown(f"Real qualifying position: P{int(position)}.")
        
        sim_position = comparison_grid.loc[abbr, 'Simulated position']
        st.markdown(f"Simulated qualifying position: P{int(sim_position)}.")

        fig = expected_position(st.session_state.df, session, driver, abbr, st.session_state.n)
        st.plotly_chart(fig, width='stretch')

    # AI analysis
    with tab4:
        st.markdown("Ask AI about anything related to this app (please be conscious that this is using a free tier of Google AI studio," \
        "so token limits may restrict usage.)")

        # Default prompt buttons — only show before conversation starts
        if not st.session_state.chat_history:
            st.markdown("**Try asking:**")
            col1, col2, col3 = st.columns(3)

            default_prompts = [
                "What is Formula 1 qualifying?",
                "Explain in a non-technical way how this app works.",
                "Who was most likely to take pole position, and how confident is the simulation in that?"
            ]

            for col, prompt in zip([col1, col2, col3], default_prompts):
                with col:
                    if st.button(prompt, use_container_width=True):
                        st.session_state.chat_history.append({"role": "user", "content": prompt})
                        with st.spinner("Thinking..."):
                            response = get_chat_response(
                                st.session_state.chat_history,
                                build_system_prompt(st.session_state.stats_dict, session)
                            )
                        st.session_state.chat_history.append({"role": "assistant", "content": response})
                        st.rerun()

        # Initialise chat history if not present
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []

        # Render existing messages
        for message in st.session_state.chat_history:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # Handle new input
        user_input = st.chat_input("Ask about the qualifying session...")

        if user_input:
            st.session_state.chat_history.append({"role": "user", "content": user_input})

            with st.spinner("Thinking..."):
                response = get_chat_response(
                    st.session_state.chat_history,
                    build_system_prompt(st.session_state.stats_dict, session)
                )

            st.session_state.chat_history.append({"role": "assistant", "content": response})
            st.rerun()

    # Data
    with tab5:
        # Rename column headers to P1, P2 etc.
        st.markdown("This table shows the probability (0 - 1) of a driver qualifying in each position.")
        st.dataframe(st.session_state.df.rename(columns=lambda x: f"P{x}"))

        st.markdown("This table contains statistics based on the position probabilities table, and simulated results.")
        st.dataframe(merge_stats_comparison_grid(stats, comparison_grid))

# Display message if session changes that simulation must be rerun.
elif "df" in st.session_state:
    st.info("Session changed — click Run to generate results for the selected qualifying session.", icon="ℹ️")

st.divider()

st.markdown("Created by **Stuart Wilson** · [LinkedIn](https://www.linkedin.com/in/stuart-n-wilson/) · [GitHub](https://github.com/stuart-n-wilson)")
