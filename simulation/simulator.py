import pandas as pd
import numpy as np
from scipy.optimize import linear_sum_assignment
from collections import defaultdict

# Internal helper functions ---

def _create_driver_session_stats(laps, results):
    """ Helper function to create stats for Q1, Q2 and Q3.

    Takes session object as input and then simulates each qualifying subsession with driver eliminates at each stage.
    Drivers who, in real life, did not progress to the next stage are given simulated improvement from real data.

    Args:
        session: FastF1 session object.

    Returns:
        q1_stats, q2_stats, q3_stats:
        Stats for each driver for each subsession as pd df.
        Indexed by abbreviation e.g. HAM.
        Column headers are mean, std, count.
    """
    q1, q2, q3 = laps.split_qualifying_sessions()

    all_drivers = pd.Index(
        results["Abbreviation"].dropna().unique(),
        name="Driver"
    )

    # Helper function
    def extract_stats(laps_df):
        laps = laps_df.pick_quicklaps().loc[lambda df: ~df["Deleted"].fillna(False)].copy()
        laps['LapTimeSeconds'] = laps["LapTime"].dt.total_seconds()
        return laps.groupby("Driver")["LapTimeSeconds"].agg(["mean", "std", "count"])

    # Q1 stats ---
    q1_stats_raw = extract_stats(q1)
    q1_stats = q1_stats_raw.copy()

    q1_backup_std = q1_stats["std"].median()
    q1_stats["std"] = q1_stats["std"].fillna(q1_backup_std)

    # Ensure all drivers are in the stats, even if they did not take part.
    q1_stats = q1_stats.reindex(all_drivers)

    # Drivers without competitive Q1 laps fill with placeholder values (infinite lap time).
    q1_stats["mean"] = q1_stats["mean"].fillna(np.inf)
    q1_stats["std"] = q1_stats["std"].fillna(0.5)
    q1_stats["count"] = q1_stats["count"].fillna(1).astype(int)


    # Q2 stats ---
    q2_stats_raw = extract_stats(q2)
    common_drivers_q1_q2 = q1_stats_raw.index.intersection(q2_stats_raw.index)

    # Calculate avg improvement from Q1 to Q2 from drivers who were in both
    q1_to_q2_avg_improvement = (q1_stats_raw.loc[common_drivers_q1_q2, 'mean'] - q2_stats_raw.loc[common_drivers_q1_q2, 'mean']).mean()

    q2_stats = q2_stats_raw.reindex(all_drivers)
    q2_stats["mean"] = q2_stats["mean"].fillna(q1_stats["mean"] - q1_to_q2_avg_improvement)

    q2_backup_std = q2_stats_raw["std"].median()
    q2_stats["std"] = q2_stats["std"].fillna(q2_backup_std)
    q2_stats["count"] = q2_stats["count"].fillna(int(q2_stats_raw["count"].mean()))


    # Q3 stats ---
    q3_stats_raw = extract_stats(q3)
    common_drivers_q2_q3 = q2_stats_raw.index.intersection(q3_stats_raw.index)

    q2_to_q3_avg_improvement = (q2_stats_raw.loc[common_drivers_q2_q3, "mean"] - q3_stats_raw.loc[common_drivers_q2_q3, "mean"]).mean()

    q3_stats = q3_stats_raw.reindex(all_drivers)
    q3_stats["mean"] = q3_stats["mean"].fillna(q2_stats["mean"] - q2_to_q3_avg_improvement)

    q3_backup_std = q3_stats_raw["std"].median()
    q3_stats["std"] = q3_stats["std"].fillna(q3_backup_std)
    q3_stats["count"] = q3_stats["count"].fillna(int(q3_stats_raw["count"].mean()))    

    return q1_stats, q2_stats, q3_stats

def _simulate_session(q_stats):
    """ Helper function to simulate a single session based on stats.

    Generates a single lap time for each driver based on a normal distribution
    using the provided mean and standard deviation.

    Args:
        q_stats: DataFrame containing 'mean', 'std', and 'count' for drivers.

    Returns:
        list: Ordered list of driver abbreviations from fastest to slowest.
    """
    # Calculate average number of laps for that session
    n_attempts = int(q_stats['count'].mean())
    results = {}

    for driver in q_stats.index:
        mean, std = q_stats.loc[driver, 'mean'], q_stats.loc[driver, 'std']

        # Ensure drivers with inf lap time are last.
        if np.isinf(mean):
            results[driver] = np.inf  
            continue

        # Random normal distribution
        lap_times = np.random.normal(mean, std, n_attempts)
        results[driver] = lap_times.min()

    return sorted(results, key=results.get)

def _simulate_qualifying(q1_stats, q2_stats, q3_stats, year):
    """ Simulates each stage of qualifying (Q1, Q2, Q3) with eliminations.

    Accounts for different elimination cutoffs depending on the season 
    regulations (e.g., 22 drivers in 2026+).

    Args:
        q1_stats, q2_stats, q3_stats: DataFrames from _create_driver_session_stats.
        year: Integer representing the championship year.

    Returns:
        list: Full qualifying results as an ordered list of driver abbreviations (P1 to P20/22).
    """
    # Q1 Sim
    q1_result = _simulate_session(q1_stats)
    
    cutoff = 16 if year >= 2026 else 15
    q2_drivers, q1_eliminated = q1_result[:cutoff], q1_result[cutoff:]

    # Q2 Sim
    q2_result = _simulate_session(q2_stats.loc[q2_drivers])
    q3_drivers, q2_eliminated = q2_result[:10], q2_result[10:]

    # Q3 Sim
    q3_result = _simulate_session(q3_stats.loc[q3_drivers])

    return q3_result + q2_eliminated + q1_eliminated

def _count_positions(q1_stats, q2_stats, q3_stats, year, n):
    """ Runs multiple simulations and tallies the finishing positions for each driver.

    Args:
        q1_stats, q2_stats, q3_stats: DataFrames from _create_driver_session_stats.
        year: Integer representing the championship year.
        n: Number of Monte Carlo simulations to run.

    Returns:
        defaultdict: A nested dictionary where keys are driver abbreviations and 
                     values are dictionaries of {position: count}.
    """
    # Automatically create position with count 0 if not seen before, with fresh dictionary for each driver.
    position_counts = defaultdict(lambda: defaultdict(int))

    for i in range(n):
        result = _simulate_qualifying(q1_stats, q2_stats, q3_stats, year)
        # Add count for that position for driver, adjust for 0 indexing.
        for position, driver in enumerate(result):
            position_counts[driver][position + 1] +=1

    return position_counts

def _get_position_probability(position_counts, n):
    """ Converts raw position counts into percentage-based probabilities.

    Args:
        position_counts: Nested dictionary from _count_positions.
        n: Number of simulations used for the calculation.

    Returns:
        dict: A nested dictionary where keys are driver abbreviations and 
              values are dictionaries of {position: probability}.
    """
    position_probabilities = {}

    for driver, positions in position_counts.items():
        position_probabilities[driver] = {
            position: count / n
            for position, count in positions.items()
        }

    return position_probabilities

def _monte_carlo_qualifying(laps, results, year, n):
    """ Orchestrates the full Monte Carlo simulation process.

    Extracts session data, runs the simulation loop, and calculates probabilities.

    Args:
        session: FastF1 session object.
        n: Number of simulations to perform.

    Returns:
        pd.DataFrame: A matrix where rows are drivers and columns are positions (1-20/22),
                      containing the probability of that driver finishing in that position.
    """
    # Extract data
    q1, q2, q3 = _create_driver_session_stats(laps, results)
    position_counts = _count_positions(q1, q2, q3, year, n)

    # Run the loop
    position_counts = _count_positions(q1, q2, q3, year, n)

    # Calculate probabilities
    position_probabilities = _get_position_probability(position_counts, n)

    df = pd.DataFrame.from_dict(position_probabilities, orient="index")
    df = df.fillna(0)
    df.index.name = 'Driver'
    df.columns.name = 'Position'
    df = df.reindex(sorted(df.columns), axis=1)

    return df

def _simulate_grid(df):
    """ Determines the most likely unique grid order using the Hungarian algorithm.

    Converts probabilities into a cost matrix and minimizes the cost to ensure 
    every driver is assigned a unique, optimal position.

    Args:
        df: Probability DataFrame output from _monte_carlo_qualifying.

    Returns:
        pd.DataFrame: A DataFrame indexed by Driver abbreviation with a single 
                      column 'SimPosition'.
    """
    # Replace 0 with 1e-6
    df_no_zero = df.replace(0, 1e-6)

    # Log transform probabilities and make negative to convert into a cost matrix.
    cost = -np.log(df_no_zero)

    # Algorithm to find least cost matching of drivers to positions.
    row_ind, col_ind = linear_sum_assignment(cost)

    # Extract driver abbreviation / position pairs from df.
    grid = pd.DataFrame({
        "Driver": df.index[row_ind],
        "SimPosition":  df.columns[col_ind]
        })
    
    return grid.set_index('Driver').sort_values('SimPosition', ascending=True)

# Public functions ---

def run_full_monte_carlo(laps, results, year, n):
    """ The primary public entry point for the simulation engine.

    Wraps the Monte Carlo probability generation and the final grid assignment 
    into a single call for the UI.

    Args:
        session: FastF1 session object.
        n: Number of simulations to perform.

    Returns:
        tuple: (prob_df, sim_grid)
               - prob_df: Full probability matrix.
               - sim_grid: The final predicted grid positions.
    """
    prob_df = _monte_carlo_qualifying(laps, results, year, n)
    sim_grid = _simulate_grid(prob_df)

    return prob_df, sim_grid