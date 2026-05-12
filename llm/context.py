from utils.analysis import compare_grid, get_probability_stats, merge_stats_comparison_grid

def build_llm_context(df, simulated_grid, results, year):
    """ Prepares a unified statistics dictionary for LLM consumption.

    Composes the analysis pipeline into a single driver-keyed dictionary
    by joining simulated results, real results, and probability statistics.

    Args:
        df: pd.DataFrame of position probabilities from monte_carlo_qualifying.
        simulated_grid: pd.DataFrame output from simulate_grid.
        session: FastF1 session object.
        year: Integer representing the championship year.

    Returns:
        dict: A dictionary with driver abbreviations as keys and a dictionary
              of their respective statistics as values.
    """
    comparison_grid = compare_grid(simulated_grid, results)
    stats = get_probability_stats(df, year)
    merged = merge_stats_comparison_grid(stats, comparison_grid)
    return merged.to_dict(orient='index')