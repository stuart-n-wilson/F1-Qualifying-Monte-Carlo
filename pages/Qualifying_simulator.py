# Packages and functions ---
import streamlit as st
import fastf1 as f1
import pandas as pd
from datetime import datetime as dt
from simulator import monte_carlo_qualifying
from plotting import position_probability_plot, expected_position, create_heatmap

f1.set_log_level('ERROR')


# Title section ---
st.title('F1 Qualifying Position Simulator')
st.text('Select a qualifying session and then run thousands of simulations to see where drivers qualify.')

st.divider()

st.subheader("Choose a Qualifying session")

# User inputs to choose session ---
year = st.slider("Year", min_value=2018, max_value=dt.now().year, value=2025)
gp = st.selectbox("Grand Prix", f1.get_event_schedule(year, include_testing=False).loc[lambda df: df["EventDate"] <= pd.Timestamp.today(), "EventName"].to_list())


# Load session and cache ---
@st.cache_resource(show_spinner=False)
def load_session(year, gp):
    f1.set_log_level('ERROR')
    session = f1.get_session(year, gp, 'Q')
    session.load()
    return session

session = load_session(year, gp)

# Additional user inputs ---
n = st.number_input("Monte Carlo simulations", min_value=1, max_value=5000, value=500)

st.divider()

st.subheader("Run the simulation")

# Run simulation ---
if st.button("Run"):
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

    tab1, tab2, tab3, tab4 = st.tabs(["Dataframe", "Heatmap", "Position Analysis","Driver Analysis"])

    # Dataframe
    with tab1:
        st.dataframe(st.session_state.df)

    # Heatmap
    with tab2:
        fig = create_heatmap(st.session_state.df, session)
        st.plotly_chart(fig, use_container_width=True)
    
    # Position
    with tab3:
        pos = st.slider("Qualifying position", min_value=1, max_value=len(session.results), value=1)
        fig = position_probability_plot(st.session_state.df, session, pos, st.session_state.n)
        st.plotly_chart(fig, use_container_width=True)
    
    # Driver
    with tab4:
        driver = st.selectbox("Driver", sorted(session.get_driver(d)['FullName'] for d in session.drivers))
        abbr = session.results.loc[
            session.results["FullName"] == driver,
            "Abbreviation"].values[0]
        fig = expected_position(st.session_state.df, session, driver, abbr, st.session_state.n)
        st.plotly_chart(fig, use_container_width=True)

elif "df" in st.session_state:
    st.info("Session changed — click Run to generate results for the selected qualifying session.")
