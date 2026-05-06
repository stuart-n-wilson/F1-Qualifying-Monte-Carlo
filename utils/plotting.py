import plotly.graph_objects as go

def position_probability_plot(df, session, pos=1, n=500):
    '''
    Input: df of position probabilities, session, qualifying position (default is pole) and number of simulations.

    Output: probability distribution fig for given position.
    '''
    driver_names = session.results.set_index('Abbreviation')['FullName'].to_dict()
    
    driver_colours = {
        driver: f"#{colour}"
        for driver, colour in session.results.set_index('Abbreviation')['TeamColor'].items()
    }

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
        title_subtitle_text=f"{session.event.EventName} {session.event.year}",
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


def expected_position(df, session, driver, abbr, n=500):
    '''
    Input: df of position probabilities, session, driver name, driver abbreviation, n simulations.

    Output: Bar plot of driver's position probabilities.
    '''

    # Driver colours
    driver_colours = {
        abbr: f"#{colour}"
        for abbr, colour in session.results.set_index('Abbreviation')['TeamColor'].items()
    }

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
        title_subtitle_text=f"{session.event.EventName} {session.event.year}",
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

def colour_grid_change(df):
    """
    Input: 

    Indicates position gain in green with up arrow, and lost positions in red with down arrow.
    Display floats as int.

    Output: formatted/coloured df.
    """

    # Add arrows to indicate position change direction.
    df['Position change'] = df["Position change"].apply(lambda x: f"↑ {x:.0f}" if x > 0 else(f"↓ {abs(x):.0f}" if x < 0 else "0"))

    df_coloured = df.style \
        .format({'Simulated position': '{:.0f}', 'Real position': '{:.0f}'}) \
        .map(
            lambda val: "color: green" if "↑" in val else ("color: red" if "↓" in val else ""),
            subset=["Position change"]
            )
    
    return df_coloured
    