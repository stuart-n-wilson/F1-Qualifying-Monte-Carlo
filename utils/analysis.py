# Internal helper functions ---

def real_results(session):
    """ Helper function to extract and clean official session results.

    Formats the FastF1 session results to use the driver abbreviation as the 
    index and selects only essential identification and position columns.

    Args:
        session: FastF1 session object.

    Returns:
        pd.DataFrame: Cleaned results indexed by abbreviation (e.g., HAM).
                      Columns: 'Driver Name', 'Team', 'Position'.
    """
    return session.results.set_index('Abbreviation').rename(columns={'TeamName': 'Team', 'FullName':'Driver Name'}).rename_axis('Driver')[['Driver Name', 'Team', 'Position']]

# Public functions ---

def compare_grid(sim_grid, session):
    """ Calculates the delta between the simulated grid and true qualifying results.

    Joins the simulated grid DataFrame with real-world results on the driver 
    abbreviation index to determine position gains or losses.

    Args:
        sim_grid: pd.DataFrame output from simulate_grid.
        session: FastF1 session object.

    Returns:
        pd.DataFrame: Comparison table showing simulated vs. real positions 
                      and the calculated 'Position change'.
    """
    # Join sim_grid and real session results on Abbreviation
    df = sim_grid.merge(real_results(session), left_index=True, right_index=True)

    df['Position change'] = df['Position'] - df['SimPosition']

    df = df.rename(columns={'SimPosition': 'Simulated position', 'Position': 'Real position'})

    # Reoder cols
    df = df[['Driver Name', 'Team', 'Simulated position', 'Real position', 'Position change']]

    return df

def colour_grid_change(df):
    """ Internal UI helper to format and color-code position changes.

    Indicates position gains in green with an up arrow and losses in red 
    with a down arrow. Formats floats to integers for cleaner display.

    Args:
        df: pd.DataFrame containing a 'Position change' column.

    Returns:
        Styler: A formatted Pandas Styler object with conditional CSS coloring.
    """
    # Add arrows to indicate position change direction.
    df['Position change'] = df["Position change"].apply(lambda x: f"↑ {x:.0f}" if x > 0 else(f"↓ {abs(x):.0f}" if x < 0 else "0"))

    return df.style \
            .format({'Simulated position': '{:.0f}', 'Real position': '{:.0f}'}) \
            .map(
                lambda val: "color: green" if "↑" in val else ("color: red" if "↓" in val else ""),
                subset=["Position change"]
                )

def get_probability_stats(df, year):
    """ Calculates statistical metrics from the driver position probability matrix.

    Computes the expected position (mean), standard deviation, and probabilities 
    for reaching Q3 or being eliminated in Q1/Q2 based on the year's regulations.

    Args:
        df: pd.DataFrame of probabilities from monte_carlo_qualifying.
        year: Integer representing the championship year (for elimination rules).

    Returns:
        pd.DataFrame: The input probability matrix with adjoined statistical 
                      columns (mean, std, stage probabilities, etc.).
    """  
    positions = df.columns.astype(int).values
    probs = df.values

    # @ shorthand for matrix mult.
    mean = probs @ positions # E(X)
    mean_sq = probs @ (positions**2)

    # Var = E(X**2) - (E(X))**2 
    var = mean_sq - mean**2

    df_stats = df.copy()

    df_stats['mean'] = mean
    df_stats['std'] = var ** 0.5

    if year >= 2026:
        # 22 drivers: Q3=P1-10, Q2=P11-16, Q1=P17-22
        df_stats['q3_prob'] = df.loc[:, 1:10].sum(axis=1)
        df_stats['q2_prob'] = df.loc[:, 11:16].sum(axis=1)
        df_stats['q1_prob'] = df.loc[:, 17:].sum(axis=1)

    else:
        # 20 drivers: Q3=P1-10, Q2=P11-15, Q1=P16-20
        df_stats['q3_prob'] = df.loc[:, 1:10].sum(axis=1)
        df_stats['q2_prob'] = df.loc[:, 11:15].sum(axis=1)
        df_stats['q1_prob'] = df.loc[:, 16:].sum(axis=1)
    
    df_stats['pole_prob'] = df[1]
    df_stats['front_row_prob'] = df.loc[:, 1:2].sum(axis=1)

    return df_stats

def merge_stats_comparison_grid(stats, comparison_grid):
    """ Joins detailed probability statistics with the simulated grid comparison.

    Subsets the probability statistics to remove individual position columns 
    and merges the remaining metrics with the comparison grid.

    Args:
        stats: pd.DataFrame output from get_probability_stats.
        comparison_grid: pd.DataFrame output from compare_grid.

    Returns:
        pd.DataFrame: A unified DataFrame indexed by abbreviation containing 
                      identifying info, position comparison, and statistical metrics.
    """
    # Update this with more stats to extract, must also be in get_probability_stats.
    stats_subset = stats[['mean', 'std', 'q3_prob', 'q2_prob', 'q1_prob', 'pole_prob', 'front_row_prob']]

    return comparison_grid.merge(stats_subset, left_index=True, right_index=True)

