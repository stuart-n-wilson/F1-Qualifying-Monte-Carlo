# 🏎️ F1 Qualifying Simulator Application

![Python](https://img.shields.io/badge/Python-blue) [![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://f1-qualifying-monte-carlo-simulator.streamlit.app/)

An app that uses Monte Carlo Simulation to simulate F1 Qualifying sessions. Try it out [**here**](https://f1-qualifying-monte-carlo-simulator.streamlit.app/).

---

## 🚀 Overview

This application uses Monte Carlo simulation and real F1 data to model Formula 1 Qualifying sessions and estimate the probability of each driver qualifying in each position.

---

## 🎯 Motivation

This project was built to explore how Monte Carlo simulation (and a good chunk of domain knowledge) can be applied to real world Formula 1 data.

It demonstrates:
- probabilistic modelling
- multi-stage simulation
- building interactive data applications

---

## ⚙️ How it works

### Simulating qualifying
- With each session of qualifying (Q1, Q2, Q3), a normal distribution is modelled from the driver's real lap times.
- If a driver did not take part in a session, and infinite lap time is generated for them.
- The average number of lap attempts per session is calculated and used as the number of samples in the simulation.
- For Q1, the top 15 (or 16 in 2026, it automatically adjusts) drivers progress into Q2, with the eliminated drivers' positions fixed.
- Q2 lap times are generated in the same way as Q1.
- For drivers who did not make it into that session in real life but did in the simulation, an average time delta between sessions is calculated (only using the real times), and then applied to their previous session lap time.
- The fastest 10 drivers progress into Q3, with the eliminated drivers' positions fixed.
- Q3 sets the order for the remaining 10 drivers, the fastest driver takes pole position.
- As before, any missing real data has a simulated session-to-session delta.
- A final qualifying order of drivers is produced.

### The Monte Carlo method
- The full process of qualifying is simulated repeatedly (user-defined number of times).
- Each simulation produces a complete qualifying order.
- Frequencies of qualifying positions are converted into probabilities.

### The visualisations
- A heatmap of probabilities is generated from the probabilities dataframe.
- The user can choose a position, or driver to focus on, and then probability distributions are generated accordingly.
- Each plot automatically assigns team colours to drivers.

---

## 📂 Application Structure

```
F1-Qualifying-Monte-Carlo-Simulator/
├── pages/
│   ├── Qualifying_simulator.py   # Application simulator page
├── Homepage.py                   # Application homepage
├── plotting.py                   # Visualisation functions
├── requirements.txt              # Package requirements
├── simulator.py                  # Qualifying simulation functions
└── README.md
```

---

## 📝 Limitations/assumptions

- Lap times are normally distributed.
- Limited to 2018 onwards as previous data is unavailable.
- Assumes independence between laps.
- No external factors (weather, track evolution etc) are considered.

---

## ▶️ How to Run Locally

1. Clone the repository  
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
3. Execute app:
   ```bash
   streamlit run Homepage.py
