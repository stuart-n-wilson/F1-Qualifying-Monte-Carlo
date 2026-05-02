# Packages and functions ---
import streamlit as st
import fastf1 as f1
import pandas as pd
from datetime import datetime as dt
from simulator import monte_carlo_qualifying, simulate_grid
from plotting import position_probability_plot, expected_position, create_heatmap
from analysis import compare_grid

f1.set_log_level('ERROR')


# Title section ---
st.title('F1 Qualifying Position Simulator')
st.text('Select a qualifying session and then run thousands of simulations to see where drivers qualify.')

st.divider()

st.subheader("Choose a Qualifying session")

# User inputs to choose session ---
year = st.slider("Year", min_value=2018, max_value=dt.now().year, value=2026)
gp = st.selectbox("Grand Prix", f1.get_event_schedule(year, include_testing=False).loc[lambda df: df["EventDate"] <= pd.Timestamp.today(), "EventName"].to_list())



import os

@st.cache_resource(show_spinner="Downloading the data...")
def load_session(year, gp):
    f1.set_log_level('ERROR')
    cache_dir = "/tmp/fastf1_cache"
    os.makedirs(cache_dir, exist_ok=True)
    f1.Cache.enable_cache(cache_dir)
    session = f1.get_session(year, gp, 'Q')
    session.load()
    return session


# Load session and cache ---
#@st.cache_resource(show_spinner="Downloading the data...")
#def load_session(year, gp):
 #   f1.set_log_level('ERROR')
  #  session = f1.get_session(year, gp, 'Q')
   # session.load()
    #return session

session = load_session(year, gp)

# Additional user inputs ---
n = st.number_input("Monte Carlo simulations", min_value=1, max_value=5000, value=500)

st.divider()

st.subheader("Run the simulation")

# Run simulation ---
if st.button("Run"):
    with st.spinner("Running the simulation..."):
        st.session_state.df = monte_carlo_qualifying(session, n)
        st.session_state.n = n
        st.session_state.run_year = year
        st.session_state.run_gp = gp

st.divider()

if (
    "df" in st.session_state
    and st.session_state.get("run_year") == year
    and st.session_state.get("run_gp") == gp
    ):

    st.subheader("Simulation Results")

    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Simulated results", "Position Analysis","Driver Analysis", "Probabilities dataframe", "Probabilties heatmap"])

    # Simulated results
    with tab1:
        st.dataframe(compare_grid(simulate_grid(st.session_state.df), session))
        st.info("A real position may be None if the driver did not qualify.", icon="ℹ️")

    # Position probability distribution plot
    with tab2:
        pos = st.slider("Qualifying position", min_value=1, max_value=len(session.results), value=1)

        # Protect against missing driver for position.
        match = session.results.loc[session.results['Position'].astype('Int64') == pos, 'FullName'].values
        if len(match) == 0:
            st.markdown(f"Real P{pos} qualifier: No driver qualified in this position")
        else:
            st.markdown(f"Real P{pos} qualifier: {match[0]}")

        fig = position_probability_plot(st.session_state.df, session, pos, st.session_state.n)
        st.plotly_chart(fig, use_container_width=True)
    
    # Driver probability distribution plot
    with tab3:
        driver = st.selectbox("Driver", sorted(session.get_driver(d)['FullName'] for d in session.drivers))
        abbr = session.results.loc[session.results["FullName"] == driver, "Abbreviation"].values[0]
        position = session.results.loc[session.results['FullName'] == driver, 'Position'].values[0]

        if pd.isna(position):
            st.markdown("Real qualifying position: did not qualify.")
        else:
            st.markdown(f"Real qualifying position: P{int(position)}.")

        fig = expected_position(st.session_state.df, session, driver, abbr, st.session_state.n)
        st.plotly_chart(fig, use_container_width=True)

    # Dataframe of probabilities
    with tab4:
        # Rename column headers to P1, P2 etc.
        st.dataframe(st.session_state.df.rename(columns=lambda x: f"P{x}"))
        st.info("This table shows the probability (0 - 1) of a driver qualifying in each position.", icon="ℹ️")

    # Probabilities heatmap
    with tab5:
        fig = create_heatmap(st.session_state.df, session)
        st.plotly_chart(fig, use_container_width=True)
        st.info("This is the Probabilties dataframe as a heatmap.", icon="ℹ️")


# Display message if session changes that simulation must be rerun.
elif "df" in st.session_state:
    st.info("Session changed — click Run to generate results for the selected qualifying session.", icon="ℹ️")