# Packages and functions ---
import streamlit as st
import fastf1 as f1
import pandas as pd
from datetime import datetime as dt
from simulator import monte_carlo_qualifying
from plotting import position_probability_plot, expected_position

f1.set_log_level('ERROR')


# Title section ---
st.title('F1 Qualifying Simulator')
st.text('This app uses Monte Carlo simulation to simulate Formula 1 Qualifying sessions.')


# User inputs to choose session ---
year = st.slider("Year", min_value=2018, max_value=dt.now().year, value=2025)
gp = st.selectbox("Event", f1.get_event_schedule(year, include_testing=False).loc[lambda df: df["EventDate"] <= pd.Timestamp.today(), "EventName"].to_list())


# Load session ---
session = f1.get_session(year, gp, 'Q')
session.load()

# Additional user inputs
pos = st.slider("Position", min_value=1, max_value=len(session.results), value=1)
driver = st.selectbox("Driver", sorted(session.get_driver(d)['FullName'] for d in session.drivers))
abbr = session.results.loc[
    session.results["FullName"] == driver,
    "Abbreviation"].values[0]
n = st.number_input("Number of simulations", min_value=1, max_value=5000, value=500)


run = st.button("Run Simulation")

if run:
    st.write("Running simulation...")

    df = monte_carlo_qualifying(session, n)

    st.dataframe(df)

    fig = position_probability_plot(df, session, pos, n)

    st.pyplot(fig, use_container_width=True)

    fig = expected_position(df, session, driver, abbr, n)

    st.pyplot(fig, use_container_width=True)