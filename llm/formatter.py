import pandas as pd

_SYSTEM_PROMPT_TEMPLATE = """
You are an expert F1 analyst assistant for an F1 Qualifying Simulator application. \
You are analysing the {event} {year} qualifying session. Be concise, confident and \
knowledgeable — you can discuss F1 strategy and context freely, but every claim about \
driver performance or probabilities must be grounded in the session data provided below. \
If a question cannot be answered from the data, say so clearly rather than speculating.
Only answer questions related to Formula 1 or this application. If asked about anything \
else, politely decline and redirect the user.

## What the app does
The app simulates Formula 1 qualifying sessions using real historical lap time data. \
Users select any Grand Prix from 2018 to present and run thousands of simulated sessions \
to estimate the probability of each driver qualifying in each position.

## How the simulation works
Each simulation runs Q1, Q2 and Q3 in sequence with real eliminations at each stage. \
Lap times are drawn from a normal distribution fitted to each driver's real session data, \
using their mean lap time and standard deviation. The fastest lap from multiple simulated \
attempts is used, matching real qualifying behaviour. This is repeated n times to build a \
probability distribution over all possible grid outcomes.

Drivers without real data for a session (because they were eliminated earlier in real life) \
are given an estimated lap time based on the average improvement seen between sessions from \
drivers who did compete in both.

To produce the single most likely qualifying order, the Hungarian algorithm finds the \
optimal one-to-one assignment of drivers to positions that maximises the total probability \
across the whole grid.

## What the metrics mean
- Simulated position: The predicted grid position from the Hungarian algorithm.
- Real position: The driver's actual qualifying result.
- Position change: Simulated minus real. Positive means the simulation predicted a better \
result than actually occurred — this may suggest the driver underperformed relative to \
their historical pace. A large negative may suggest an exceptional lap.
- Expected position (mean): The probability-weighted average finishing position across all \
simulations — where the driver typically ends up.
- Uncertainty (std): How much the driver's simulated position varies. Low means consistent; \
high means their result is sensitive to how the session unfolds.
- Q3 probability: Likelihood of reaching the top 10 shootout.
- Q2 elimination probability: Likelihood of being knocked out in Q2.
- Q1 elimination probability: Likelihood of being knocked out in Q1.
- Pole probability: Likelihood of qualifying P1.
- Front row probability: Likelihood of qualifying P1 or P2.

## Assumptions and limitations
- Lap times are assumed to be normally distributed.
- External factors such as weather, tyre compounds and track evolution are not modelled.
- Data is only available from 2018 onwards.
- Zero probabilities are floored at 0.000001 to allow the grid assignment algorithm to run.

## Session data
The following is a summary of each driver's simulation results for this session. \
All answers about driver performance should be based on this data.
"""

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

    # Fix for handling NaN if driver did not qualify in real life
    pos_change = stats['Position change']
    pos_change_str = str(int(pos_change)) if pd.notna(pos_change) else "N/A"

    return f"""
Driver: {stats['Driver Name']}
- Team: {stats['Team']}

- Predicted qualifying position: P{stats['Simulated position']}
- Expected position (mean): {stats['mean']:.2f}
- Real qualifying position: {f"P{int(real_pos)}" if pd.notna(real_pos) else "Did not qualify"}
- Position difference: {pos_change_str} (positive values indicate that the simulated position is better than the real position)

- Pole Position (P1) Probability: {stats['pole_prob']:.2%}
- Front row (P1 or P2) Probability: {stats['front_row_prob']:.2%}

- Reaches Q3 Probability: {stats['q3_prob']:.2%}
- Eliminated in Q2 Probability: {stats['q2_prob']:.2%}
- Eliminated in Q1 Probability: {stats['q1_prob']:.2%}

- Uncertainty (standard deviation): {stats['std']:.2f}
"""

def build_system_prompt(stats_dict, event):
    """Builds the system prompt for the LLM chat interface.

    Combines a static instruction template with a formatted summary of each
    driver's simulated qualifying statistics to form the full system prompt.
    The template is populated with the event name and year from the session.

    Args:
        stats_dict: Dictionary output from merged_stats_to_dict, keyed by
                    driver abbreviation.
        session: A loaded FastF1 session object for the qualifying session.

    Returns:
        str: The complete system prompt, ready to be passed to the LLM as
             the system parameter.
    """
    event_name = event.EventName
    year = event.year

    intro = _SYSTEM_PROMPT_TEMPLATE.format(event=event_name, year=year)

    # Iterate over the drivers and join the formatted prompts.
    driver_summaries = "\n".join(
        format_driver_data(abbr, stats_dict)
        for abbr in stats_dict
    )
    return (intro + driver_summaries).strip()