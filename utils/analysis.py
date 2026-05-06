def real_results(session):
    """
    Input: session.

    Formats session results with abbreviation as index, and minimal columns.

    Output: real results dataframe.
    """

    return session.results.set_index('Abbreviation').rename(columns={'TeamName': 'Team', 'FullName':'Driver Name'}).rename_axis('Driver')[['Driver Name', 'Team', 'Position']]


def compare_grid(sim_grid, session):
    """
    Input: Simulated grid dataframe, and session.
    
    Calculates difference between simulated and true position.

    Output: Comparison dataframe.
    """

    # Join sim_grid and real session results on Abbreviation
    df = sim_grid.merge(real_results(session), left_index=True, right_index=True)

    df['Position change'] = df['Position'] - df['SimPosition']

    df = df.rename(columns={'SimPosition': 'Simulated position', 'Position': 'Real position'})

    # Reoder cols
    df = df[['Driver Name', 'Team', 'Simulated position', 'Real position', 'Position change']]

    return df


def get_probability_stats(df, year):
    """
    Input: df from monte_carlo_qualifying i.e. driver position probabilities matrix.
    
    Calculates expected (mean) position, standard deviation, and Q1, Q2 and Q3 probabilities.

    Output: input df with adjoined stats.
    """

    positions = df.columns.astype(int).values
    probs = df.values

    # @ shorthand for matrix mult.
    mean = probs @ positions
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
    """
    Input: stats df and comparison grid.

    Joins on index (which is abbreviation for both).
    Subsets stats to remove individual position probabilities.

    Output: Joined df.
    """

    # Update this with more stats to extract, must also be in get_probability_stats.
    stats_subset = stats[['mean', 'std', 'q3_prob', 'q2_prob', 'q1_prob', 'pole_prob', 'front_row_prob']]

    return comparison_grid.merge(stats_subset, left_index=True, right_index=True)

def merged_stats_to_dict(merged_stats):
    """
    Input: merged stats grid position df.

    Output: dictionary with abbr as key and dict of data as value.
    """
    return merged_stats.to_dict(orient='index')

    
