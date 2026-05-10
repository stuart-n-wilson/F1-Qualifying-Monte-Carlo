# 🏎️ F1 Qualifying Simulator

![Python](https://img.shields.io/badge/Python-blue) [![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://f1-qualifying-monte-carlo-simulator.streamlit.app/)

A Monte Carlo simulation of Formula 1 qualifying sessions, built as a Data Science portfolio project. Try it out [**here**](https://f1-qualifying-monte-carlo-simulator.streamlit.app/).

---

## 🚀 Overview

Monte Carlo simulation is a technique that uses the randomness of real data, and repeats events accounting for this randomness. This app uses the randomness of the real lap times and simulates full qualifying sessions to find the probabilities of each driver qualifying in each position, and then works out a most probable finishing order.

Select any Grand Prix qualifying session from 2018 to present, choose the number of simulations to run, and the app will:

- Simulate Q1, Q2 and Q3 with eliminations at each stage using real session lap time data
- Produce a probability matrix showing the likelihood of each driver qualifying in each position
- Derive the most probable full grid using the Hungarian algorithm
- Compare the simulated grid against the real qualifying result
- Provide an AI chat interface to explore and interpret the results

---

## ⚙️ How it works

### Data
Session data is loaded via the [FastF1](https://docs.fastf1.dev/) library, which provides official F1 timing data from 2018 onwards. Laps are filtered to quicklaps only, removing non-competitive laps before fitting distributions to each driver.

### Monte Carlo simulation
For each driver in each session (Q1, Q2, Q3), a normal distribution is fitted to their real lap times. A simulated lap time is drawn from this distribution, repeated for the average number of lap attempts in that session, and the fastest is taken — matching real qualifying behaviour. The full three-stage session is simulated `n` times (user-defined, up to 5,000), and position frequencies are converted into probabilities.

Drivers who did not reach a session in real life but do in the simulation are given an estimated lap time derived from the average session-to-session improvement observed from drivers with complete data.

### Grid assignment: the Hungarian algorithm
The probability matrix alone is insufficient to produce a unique grid — multiple drivers may have their highest probability at the same position. The Hungarian algorithm (`scipy.optimize.linear_sum_assignment`) solves this as a linear sum assignment problem, finding the one-to-one matching of drivers to positions that maximises the total joint probability across the whole grid.

### AI analysis
An LLM chat interface is built into the simulator, grounded in the session-specific simulation data. The model can explain results, compare drivers, and answer questions about the simulation — but is constrained to only make claims supported by the data it has been given.

---

## 📂 Project structure

```
F1-Qualifying-Monte-Carlo-Simulator/
├── pages/
│   ├── Qualifying_simulator.py   # Main simulator page
│   ├── Technical_notes.py        # Methodology and maths
├── simulation/
│   ├── simulator.py              # Monte Carlo simulation engine
├── utils/
│   ├── analysis.py               # Statistical analysis functions
│   ├── plotting.py               # Visualisation functions
├── llm/
│   ├── api.py                    # LLM API call
│   ├── context.py                # Simulation context builder
│   ├── formatter.py              # System prompt and driver formatting
├── Homepage.py                   # Application homepage
├── requirements.txt              # Package dependencies
└── README.md
```

---

## 📝 Assumptions and limitations

- Lap times are assumed to be normally distributed.
- Data is only available from 2018 onwards.
- External factors such as weather, tyre compounds and track evolution are not modelled.
- Assumes independence between laps and between drivers.

---

## 🛠️ Stack

Python · FastF1 · NumPy · SciPy · Pandas · Plotly · Streamlit · Gemini API

---

## ▶️ Running locally

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Add a `.streamlit/secrets.toml` file with your Gemini API key:
   ```toml
   GEMINI_API_KEY = "your-key-here"
   ```
4. Run the app:
   ```bash
   streamlit run Homepage.py
   ```
