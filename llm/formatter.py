def format_driver_data(abbr, stats_dict):
    stats = stats_dict[abbr]
    return f"""
Driver: {stats['Driver Name']}
- Team: {stats['Team']}

- Predicted qualifying position: {stats['Simulated position']}
- Expected position (mean): {stats['mean']}
- Real qualifying position: {stats['Real position']}
- Position difference: {stats['Position change']} (positive values indicate that the simulated position is better than the real position)

- Pole Position (P1) Probability: {stats['pole_prob']:.2%}
- Front row (P1 or P2) Probability: {stats['front_row_prob']:.2%}

- Reaches Q3 Probability: {stats['q3_prob']:.2%}
- Eliminated in Q2 Probability: {stats['q2_prob']:.2%}
- Eliminated in Q1 Probability: {stats['q1_prob']:.2%}

- Uncertainty (standard deviation): {stats['std']:.2f}
"""
