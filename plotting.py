import matplotlib.pyplot as plt
import seaborn as sns
import fastf1 as f1
from simulator import monte_carlo_qualifying


def f1_plot_theme():
    '''
    Sets style for matplotlib plots.
    '''
    plt.style.use("dark_background")
    plt.rcParams["figure.facecolor"] = "#1b1b1b"
    plt.rcParams["axes.facecolor"] = "#1b1b1b"
    plt.rcParams["grid.color"] = "#898989"
    plt.rcParams["axes.grid.axis"] = "y"
    plt.rcParams["text.color"] = "#898989"
    plt.rcParams["axes.labelcolor"] = "#d6d6d6"
    plt.rcParams["axes.titlecolor"] = "#f2f2f2"
    plt.rcParams["xtick.color"] = "#a4a4a4"
    plt.rcParams["ytick.color"] = "#a4a4a4"

def position_probability_plot(df, session, pos=1, n=500):
    '''
    Input: df of position probabilities, session, qualifying position (default is pole) and number of simulations.
    
    Output: probability distribution fig for given position.
    '''

    driver_colours = {
        driver: f"#{colour}"
        for driver, colour in session.results.set_index('Abbreviation')['TeamColor'].items()
    }

    data = df[pos].reset_index()
    data.columns = ["Driver", "Probability"]
    data = data.sort_values("Probability", ascending=False)
    data['Colour'] = data['Driver'].map(driver_colours)


    f1_plot_theme()

    fig, ax = plt.subplots(figsize=(12, 6))
    
    ax.bar(
        data['Driver'],
        data['Probability'],
        color=data['Colour']
    )

    sns.despine(ax=ax)

    ax.set_title(
        f"{session.event.EventName} {session.event.year} P{pos} Qualifying Probability Distribution - {n} simulations",
        fontsize=16,
        weight="bold",
        pad=15
    )
    ax.set_xlabel('Driver', fontsize=12, weight="bold", labelpad=15)
    ax.set_ylabel('Probability', fontsize=12, weight="bold", labelpad=15)
    ax.set_axisbelow(True)
    ax.grid(axis='y', color="#555555", alpha=0.3, linewidth=0.8)

    return fig

def expected_position(df, session, driver, abbr, n=500):
    '''
    Input: df of position probabilities, gp, year, driver abbreviation, number of simulations.

    Output: Driver qualifying position probability distribution fig.
    '''

    driver_colours = {
        abbr: f"#{colour}"
        for abbr, colour in session.results.set_index('Abbreviation')['TeamColor'].items()
    }


    row = df.loc[abbr]
    positions = sorted(row.index.astype(int))

    probabilities = row.values

    f1_plot_theme()

    fig, ax = plt.subplots(figsize=(12, 6))

    ax.bar(
        positions,
        probabilities,
        color = driver_colours[abbr]
    )

    sns.despine(ax=ax)

    ax.set_title(f"{session.event.EventName} {session.event.year} {driver} Qualifying Position Probability Distribution - {n} simulations", fontsize=16, weight="bold", pad=15)
    ax.set_xlabel('Position', fontsize=12, weight="bold", labelpad=15)
    ax.set_ylabel('Probability', fontsize=12, weight="bold", labelpad=15)
    ax.set_xticks(positions)
    ax.set_axisbelow(True)
    ax.grid(axis='y', color="#555555", alpha=0.3, linewidth=0.8)

    return fig