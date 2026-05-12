import plotly.graph_objects as go
import pandas as pd

def _get_driver_colours(results):
    """ Helper function to create a mapping of driver abbreviations to team colours.

    Extracts team colours from the FastF1 session results and ensures they are 
    formatted as hex strings for Plotly marker compatibility.

    Args:
        session: FastF1 session object.

    Returns:
        dict: A dictionary where keys are driver abbreviations (e.g., 'HAM') 
              and values are hex color strings (e.g., '#00d2be').
    """
    return {
        abbr: f"#{colour}" if pd.notna(colour) else "#888888"
        for abbr, colour in results.set_index('Abbreviation')['TeamColor'].items()
    }

def position_probability_plot(df, results, event, n, pos=1):
    """ Creates a bar chart showing driver probabilities for a specific grid position.

    Visualises which drivers are most likely to qualify in the selected position (e.g. P1).
    Sorted from highest to lowest probability.

    Args:
        df: pd.DataFrame of position probabilities from the Monte Carlo simulation.
        session: FastF1 session object.
        n: Integer representing the number of simulations performed.
        pos: Integer representing the qualifying position to plot (default is 1).
        
    Returns:
        go.Figure: A Plotly bar figure showing probability distribution for the given position.
    """
    driver_names = results.set_index('Abbreviation')['FullName'].to_dict()
    driver_colours = _get_driver_colours(results)
    
    data = df[pos].reset_index()
    data.columns = ["Driver", "Probability"]
    data = data.sort_values("Probability", ascending=False)
    data['Colour'] = data['Driver'].map(driver_colours)
    data['FullName'] = data['Driver'].map(driver_names)

    fig = go.Figure()

    fig.add_bar(
        x=data["Driver"],
        y=data["Probability"] * 100,
        marker_color=data["Colour"],
        customdata=data["FullName"],
        hovertemplate="Driver: %{customdata}<br>Probability: %{y:.1f}%<extra></extra>",
    )

    fig.update_layout(
        title={
            "text": f"P{pos} Qualifying Probability Distribution - {n} simulations",
            "x": 0.5,
            "xanchor": "center"
        },
        title_font=dict(size=20),
        title_subtitle_text=f"{event.EventName} {event.year}",
        title_subtitle_font=dict(size=14),
        xaxis_title="Driver",
        yaxis_title="Probability (%)",
        margin=dict(t=90)
    )

    fig.update_yaxes(
        showgrid=True,
        gridwidth=1,
        zeroline=False,
    )

    fig.update_xaxes(showgrid=False)

    return fig

def expected_position(df, results, event, driver, abbr, n):
    """ Creates a bar chart of a specific driver's probability across all positions.

    Provides a visual position probability distribution for each driver.

    Args:
        df: pd.DataFrame of position probabilities from the Monte Carlo simulation.
        session: FastF1 session object.
        driver: String containing the full name of the driver.
        abbr: String containing the driver's three-letter abbreviation.
        n: Integer representing the number of simulations performed.

    Returns:
        go.Figure: A Plotly bar figure showing the driver's probability per position.
    """
    driver_colours = _get_driver_colours(results)

    # Data
    row = df.loc[abbr]
    positions = sorted(row.index.astype(int))
    probabilities = row.values

    # Create figure
    fig = go.Figure()

    fig.add_bar(
        x=positions,
        y=(probabilities * 100),
        marker_color=driver_colours[abbr],
        hovertemplate="Position: %{x}<br>Probability (%): %{y:.1f}%<extra></extra>"
    )

    # Titles and such
    fig.update_layout(
        title={
            "text": f"{driver} Qualifying - {n} simulations",
            "x": 0.5,
            "xanchor": "center"
        },
        title_font=dict(size=20),
        title_subtitle_text=f"{event.EventName} {event.year}",
        title_subtitle_font=dict(size=14),
        xaxis_title="Position",
        yaxis_title="Probability (%)",
        margin=dict(t=90)
    )

    fig.update_xaxes(
        tickmode="array",
        tickvals=positions,
        showgrid=False,
    )

    return fig

def position_change_bump(comparison_grid, results, event, n):
    """
    Input: comparison_grid from compare_grid(), session, n simulations.

    Creates a bump chart mapping each driver's real qualifying position
    to their simulated position, coloured by team.

    Output: Bump chart fig.
    """
    df = comparison_grid.copy()
    driver_colours = _get_driver_colours(results)

    fig = go.Figure()

    for abbr, row in df.iterrows():
        real_pos = row['Real position']
        sim_pos  = int(row['Simulated position'])
        colour   = driver_colours.get(abbr, '#888888')

        y_real = real_pos if pd.notna(real_pos) else len(df) + 1

        fig.add_scatter(
            x=[0, 1],
            y=[y_real, sim_pos],
            mode='lines+markers',
            line=dict(color=colour, width=2),
            marker=dict(color=colour, size=8),
            name=row['Driver Name'],
            hovertemplate=f"<b>{row['Driver Name']}</b><br>Real: {'P' + str(int(y_real)) if pd.notna(real_pos) else 'DNS'}<br>Simulated: P{sim_pos}<extra></extra>",
            yaxis="y1"
        )

    # Position labels on the right
    fig.add_scatter(
        x=[1.05] * len(df),
        y=list(range(1, len(df) + 1)),
        mode='text',
        text=[f"P{i}" for i in range(1, len(df) + 1)],
        textposition='middle right',
        textfont=dict(size=11),
        hoverinfo='skip',
        showlegend=False
    )

    fig.update_layout(
        title={
            "text": f"Real vs Simulated Grid — {n} simulations",
            "x": 0.5,
            "xanchor": "center"
        },
        title_font=dict(size=20),
        title_subtitle_text=f"{event.EventName} {event.year}",
        title_subtitle_font=dict(size=14),
        xaxis=dict(
            tickvals=[0, 1],
            ticktext=["Real", "Simulated"],
            showgrid=False,
            range=[-0.05, 1.2],
            showline = False,
            mirror = False
        ),
        yaxis=dict(
            autorange="reversed",
            tickvals=list(range(1, len(df) + 1)),
            ticktext=[f"P{i}" for i in range(1, len(df) + 1)],
            showgrid=False,
            gridwidth=1,
            mirror = False,
            showline = False,
            zeroline = False
        ),
        showlegend=False,
        margin=dict(t=90, l=60, r=80)
    )

    return fig