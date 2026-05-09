import pandas as pd

def format_driver_data(abbr, stats_dict):
    """ Formats a single driver's statistics into a structured prompt string for the LLM.

    Extracts the relevant statistics for a given driver from the context dictionary
    and renders them as a human-readable string containing position predictions,
    probabilities, and uncertainty metrics.

    Args:
        abbr: String containing the driver's three-letter abbreviation (e.g., 'HAM').
        stats_dict: Dictionary output from build_llm_context, keyed by abbreviation.

    Returns:
        str: A formatted multi-line string summarising the driver's simulated
             qualifying statistics, ready to be passed to the LLM.
    """
    stats = stats_dict[abbr]
    real_pos = stats['Real position']
    return f"""
Driver: {stats['Driver Name']}
- Team: {stats['Team']}

- Predicted qualifying position: {f"P{stats['Simulated position']}"}
- Expected position (mean): {stats['mean']:.2}
- Real qualifying position: {f"P{int(real_pos)}" if pd.notna(real_pos) else "Did not qualify"}
- Position difference: {int(stats['Position change'])} (positive values indicate that the simulated position is better than the real position)

- Pole Position (P1) Probability: {stats['pole_prob']:.2%}
- Front row (P1 or P2) Probability: {stats['front_row_prob']:.2%}

- Reaches Q3 Probability: {stats['q3_prob']:.2%}
- Eliminated in Q2 Probability: {stats['q2_prob']:.2%}
- Eliminated in Q1 Probability: {stats['q1_prob']:.2%}

- Uncertainty (standard deviation): {stats['std']:.2f}
"""
