import streamlit as st

st.title("Technical notes")
st.markdown("A deep dive into the methodology, maths, and implementation behind the simulator.")

st.divider()

# Monte Carlo ---
st.subheader("Monte Carlo simulation")
st.markdown("""
The core idea is to replace a deterministic (fixed) prediction with a probabilistic (random) one.
For each simulation, every driver is given a lap time that is drawn from a normal distribution derived from their
real session data. By repeating this process, position counts for each driver are aggregated into a probability
matrix.
            
For driver $i$ in session $s$, a simulated lap time $t$ is sampled as:

$$ t_{i,s} \\sim \\mathcal{N}(\\mu_{i,s}, \\, \\sigma_{i,s}^2) $$

where the mean $\\mu_{i,s}$ and variance $\\sigma_{i,s}^2$ are estimated from the driver's quick laps in that
subsession (Q1, Q2, Q3). Each subsession samples `n_attempts` from the distribution, which is the average number
of laps in that subsession, and takes the minimum (the fastest) - this is reflective of real sessions.
""")

st.divider()

# Stats assumptions ---
st.subheader("Stastical assumptions")

st.markdown("""
**Lap times are normally distributed.** This is a simplifying assumption and is supported by the fact that only
quick laps are used in the approximation.
            
**Expected position and position variance** are derived from the probability matrix produced by the repeated
simulations. For a driver $$i$$, with probabililty $$p_{i,k}$$ of finishing in position $$k$$:
            
$$ \\mathbb{E}(X_i) = \\sum_k k \\cdot p_{i,k} $$.

That is, the expected position for each driver is the weighted sum of the position probabilities. This is
efficiently calculated using matrix multiplication as `probs @ position`. Also from this, the variance is
calculated as
            
$$ \\text{Var}(X_i) = \\mathbb{E}[X_i^2] - (\\mathbb{E}[X_i])^2$$.
""")

st.divider()

# Hungarian algorithm ---
st.subheader("Grid assigment: the Hungarian algorithm")

st.markdown("""
The probability matrix gives probability distribtuions over positions and drivers, but it is insufficient in
setting a final order: drivers can be the most likely for more than one position, and positions can have drivers
with equal probability.
            
The final order must a one-to-one matching of drivers with positions, and at that, the most probable one. This
leads to the problem being framed as linear sum assingment that maximises total likelihood; this is solved by
the Hungarian algorithm (via `scipy.optimize.linear_sum_assignment`).
            
The Hungarian algorithm minimses cost, so the the probability matrix is converted into a cost matrix by taking
the negative log of each entry, giving the negative log probability. This is necessary in minimising the cost,
since by the properties of logs, $$\\text{log}(p_{i,k} \\cdot p_{i, k+1}) = \\text{log}(p_{i,k}) + \\text{log}(p_{i,k+1})$$. 
Hence the goal is to minimise the cost sum, which is what the Hungarian algorithm does.

The result is that final order is one that maximises the total probability and meets the matching criteria.
""")
st.divider()

# Data pipeline ---
st.subheader("Data pipeline")

st.markdown("""
Data is downloaded from the [FastF1](https://docs.fastf1.dev/) library, which provides official F1 data from 2018
onwards. To reduce load time, only lap timing data is loaded (telemtry, weather and messages are disabled).
        
From each subsession, laps are filtered to quick laps (using `.pick_quicklaps()`), which removes non-competitive
laps (e.g. in/out laps, incomplete laps, cool-down laps) before fitting the distributions to each driver.
        
Using `.split_qualifying_sessions()`, statistics are calculated for each subsession individually.
Additionally, sessions are cached using `fastf1.cache` and `st.cache_data` to reduce downloads to only once per
session.
""")

st.divider()

# Limitations ---
st.subheader("Limitations and edge cases")
st.markdown("""
**Drivers who did not set any laps** in a session (due to crashes, red flags etc) are giving an $\\mu = \\infty$ and
a standard deviation of the session's median. This is to force them to the back of the session in terms of order.
            
**Drivers with missing Q2 or Q3 data** happens when in real life the driver did not progress into that session, but
did in the simulation. To handle this, a mean session-to-session improvement is estimated from the drivers with
complete data, and applied to their mean lap time from the previous session; this prevents drivers from being automically
the slowest in this session.
            
**Zero probabilities** are replaced by $10^{-6}$ before calculating log probabililties, since $\\log(0)$ is undefined.

**2026 grid size change** - from 2026 (onwards), the grid has increase from 20 drivers to 22, with 6 drivers eliminated
at the end of Q1 and Q2, rather than 5; all calculations account for this.

**External factors** such as weather, tyre compounds/degredation are not considered.
""")

st.divider()

# LLM
st.subheader("LLM integration")
st.markdown("""
The simulator includes an AI chat interface that allows users to ask questions about the simulation results. 
The model used is **Gemini 2.5 Flash Lite**, accessed via Google AI studio.
            
**Context**

Rather than directly passing the probability matrix into the model, which would highly likely cause
numerical errors and incorrect interpretations, the context is constructed from a natural language      
summary for each driver that contains driver info and statistics dervied from the probability matrix.

**Hallucination prevention**

An application such as this, with specific data generating insights, is very perceptible to
hallucination. The model is explicity instructed to only used data provided in the prompt - this
prompt contains detailed instructions alongside the formatted driver summaries. This does reduce
the model's flexibility, but is necessary for ensuring responses that are grounded in the data.
The prompt is rebuilt on every API call to prevent data leakage from one simulation to the next.
""")

st.divider()

st.markdown("Created by **Stuart Wilson** · [LinkedIn](https://www.linkedin.com/in/stuart-n-wilson/) · [GitHub](https://github.com/stuart-n-wilson)")


