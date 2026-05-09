import streamlit as st

st.sidebar.success('Please select a page above.')

# Title section ---
st.title('🏎️ F1 Qualifying Simulator')
st.markdown("A Monte Carlo simulation of Formula 1 qualifying sessions.")
st.info("Head over to the Qualifying simulator page (on the left) to get started.", icon="ℹ️")


st.divider()

st.subheader("The problem and the solution")
st.markdown("""
Formula 1 qualifying sessions determine the starting order of the race, and are meant to demonstrate the true speed of the teams and drivers.
But a single session cannot reasonably make these comparisons, and inference from singles values can be misleading. So what's the solution?
            
- Can we obtain a more accurate estimate of team/driver pace?
- How do we see what could have been?
- If we repeated the session thousands of times, what is the most likely qualifying order?
- Can we identify when drivers performed exceptionally well, or poorly?

Monte Carlo simulation is a technique that uses the randomness of real data, and repeats events accounting for this randomness.
This app uses the randomness of the real lap times and simulates full qualifying sessions to find the probabilities of each driver
qualifying in each position, and then works out a most probable finishing order.
            
While being applied here to a Formula 1 context, this method is applicable to any situation where decisions are based on
historical data that contains uncertainty.
""")

st.divider()

st.subheader("What it does")
st.markdown("""
Select any Grand Prix qualifying session from 2018 to present, choose the number of simulations to run, and the app will:
- Simulate Q1, Q2 and Q3 with eliminations at each stage using real session lap time data
- Produce a probability matrix showing the likelihood of each driver qualifying in each position
- Derive the most probable full grid using the Hungarian algorithm
- Compare the simulated grid against the real qualifying result
- Create visualisations to analyse each driver or position
""")

st.divider()

st.subheader("How to use it")
st.markdown("""
1. Go to the **Qualifying Simulator** page in the sidebar
2. Select a year and Grand Prix
3. Set the number of simulations (higher = more accurate, slower to run)
4. Click **Run**
""")
st.info("Head to **Technical Notes** in the sidebar to read about the methodology, maths and implementation.", icon="ℹ️")

st.divider()

st.markdown("Created by **Stuart Wilson** · [LinkedIn](https://www.linkedin.com/in/stuart-n-wilson/) · [GitHub](https://github.com/stuart-n-wilson) · Actively looking for Junior Data Science roles")