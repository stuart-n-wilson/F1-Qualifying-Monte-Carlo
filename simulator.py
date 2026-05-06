import pandas as pd
import numpy as np
from scipy.optimize import linear_sum_assignment

def create_driver_session_stats(session):
    '''
    Input: session.

    Filters to competitive laps.
    Drivers who did not set a lap in that session are given default stats.
    
    Output: driver stats for q1, q2 and q3.
    '''

    q1, q2, q3 = session.laps.split_qualifying_sessions()

    # List of all drivers in qualifying session.
    all_drivers = pd.Index(
        session.results["Abbreviation"].dropna().unique(),
        name="Driver"
    )

    # Q1 stats ---

    q1_laps = q1.pick_quicklaps().loc[lambda df: ~df["Deleted"]].copy()
    q1_laps["LapTimeSeconds"] = q1_laps["LapTime"].dt.total_seconds()

    q1_stats = q1_laps.groupby("Driver")["LapTimeSeconds"].agg(["mean", "std", "count"])
    q1_stats_raw = q1_stats.copy()

    q1_backup_std = q1_stats["std"].median()
    q1_stats["std"] = q1_stats["std"].fillna(q1_backup_std)

    # Ensure all drivers are in the stats, even if they did not take part.
    q1_stats = q1_stats.reindex(all_drivers)
    
    # Drivers without competitive Q1 laps fill with placeholder values (infinite lap time).
    q1_stats["mean"] = q1_stats["mean"].fillna(np.inf)
    q1_stats["std"] = q1_stats["std"].fillna(0.5)
    q1_stats["count"] = q1_stats["count"].fillna(1).astype(int)


    # Q2 stats ---

    q2_laps = q2.pick_quicklaps().loc[lambda df: ~df["Deleted"]].copy()
    q2_laps["LapTimeSeconds"] = q2_laps["LapTime"].dt.total_seconds()

    q2_stats = q2_laps.groupby("Driver")["LapTimeSeconds"].agg(["mean", "std", "count"])
    q2_stats_raw = q2_stats.copy()

    # Calculate avg improvement from Q1 to Q2 from drivers who were in both
    common_drivers_q1_q2 = q1_stats_raw.index.intersection(q2_stats_raw.index)
    q1_common = q1_stats_raw.loc[common_drivers_q1_q2, 'mean']
    q2_common = q2_stats_raw.loc[common_drivers_q1_q2, 'mean']
    improvement = q1_common - q2_common
    q1_to_q2_avg_improvement = improvement.mean()

    # Ensure all drivers are in the stats, even if they did not take part.
    q2_stats = q2_stats.reindex(all_drivers)

    # Fill missing Q2 time with improved Q1 time.
    q2_stats['mean'] = q2_stats['mean'].fillna(q1_stats['mean'] - q1_to_q2_avg_improvement)

    q2_backup_std = q2_stats_raw["std"].median()
    q2_stats["std"] = q2_stats["std"].fillna(q2_backup_std)
    q2_stats["count"] = q2_stats["count"].fillna(int(q2_stats_raw["count"].mean()))


    # Q3 stats ---

    q3_laps = q3.pick_quicklaps().loc[lambda df: ~df["Deleted"]].copy()
    q3_laps["LapTimeSeconds"] = q3_laps["LapTime"].dt.total_seconds()

    q3_stats = q3_laps.groupby("Driver")["LapTimeSeconds"].agg(["mean", "std", "count"])
    q3_stats_raw = q3_stats.copy()

    # Calculate avg improvement from Q2 to Q3 from drivers who were in both
    common_drivers_q2_q3 = q2_stats_raw.index.intersection(q3_stats_raw.index)
    q2_common = q2_stats_raw.loc[common_drivers_q2_q3, 'mean']
    q3_common = q3_stats_raw.loc[common_drivers_q2_q3, 'mean']
    improvement = q2_common - q3_common
    q2_to_q3_avg_improvement = improvement.mean()

    # Ensure all drivers are in the stats, even if they did not take part.
    q3_stats = q3_stats.reindex(all_drivers)

    # Fill missing Q3 time with improved Q2 time.
    q3_stats['mean'] = q3_stats['mean'].fillna(q2_stats['mean'] - q2_to_q3_avg_improvement)

    q3_backup_std = q3_stats_raw["std"].median()
    q3_stats["std"] = q3_stats["std"].fillna(q3_backup_std)
    q3_stats["count"] = q3_stats["count"].fillna(int(q3_stats_raw["count"].mean()))    


    return q1_stats, q2_stats, q3_stats

def simulate_session(q_stats):
    '''
    Input: qualifying session stats.

    Uses average number of attempts for that session.

    Output: simulated results as ordered list of driver names.
    '''

    # Calculate average number of laps for that session
    n_attempts = int(q_stats['count'].mean())

    results = {}

    for driver in q_stats.index:
        mean = q_stats.loc[driver, 'mean']
        std = q_stats.loc[driver, 'std']

        lap_times = np.random.normal(mean, std, n_attempts)
        best_lap = lap_times.min()

        results[driver] = best_lap

    sorted_drivers = sorted(results, key=results.get)

    return sorted_drivers

def simulate_qualifying(session):
    '''
    Input: session.

    Simulates each stage of qualifying with eliminations.

    Output: full qualifying results as ordered list of driver names.
    '''

    q1, q2, q3 = create_driver_session_stats(session)

    # Q1 Sim --- 
    q1_result = simulate_session(q1)
    
    if session.date.year < 2026:
        q2_drivers = q1_result[:15]
        q1_drivers_eliminated = q1_result[15:]

    # 2026 elimates 6 drivers from each session.
    else:
        q2_drivers = q1_result[:16]
        q1_drivers_eliminated = q1_result[16:]
    
    # Q2 Sim ---
    q2_result = simulate_session(q2.loc[q2_drivers])

    q3_drivers = q2_result[:10]
    q2_drivers_eliminated = q2_result[10:]

    # Q3 Sim ---
    q3_result = simulate_session(q3.loc[q3_drivers])

    qualifying_result = q3_result + q2_drivers_eliminated + q1_drivers_eliminated

    return qualifying_result

def qualifying_MC(session, n=500):
    '''
    Input: session, n simulations.

    Output: count of each position per driver as dictionary.
    '''

    from collections import defaultdict

    # Automically create position with count 0 if not seen before, with fresh dictionary for each driver.
    position_counts = defaultdict(lambda: defaultdict(int))

    for i in range(n):
        result = simulate_qualifying(session)

        # Add count for that position for driver, adjust for 0 indexing.
        for position, driver in enumerate(result):
            position_counts[driver][position + 1] +=1

    return position_counts

def get_position_probability(position_counts, n=500):
    """
    Input: positions counts.

    Output: positions probabilities.
    """

    position_probabilities = {}

    for driver, positions in position_counts.items():
        position_probabilities[driver] = {
            position: count / n
            for position, count in positions.items()
        }

    return position_probabilities

def monte_carlo_qualifying(session, n=500):
    '''
    Input is GP name, year, and number of simulations n.
    Returns dataframe of drivers with probabilities for each position.
    '''
    
    position_counts = qualifying_MC(session, n)
    position_probabilities = get_position_probability(position_counts, n)

    df = pd.DataFrame.from_dict(position_probabilities, orient='index')

    df = df.fillna(0)
    df.index.name = 'Driver'
    df.columns.name = 'Position'
    df = df.reindex(sorted(df.columns), axis=1)

    return df

def simulate_grid(df):
    """
    Input: df is output from monte_carlo_qualifying().

    Uses Hungarian algorithm to maximise likelihood of full grid order by minimising cost.
    Zero probabilities are converted to 1e-6 to prevent log(0).

    Output: dataframe with driver abbreviation, as index, and grid position.
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




