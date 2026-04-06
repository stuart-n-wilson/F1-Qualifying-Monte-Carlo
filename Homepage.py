# Packages and functions ---
import streamlit as st

st.sidebar.success('Please select a page above.')

# Title section ---
st.title('🏎️ F1 Qualifying Simulator')
st.markdown("Estimate the probability of every driver qualifying in every position.")
st.markdown("Simulate Formula 1 qualifying sessions using Monte Carlo methods.")
st.info("Go to the Qualifying simulator page (on the left) to get started.")

st.divider()

st.subheader("What this is")

st.markdown("""
This application simulates Formula 1 qualifying sessions using real session data.

- Each simulation runs Q1, Q2 and Q3, with eliminations at each stage.
- Supports every Grand Prix from 2018 to present.
- Automatically generates visualisations with team colours.
""")


st.divider()

st.subheader("How it works")

st.markdown("""
- Lap times are predicted using historical data and Monte Carlo simulation.
- Qualifying sets the order for the race. Three sessions take place in qualifying:
  - **Q1** – The slowest 5 (or 6 in 2026) drivers are eliminated. Their finishing position here becomes their starting position for the race. The remaining drivers progress to Q2.
  - **Q2** – Same format as Q1. The fastest 10 drivers make it into Q3, while eliminated drivers have their positions set.
  - **Q3** – The final shootout that determines the top 10 starting order. The fastest driver starts on pole.
""")

st.divider()

st.subheader("How to use")

st.markdown("- Head to the simulator page and click **Run**.")
st.markdown("- Results are displayed in tabs below.")

st.divider()

st.subheader("What you can explore")

st.markdown("- The numerical probabilities of any driver qualifying in any position.")
st.markdown("- How each driver qualifies over thousands of simulations.")
st.markdown("- Explore each grid position and which drivers are the most likely to occupy it.")

st.divider()

st.subheader("Assumptions and limitations")

st.markdown("- Lap times are normally distributed.")
st.markdown("- Limited to 2018 onwards as previous data is unavailable.")
st.markdown("- Drivers who progressed into a session in a simulation that they did not reach in real life are given an averaged improved lap from the previous session.")

st.divider()

st.subheader("About")

st.markdown("- Built using Python, FastF1, Plotly and Streamlit.")
st.markdown("- Entirely my own work as a Data Science project.")
st.markdown("- Feel free to get in touch here (I am actively looking for Junior Data Science roles...): https://www.linkedin.com/in/stuart-n-wilson/")


st.divider()

st.markdown("Thanks for checking this out, hope you enjoy! \n**-Stuart**")
